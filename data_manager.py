import operator
import pandas


def convert_unix_timestamp(data):
    for line in data:
        line["submission_time"] = pandas.to_datetime(line["submission_time"], unit='s')
    return data
