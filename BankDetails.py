import os
import csv
import json
import logging
import formator
from operator import attrgetter
from collections import namedtuple


CONFIG_FILE = "config.json"


class BankTransactions:
    """
    Object to store all the Bank Details, which can be easily accessed and modified in future.
    """
    def __init__(self, heads):
        """
        Initializes the named tuple object and a list to store all its object
        :param heads:
        """
        self.details_tuple = namedtuple("BankDetails", heads)
        self.transactions = list()

    def update_bank_transactions(self, details):
        """
        creates a named tuple and appends it inside transactions list.
        :param details:
        :return: True if no error occured
        """
        try:
            self.transactions.append(self.details_tuple(**details))
            return True

        except TypeError as e:
            logging.error("Missing one parameter while creating a Named Tuple")
            logging.error("{}: {}".format(type(e), e))
            return False


def get_config(conf_file):
    """
    Reads the config file of CONFIG_FILE.
    Validates the common date time format specified in config file to evaluate the date format.
    :return: config file (dict)
    """
    try:
        with open(os.path.abspath(conf_file), "r") as f:
            config_file = json.load(f)
            logging.info("Opened config file, {}".format(config_file))
        logging.debug("Read config file and returning it.", config_file)
        return config_file

    except FileNotFoundError as e:
        logging.error("File Not Found: {}".format(e.filename))
        logging.debug("{}: {}".format(type(e), e))


def files_from_folder(path, exception_files=()):
    """
    Reads all the files from folder path provided
    :param path:
    :param exception_files:
    :return: absolute path of all file within a folder (list)
    """
    path = os.path.abspath(path)
    logging.debug("Path of the folder {}".format(path))
    logging.debug("Exception files are {}". format(exception_files))
    all_files = list()
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)) and file not in exception_files:
            all_files.append(os.path.join(path, file))
    logging.debug("Files: {}".format(all_files))
    return all_files


def get_specific_conf(fields, titles):
    """
    From config file extracts, gets to simple config file required for each file.
    :param fields:
    :param titles:
    :return: specific config file (dict)
    """
    spec_conf = dict()
    try:
        for key, values in fields.items():
            spec_conf[key] = dict()
            value = values["Title"]
            for v in value:
                if "." not in v and v in titles:
                    spec_conf[key]["value"] = v
                    spec_conf[key]["format"] = formator.convertor[values["Format"]]
                    break
                elif "." in v:
                    vals = v.split(".")
                    if all([val in titles for val in vals]):
                        spec_conf[key]["value"] = vals
                        spec_conf[key]["format"] = formator.convertor[values["Format"]]
                        break
            else:
                logging.error("not found a format in a file specified in the config file")
                return None
    except KeyError as e:
        logging.error("{}: {}".format(type(e), e))
    return spec_conf


def read_file(config, path):
    """
    reads file and update inside output file
    :param config:
    :param path:
    :return:
    """
    logging.info("Reading file {}".format(path))
    try:
        with open(path, "r") as f:
            file = csv.DictReader(f)
            yield file.fieldnames

            for row in file:
                yield row

    except FileNotFoundError as e:
        logging.error("File {} Not Found".format(path))
        logging.debug("{}: {}".format(type(e), e))
    except TypeError as e:
        logging.error("Not found a field from config file Fields in file {}".format(path))
        logging.debug("{}: {}".format(type(e), e))


def write_transactions_csv(trans_obj, out_file):
    """
    writes the Bank Details object into csv file.
    :param trans_obj:
    :param out_file:
    :return: True if no errors False if errors (bool)
    """
    file = os.path.abspath(out_file)
    try:
        with open(file, "w", newline='') as f:
            writer = csv.writer(f)
            if trans_obj:
                writer.writerow(trans_obj[0]._fields)
                for row in sorted(trans_obj, key=attrgetter("TransactionTime")):
                    writer.writerow(list(row))

            else:
                logging.error("Bank details is empty")
                return False

        return True

    except FileNotFoundError as e:
        logging.error("output file not found, {}".format(e.filename))
        logging.debug("{}: {}".format(type(e), e))
        return False


def fetch_bank_details(config):
    """
    Gets details from csv file and combine with one file.
    :param config:
    :return: None
    """
    logging.info("Fetching Bank Details.")
    folder_path = os.path.abspath(config["Configurations"]["InputFolderPath"])
    exceptions_files = config["Configurations"]["ExceptionFiles"]
    logging.debug("folder_path: {}".format(folder_path))
    all_csv_files = files_from_folder(folder_path, exceptions_files)
    output_headings = config["Fields"].keys()
    logging.debug("Headings of the output file: {}".format(output_headings))
    try:
        bank_details = BankTransactions(output_headings)
        if all_csv_files:
            for file_path in all_csv_files:
                read_file_and_heads = read_file(config, file_path)
                titles = next(read_file_and_heads)
                spec_config = get_specific_conf(config["Fields"], titles)
                if not spec_config:
                    logging.error("file {}, Titles are not updated in config file.".format(file_path))
                    raise TypeError

                for row in read_file_and_heads:
                    bank = dict()
                    for key, conf in spec_config.items():
                        if isinstance(conf["value"], str):
                            bank[key] = conf["format"](row[conf["value"]])
                        elif isinstance(conf["value"], list):
                            bank[key] = conf["format"](".".join([row[val] for val in conf["value"]]))

                    if not bank_details.update_bank_transactions(bank):
                        logging.error("cannot update to the bank details object.")
        return bank_details

    except TypeError as e:
        logging.error("Error occured while reading file and getting its config")
        logging.debug("{}: {}".format(type(e), e))


def main():
    """
    Main function, Execute at the start of the code.
    :return:  None
    """
    config = get_config(CONFIG_FILE)
    if config:
        bank_transactions = fetch_bank_details(config)
        if write_transactions_csv(bank_transactions.transactions, config["Configurations"]["OutputFilePath"]):
            logging.info("Updated Output file {} with bank details present in folder {}".format(
                config["Configurations"]["OutputFilePath"], config["Configurations"]["InputFolderPath"]))
        else:
            logging.error("Error while writting into Output file {}".format(config["Configurations"]["OutputFilePath"]))


if __name__ == "__main__":
    logging.basicConfig(filename='bank_details_logs.log', level=logging.DEBUG)
    logging.info("Start of the Code Main Function")
    main()
