import random
import datetime
import csv
import pprint
from database import get_everything_from_db, get_boris_accuracy_from_db


# TD needs to be date, avg number of kids in food court, time(in between classes or not)
# 1 is bus, 0 is walk


@DeprecationWarning
def get_dates(num_days: int):
    """
    Gets a list of date objects. Deprecated.
    :param num_days: The amount of days you want from today - num days
    :return:
    """
    now = datetime.datetime.now()
    year_bef = datetime.date(now.year, now.month, now.day)
    dates = []
    for i in range(num_days):
        dates.append((year_bef - datetime.timedelta(num_days - i)))

    return dates


@DeprecationWarning
def get_time_comps(timestr: str):
    """
    Gets the time components. Deprecated. use convert_time instead
    :param timestr: The time string
    :return:
    """

    time_arr = timestr.split(":")
    hour = time_arr[0]
    minute = time_arr[1]

    return int(hour), int(minute)


def convert_time(timestr: str) -> float:
    """
    Converts the time to a float. useful for storing data
    :param timestr: The time string to be manipulated
    :return: float -> float representation of the time
    """
    time_arr = timestr.split(':')
    return float(f'{time_arr[0]}.{time_arr[1]}')


def get_datetime_object(hour, min):
    now = datetime.datetime.now()
    return datetime.datetime(now.year, now.month, now.day, hour, min)


def generate_training_data(class_times: list, num_days: int) -> tuple:
    training_data = []
    targets = []
    dates = get_dates(num_days)
    now = datetime.datetime.now()
    for date in dates:
        k = 0
        for i in range(0, len(class_times) - 1):
            more_td = []
            more_td.append(k)  # this is the date
            more_td.append(random.randint(0, 1000))  # this is the avg number of kids in food course
            more_td.append(convert_time(class_times[i]))  # this is the time
            training_data.append(more_td)

            hour_f, min_f = get_time_comps(class_times[i])
            hour_s, min_s = get_time_comps(class_times[i + 1])
            first_d = get_datetime_object(hour_f, min_f)
            second_d = get_datetime_object(hour_s, min_s)
            if second_d - first_d == datetime.timedelta(minutes=15):

                if 9 <= second_d.hour < 12:
                    targets.append(0)
                elif 12 <= second_d.hour < 13:
                    targets.append(1)
                elif 13 <= second_d.hour < 15:
                    targets.append(0)
                else:
                    targets.append(1)

            else:
                targets.append(1)
        k += 1

    return training_data, targets


def write_data_to_file(training_data: list, targets: list, mode: str, file_name: str = "training_data.csv"):
    with open(file_name, mode) as data_file:
        for i in range(len(training_data)):

            for j in range(len(training_data[i])):
                data_file.write(f'{training_data[i][j]},')

            data_file.write(f'{targets[i]}\n')


def read_in_training_data(file_name: str):
    training_data = []
    targets = []
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        the_list = list(reader)
        for entry in the_list:
            training_data.append(entry[0:3])
            targets.append(entry[3])

    return training_data, targets


def current_time_to_training_data() -> float:
    minute = datetime.datetime.now().minute
    hour = str(datetime.datetime.now().hour)
    return float(f"{hour}.{minute}")


def get_training_data_from_db() -> tuple:
    """
    Gets all of the data from the database, loops through it and produces training data necessary for classifer
    :return: tuple -> training data and the targets to train the classifier
    """
    training_data = []
    targets = []
    results = get_everything_from_db()

    for result in results:
        tmp_data = [result['day'], result['food_court_avg'], result['time'], result['location'],
                    result['location_dest']]
        targets.append(result['target'])
        training_data.append(tmp_data)

    return training_data, targets


# 0 for correct, 1 for wrong
def get_boris_accuracy_stats() -> dict:
    """
    Gets boris' accuracy statistics
    :return: dict -> containing boris statistics
    """
    results = get_boris_accuracy_from_db()
    total = len(results)
    if total == 0:
        return {
            'Correct': 0,
            'Wrong': 0,
            'Neutral': 0,
            'PercentCorrect': 0,
            'PercentWrong': 0,
            'CorrectToWrong': 0
        }
    correct = 0
    wrong = 0
    neutral = 0
    for result in results:
        if result['decision'] == 0:
            correct += 1
        elif result['decision'] == 1:
            wrong += 1
        else:
            neutral += 1
    return {
        'Correct': correct,
        'Wrong': wrong,
        'Neutral': neutral,
        'PercentCorrect': correct / total,
        'PercentWrong': wrong / total,
    }


def get_location(location: str, location_dest: str) -> tuple:
    locations_src = ['festival', 'phys/chem', 'biotech', 'ecl', 'urec', 'lakeside', 'dhall', 'carrier', 'forbes',
                     'quad']
    location_src_a = 0
    location_dest_a = 0
    for loc in locations_src:
        if location == loc:
            break
        location_src_a += 1

    for loc in locations_src:
        loc = f"{loc}_d"
        if location_dest == loc:
            break
        location_dest_a += 1

    return location_src_a, location_dest_a


def get_location_name(location_number: int) -> str:
    if location_number == 0:
        location = 'Festival'
    elif location_number == 1:
        location = "Phys/Chem"
    elif location_number == 2:
        location = 'BioTech'
    elif location_number == 3:
        location = 'ECL/Rose'
    elif location_number == 4:
        location = 'UREC'
    elif location_number == 5:
        location = 'Lakeside'
    elif location_number == 6:
        location = 'DHall'
    elif location_number == 7:
        location = 'Carrier'
    elif location_number == 8:
        location = 'Forbes'
    else:
        location = 'the Quad'

    return location
