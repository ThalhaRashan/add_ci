import ast
import unittest
import json
import responses
from unittest import mock

from app import create_app
import os

import app


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'http://data_service:7272/patient/getallpatients':
        with open('tests/get_all_patients.json') as dataFile:
            data = dataFile.read()
            json_data = ast.literal_eval(data)
        return MockResponse(json_data, 200)

    elif args[0] == 'http://institute_service:7474/institute/getbedcount':
        with open('tests/get_bed_count.json') as dataFile:
            data = dataFile.read()
            json_data = ast.literal_eval(data)
        return MockResponse(json_data, 200)

    elif args[0] == 'http://institute_service:7474/institute/getAllUnits':
        with open('tests/get_all_units.json') as dataFile:
            data = dataFile.read()
            json_data = ast.literal_eval(data)
        return MockResponse(json_data, 200)

    elif args[0] == 'http://conf_service:7676/asset/gettestunitids':
        with open('tests/get_test_unit_ids.json') as dataFile:
            data = dataFile.read()
            json_data = ast.literal_eval(data)
        return MockResponse(json_data, 200)

    elif args[0] == 'http://data_service:7272/patient/deidentifiedgetallpatients':
        with open('tests/get_test_unit_ids.json') as dataFile:
            data = dataFile.read()
            json_data = ast.literal_eval(data)
        return MockResponse(json_data, 200)

    elif args[0] == 'http://conf_service:7676/conf/getdd':
        with open('tests/get_test_unit_ids.json') as dataFile:
            data = dataFile.read()
            json_data = ast.literal_eval(data)
        return MockResponse(json_data, 200)

    return MockResponse(None, 404)


def set_up_mock_responses(x):
    responses.add(responses.POST, 'http://data_service:7272/patient/getallpatients',
                  json=x.get_all_patients, status=200)
    responses.add(responses.POST, 'http://institute_service:7474/institute/getbedcount',
                  json=x.get_bed_count, status=200)
    responses.add(responses.POST, 'http://institute_service:7474/institute/getAllUnits',
                  json=x.get_all_units, status=200)
    responses.add(responses.POST, 'http://conf_service:7676/asset/gettestunitids',
                  json=x.get_test_unit_ids, status=200)


class TestFlaskApi(unittest.TestCase):
    def setUp(self):
        with open('tests/get_all_patients.json') as dataFile:
            data = dataFile.read()
            self.get_all_patients = ast.literal_eval(data)
        with open('tests/get_bed_count.json') as dataFile:
            data = dataFile.read()
            self.get_bed_count = ast.literal_eval(data)
        with open('tests/get_all_units.json') as dataFile:
            data = dataFile.read()
            self.get_all_units = ast.literal_eval(data)
        with open('tests/get_test_unit_ids.json') as dataFile:
            data = dataFile.read()
            self.get_test_unit_ids = ast.literal_eval(data)
        application = create_app()
        self.app = application.test_client()
        # os.chdir('../')

    # @mock.patch('requests.post', side_effect=mocked_requests_get)

    @responses.activate
    def test_VizDataHospital(self):
        # os.chdir('../')
        set_up_mock_responses(self)
        payload = {'month': '01/01/2020 - 01/10/2020',
                   'unitId': '5d5fa51e3a24ff00472ace57'}
        response = self.app.post('/vizhospital', data=payload)
        expected_json_data = open("tests/VizDataHospital_expected_return.json")
        expected__data = json.load(expected_json_data)
        # with open('tests/VizDataHospital_expected_return.json', 'w') as fp:
        #     json.dump(json.loads(response.get_data().decode()), fp)
        self.assertEqual(json.loads(response.get_data().decode()), expected__data)

    @responses.activate
    def test_VizDataRegional(self):
        # os.chdir('../')
        set_up_mock_responses(self)
        payload = {'month': '01/01/2020 - 01/10/2020'}
        response = self.app.post('/VizDataRegional', data=payload)
        expected_json_data = open("tests/VizDataRegional_expected_return.json")
        expected__data = json.load(expected_json_data)
        # with open('tests/VizDataRegional_expected_return.json', 'w') as fp:
        #     json.dump(json.loads(response.get_data().decode()), fp)
        self.assertEqual(json.loads(response.get_data().decode()), expected__data)

    @responses.activate
    def test_covid_unit_stats(self):
        # os.chdir('../')
        set_up_mock_responses(self)
        payload = {"unitId": "5d5fa51e3a24ff00472ace57",
                   'month': '01/01/2020 - 01/10/2020'}

        response = self.app.post('/covid_unit_stats', data=payload)
        # expected_json_data = open("tests/Completeness_expected_return.json")
        # expected__data = json.load(expected_json_data)
        # with open('tests/Completeness_expected_return.json', 'w') as fp:
        #     json.dump(json.loads(response.get_data().decode()), fp)
        self.assertEqual(json.loads(response.get_data().decode()), '74.5')

    @responses.activate
    def test_covid_registry_stats(self):
        # os.chdir('../')
        set_up_mock_responses(self)
        payload = {"unitId": "5d5fa51e3a24ff00472ace57",
                   'month': '01/01/2020 - 01/10/2020'}

        response = self.app.post('/covid_registry_stats', data=payload)
        # expected_json_data = open("tests/Completeness_expected_return.json")
        # expected__data = json.load(expected_json_data)
        # with open('tests/Completeness_expected_return.json', 'w') as fp:
        #     json.dump(json.loads(response.get_data().decode()), fp)
        self.assertEqual(json.loads(response.get_data().decode()), '74.5')

    @responses.activate
    def test_Completeness(self):
        # os.chdir('../')
        set_up_mock_responses(self)
        payload = {"unitId": "5d5fa51e3a24ff00472ace57",
                   'month': '01/01/2020 - 01/10/2020'}
        response = self.app.post('/completeness', data=payload)
        expected_json_data = open("tests/Completeness_expected_return.json")
        expected__data = json.load(expected_json_data)
        # with open('tests/Completeness_expected_return.json', 'w') as fp:
        #     json.dump(json.loads(response.get_data().decode()), fp)
        self.assertEqual(json.loads(response.get_data().decode()), expected__data)

    @responses.activate
    def test_QIIntervention(self):
        # os.chdir('../')
        set_up_mock_responses(self)
        payload = {"unitId": "5d5fa51e3a24ff00472ace57",
                   'month': '01/01/2020 - 01/10/2020'}
        response = self.app.post('/QIIntervention', data=payload)
        # expected_json_data = open("tests/Completeness_expected_return.json")
        # expected__data = json.load(expected_json_data)
        # with open('tests/Completeness_expected_return.json', 'w') as fp:
        #     json.dump(json.loads(response.get_data().decode()), fp)
        self.assertEqual(json.loads(response.get_data().decode()), {'x': ''})

    @responses.activate
    def test_validationDashboard(self):
        # os.chdir('../')
        set_up_mock_responses(self)
        payload = {'from': 'Wed Jan 01 2020 00:00:00 GMT+0530 (India Standard Time)',
                   "to": "Thu Oct 01 2020 00:00:00 GMT+0530 (India Standard Time)",
                   'unitId': ''}
        response = self.app.post('/validationDashboard', data=payload)
        # expected_json_data = open("tests/Completeness_expected_return.json")
        # expected__data = json.load(expected_json_data)
        # with open('tests/Completeness_expected_return.json', 'w') as fp:
        #     json.dump(json.loads(response.get_data().decode()), fp)
        self.assertEqual(json.loads(response.get_data().decode()), '74.5')


if __name__ == "__main__":
    unittest.main()
