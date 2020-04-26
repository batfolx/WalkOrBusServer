import pymysql
import datetime
# config file containing credentials for MySQL database
from config import *

rds_host = db_instance
name = db_username
password = db_password
db_name = db_name

"""
Utility file for interacting with the 
database
"""

def _connect():
    """
    Establishes a connection to the database
    :return: Connection object
    """
    conn = pymysql.connect (
        host=rds_host,
        user=name,
        password=password,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=20
    )

    return conn


def add_column(column_name: str, table_name, datatype):
    conn = _connect()

    with conn.cursor() as cur:

        try:
            sql = f"ALTER TABLE {table_name} ADD {column_name} {datatype} NOT NULL"
            cur.execute(sql)
            conn.commit()
        finally:
            conn.close()


def delete_column(table_name: str, column_name: str ):
    conn = _connect()

    with conn.cursor() as cur:

        try:
            sql = 'USE `%s`; ALTER TABLE `%s` DROP COLUMN `%s`'
            cur.execute(sql, ('website_data',table_name, column_name))
            conn.commit()
        finally:
            conn.close()


def alter_column(table_name: str, column_name:str, limit: int):
    conn = _connect()

    with conn.cursor() as cur:

        try:
            sql = f'ALTER TABLE {table_name} CHANGE {column_name} {column_name} varchar({limit}) NOT NULL'
            cur.execute(sql)
            conn.commit()
        finally:
            conn.close()


def describe_user_data(table_name: str):
    conn = _connect()

    with conn.cursor() as cur:

        try:
            sql = f"DESCRIBE website_data.{table_name}"
            cur.execute(sql)
            result = cur.fetchall()
            conn.commit()
        finally:
            conn.close()
    return result


def delete_entries_from_table(table_name):
    conn = _connect()

    with conn.cursor() as cur:

        try:
            sql = f"DELETE FROM {table_name}"
            cur.execute(sql)
            result = cur.fetchall()
            conn.commit()
        finally:
            conn.close()





def add_data_to_db(day, food_court_avg, time, target, location, location_dest, timestamp: str = str(datetime.datetime.now()), accuracy = 0):
    """
    Adds data to the database.
    :param day: The day, (0,1,2,3,4)
    :param food_court_avg: the average amount of people at any given time at the food court
    :param time: The current time
    :param target: the target , aka walk or bus
    :return: None
    """
    conn = _connect()
    with conn.cursor() as cur:

        sql = "INSERT INTO website_data.user_data(day, food_court_avg, time, target, location, location_dest, timestamp, accuracy)" \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"

        cur.execute(sql, (day, food_court_avg, time, target, location, location_dest, timestamp, accuracy))
    conn.commit()
    conn.close()


def get_everything_from_db() -> list:
    """
    Gets all the data from the table for machine learning purposes
    :return: list -> list of dictionaries of all of the items
    """
    conn = _connect()
    try:
        with conn.cursor() as cur:
            sql = "SELECT * from website_data.user_data"
            cur.execute(sql)
            result = cur.fetchall()
        conn.commit()
    finally:
        conn.close()

    return result


def get_boris_accuracy_from_db():
    conn = _connect()

    try:
        with conn.cursor() as cur:
            sql = "SELECT * FROM website_data.boris_accuracy"
            cur.execute(sql)
            result = cur.fetchall()
            conn.commit()
    finally:
        conn.close()

    return result


# 0 is correct, 1 is incorrect
def add_boris_accuracy(decision: int, now: str):
    conn = _connect()
    try:
        with conn.cursor() as cur:
            sql = "INSERT INTO website_data.boris_accuracy(decision, `timestamp`)" \
                  "VALUES(%s, %s);"

            cur.execute(sql, (decision, now))
            conn.commit()
    finally:
        conn.close()


def set_right_answer(new_target: int, timestamp: str):
    conn = _connect()

    try:
        with conn.cursor() as cur:

            sql = "UPDATE website_data.user_data SET target=%s WHERE `timestamp`=%s;"
            cur.execute(sql, (new_target, timestamp))
            conn.commit()

    finally:
        conn.close()


def get_boris_accuracy():
    conn = _connect()
    try:
        with conn.cursor() as cur:
            sql = "SELECT * FROM website_data.boris_accuracy"

            cur.execute(sql)
            result = cur.fetchall()
            conn.commit()
    finally:
        conn.close()

    return result



#delete_entries_from_table('website_data.user_data')
#delete_entries_from_table('website_data.boris_accuracy')

# there are used as first time setup
"""
CREATE TABLE user_data (
    day int,
    food_court_avg int,
    time float,
    location int,
    location_dest int,
    timestamp varchar(35),
    accuracy int
);

CREATE TABLE boris_accuracy(

	decision int,
	target int,
	timestamp varchar(35)

);

"""

#add_data_to_db(2, 0, 8.3, 1, 0, 1)
