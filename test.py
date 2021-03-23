import unittest
import csv
import os
import BankDetails
from datetime import date


class BankDetailsTest(unittest.TestCase):

    def test_getting_files_with_exception(self):
        """
        Read the files present in the folder with excluding the exception files.
        :return:
        """
        conf = BankDetails.get_config("tests/config.json")
        files = BankDetails.files_from_folder(conf["Configurations"]["InputFolderPath"],
                                              conf["Configurations"]["ExceptionFiles"])
        self.assertEqual(files, [os.path.abspath("csv_files/bank1.csv"), os.path.abspath("csv_files/bank3.csv")])

    def test_negetive_config_file(self):
        """
        gets None while reading a wrong config file
        :return:
        """
        conf = BankDetails.get_config("tests/config_not.json")
        self.assertIsNone(conf)
        print("An error line is printed from the main code, since this is an Negetive test case.")

    def test_specific_configuration(self):
        """
        checks whether we are getting the right configuration for a csv file.
        :return:
        """
        fields = {
            "field1": {
                "Title": ["title1", "title2", "title3"],
                "Format": "datetime"
            },
            "field2": {
                "Title": ["title4"],
                "Format": "integer"
            },
            "field3": {
                "Title": ["title5", "title6"],
                "Format": "float"
            }
        }
        titles = ["title2", "title6", "title4"]
        spec_conf = BankDetails.get_specific_conf(fields, titles)

        self.assertEqual([value["value"] for key, value in spec_conf.items()].sort(), titles.sort())
        self.assertTrue([callable(value["format"]) for key, value in spec_conf.items()])

    def test_check_bank_data_format(self):
        """
        Calls main function of Reading files and gets object of list of named tuple for all details from csv files.
        checks the datatype of the values updated in the object.
        :return:
        """
        config = BankDetails.get_config("tests/config.json")
        bank_obj = BankDetails.fetch_bank_details(config)
        self.assertIsNotNone(bank_obj)
        for obj in bank_obj.transactions:
            self.assertTrue(isinstance(obj.TransactionTime, date))
            self.assertTrue(isinstance(obj.TransactionType, str))
            self.assertTrue(isinstance(obj.TransactionAmount, float))
            self.assertTrue(isinstance(obj.DebitedFrom, int))
            self.assertTrue(isinstance(obj.CreditedTo, int))

    def test_bank_data(self):
        """
        Calls main function of Reading files and gets object of list of named tuple for all details from csv files.
        checks the values in the bank data object.
        :return:
        """
        config = BankDetails.get_config("tests/config.json")
        bank_obj = BankDetails.fetch_bank_details(config)
        self.assertIsNotNone(bank_obj)
        expected_output = [
            ['2019-10-01', 'remove', '99.2', '198', '182'],
            ['2019-10-02', 'add', '2000.1', '188', '198'],
            ['2019-10-05', 'remove', '5.7', '198', '182'],
            ['2019-10-06', 'add', '1060.8', '188', '198']
        ]
        output = list()
        for obj in bank_obj.transactions:
            output.append(list(map(str, obj)))
            # print(output)
        self.assertEqual(expected_output, sorted(output, key=lambda x: x[0]))


if __name__ == '__main__':
    unittest.main()
