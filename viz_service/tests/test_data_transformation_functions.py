import unittest
import json
from app.shared_functions import get_admission_data, get_qi_data, get_sari_qi_data, get_investigation_data, get_data_dict


# If there is a change in datatype possible duplicate variables in the json_raw_data the test data will be updated.

# Because of the number of variables and possible combinations of values we are going to look at a couple of variables
# from each form to confirm the expected values is accurate.

# After a change in a function we will look at any change in the expected value and



class TestTransformationFunctions(unittest.TestCase):

    def setUp(self):
        with open(r'tests\test_data\raw_json_data\all_json_test_data.json') as f:
            self.all_json_data = json.load(f)

        with open(r'tests\test_data\raw_json_data\icu_json_test_data.json') as f:
            self.unit_icu_json_data = json.load(f)

        with open(r'tests\test_data\raw_json_data\ward_json_test_data.json') as f:
            self.unit_ward_json_data = json.load(f)

        with open(r'tests\test_data\raw_json_data\icu_json_data_dic.json') as f:
            self.icu_json_data_dict = json.load(f)

        with open(r'tests\test_data\raw_json_data\ward_json_data_dic.json') as f:
            self.ward_json_data_dict = json.load(f)


    # functions to be tested
    #     getAdmissionData(patients, date, test_units=[], unitId_list=None, ward=False):
    #       CHECK THAT THE DATE FILTER WORKS
    #       Try with test units
    #       Try with unit list
    #       Try with ward true
    #       Try with emmtpy/brand new unit
    #       Create a new variable with list of needed variables
    #     get_sari_qi_data(patients, date, test_units=[], unitId_list=None, ward=False):
    #     get_qi_data(patients, date, test_units=[], unitId_list=None, ward=False):
    #     get_investigation_data(patients, date, test_units=[], unitId_list=None, ward=False):

    #     get_data_dict
    #       Take input as json data dict so it has a more controlled input and output.
    #       Test that it works with ward and ICU input.
    #       Cant have a empty data dict becuase they have a deafult if none.


    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
