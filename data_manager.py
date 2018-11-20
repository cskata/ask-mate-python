import operator
import pandas


def convert_unix_timestamp_to_date(database):
    for data in database:
        data["submission_time"] = pandas.to_datetime(data["submission_time"], unit='s')
    return database


def convert_date_to_unix_timestamp(database):
    for data in database:
        data["submission_time"] = pandas.to_datetime(data["submission_time"]).value // 10**6
    return database


def sort_data(data, key, order):
    if order == "asc":
        result = data.sort(key=operator.itemgetter(key))
    else:
        result = data.sort(key=operator.itemgetter(key), reverse=True)
    return result
