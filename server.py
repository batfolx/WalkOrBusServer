import socket
from datetime import datetime
from threading import Thread
import database
import training_data_handler as atd
from classifer import classifier


def start_server():
    """
    Starts the server and listens for connections from the app
    :return: None
    """
    # create socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "192.168.1.6"
    port = 10000

    # bind socket to port
    sock.bind((host, port))

    # listen for up to 10 connections
    sock.listen(10)

    # set socket timeout

    sock.settimeout(10000)
    first_time_setup()
    try:
        while True:
            conn, addr = sock.accept()
            print(f'connection: {conn}, addr: {addr}')
            t = Thread(target=handle_connection, args=(conn, addr,), daemon=True) #TODO make this multithreaded
            t.start()
    except KeyboardInterrupt:
        pass

    # close and detach socket for cleanup
    sock.close()
    sock.detach()


def first_time_setup():
    """
    if there is nothing in DB, we add this dummy data so entire project doesn't crash
    as well as create the database & tables necessary for the server to run
    :return: None
    """

    database.create_tables_and_db()
    training_data, targets = atd.get_training_data_from_db()
    if len(training_data) == 0:
        database.add_data_to_db(0, 0, 0, 0, 0, 0)


def send_boris_answer(c, components):
    """
    Sends the answer that Boris chooses
    :param c: the connection
    :param components: the components of the bytes that were sent through socket
    :return: None
    """
    # convert all of the elements in the list to a float
    raw_data = [float(i) for i in components]

    # get the data from the database to fit the classifier
    training_data, targets = atd.get_training_data_from_db()

    # fit the data
    classifier.fit(training_data, targets)

    # predict whether or not to walk or bus (0 is walk, 1 is bus)
    answer = classifier.predict([raw_data])

    # get all the stats from the database
    stats = atd.get_boris_accuracy_stats()
    print(f'Boris answer: {answer}')
    data_points = len(training_data)
    boris_answer = answer[0]
    percent = stats['PercentCorrect'] * 100

    # send a nicely formatted string to decode to use in the app
    c.send(bytes(f"{boris_answer},{percent:.2f},{data_points}", 'utf-8'))


def handle_yes_db(c, components):
    """
    If Boris guessed correctly we will update the database with the correct
    :param c: The connection object
    :param components: the components from data packet from app
    :return: None
    """
    print(f"Incoming components in handle_yes_db {components}")
    date = components[0]
    time = components[2]
    src = components[3]
    destination = components[4]
    target = components[5]
    now = str(datetime.now())
    # 0 means he got it correct, 1 means he got it wrong
    database.add_boris_accuracy(0, now)
    stats = atd.get_boris_accuracy_stats()

    # add to the database with the correct target(answer) given to the user by Boris
    database.add_data_to_db(date, 0, time, target, src, destination,
                            timestamp=now, accuracy=f"{stats['PercentCorrect'] * 100:.2f}")
    c.send(bytes("Successfully added to DB!", encoding="utf-8"))


def handle_no_db(c, components):
    """
    Handles Boris being incorrect in his answer
    :param c: The connection object
    :param components: The components from the data sent from app
    :return: None
    """
    date = components[0]
    time = components[2]
    src = components[3]
    destination = components[4]
    target = components[5]
    now = str(datetime.now())
    database.add_boris_accuracy(1, now)
    stats = atd.get_boris_accuracy_stats()
    if target.strip() == '0':
        database.add_data_to_db(date, 0, time, 1, src, destination,
                                timestamp=now, accuracy=f"{stats['PercentCorrect'] * 100:.2f}")
    else:
        database.add_data_to_db(date, 0, time, 0, src, destination,
                                timestamp=now, accuracy=f"{stats['PercentCorrect'] * 100:.2f}")

    c.send(bytes("Successfully added to DB!", encoding="utf-8"))


def handle_nomatter_db(c):
    """
    Handles if Boris' decision didn't matter (walk/bus got there on same time)
    :param c: The connection object
    :return: None
    """
    now = str(datetime.now())
    database.add_boris_accuracy(1, now)
    c.send(bytes("Successfully added to DB!", encoding="utf-8"))


def handle_connection(c, address):
    """
    Function that handles an incoming connection and sends
    Boris' answer back to them (machine learning algorithm)
    :param c: a socket connection
    :param address: the address
    :return: None
    """
    msg = c.recv(1024)
    if not msg:
        c.close()
        return
    data = msg.decode("utf-8")
    data = data.strip()

    # if the app sends main: through socket
    # we know we just want Boris' answer
    if "main" in data:
        components = data.split(':')[1].split(',')
        send_boris_answer(c, components)

    # if app has this in its packet
    # then we know we need to update the database
    # in some way
    elif "add_db" in data:
        # raw data looks like this
        # weekday, 0, time, src, destination, target (target is answer that boris gave, i.e walk or bus)
        components = data.split(":")[1].split(',')
        print(f'components in add_db if: {components}')

        # boris got answer right
        if "yesadd_db" in data:
            print("yes add db")
            handle_yes_db(c, components)
        # boris got answer wrong
        elif "noadd_db" in data:
            print("no add db")
            handle_no_db(c, components)
        # boris' answer had no impact
        elif "nomatteradd_db" in data:
            print('dont matter')
            handle_nomatter_db(c)

    c.close()


# start the server
start_server()
