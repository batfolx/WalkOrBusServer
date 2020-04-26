import socket

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
    sock.settimeout(100000)
    try:
        while True:
            conn, addr = sock.accept()
            print(f'connection: {conn}, addr: {addr}')
            with open('milk_beverages.jpg', 'rb') as f:
                data = f.read()
                print(f"this is data: {data}, length of data: {len(data)}")

                conn.send(data)
                conn.close()


            #Thread(target=handle_connection, args=(conn, addr,)).start() #TODO make this multithreaded
    except KeyboardInterrupt:
        pass

    # close and detach socket for cleanup
    sock.close()
    sock.detach()

start_server()