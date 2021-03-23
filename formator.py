import logging
import dateutil.parser


def integer(value):
    try:
        return int(value)

    except ValueError as e:
        logging.error("value is not an integer value")
        logging.debug("{}: {}".format(type(e), e))
        return value


def string(value):
    try:
        return str(value)

    except ValueError as e:
        logging.error("value is not an string value")
        logging.debug("{}: {}".format(type(e), e))
        return value


def float_2decimal(value):
    try:
        return round(float(value), 2) # python 3 rounding works is a bankers rounding, version 3 would be better here.

    except ValueError as e:
        logging.error("value is not an string value")
        logging.debug("{}: {}".format(type(e), e))
        return value


def date_time(value):
    try:
        return dateutil.parser.parse(value).date()

    except dateutil.parser._parser.ParserError as e:
        logging.error("{}: {}".format(type(e), e))


convertor = {
    "datetime": date_time,
    "string": string,
    "float": float_2decimal,
    "integer": integer
}