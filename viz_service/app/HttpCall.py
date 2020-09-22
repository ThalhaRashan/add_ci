from requests import request
import json


def get_all_patients(key=None, value=None):
    # url = "http://127.0.0.1:7171/auth/login"
    url = "http://127.0.0.1:7272/patient/getallpatients"
    # url = "http://data_service:7272/patient/getallpatients"

    payload = f"{key}={value}"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    response = request("POST", url, data=payload, headers=headers)

    json_data = json.loads(response.text)

    patients = json_data['docs']

    if (json_data['pages'] > 1):

        for index in range(json_data['pages'] + 1):
            if index < 2:
                pass
            else:
                payload = f"{key}={value}&page={index}"
                response = request("POST", url, data=payload, headers=headers)
                json_data = json.loads(response.text)
                patients.extend(json_data['docs'])


    return patients


def get_all_patients_de_identified(key=None, value=None):
    # url = "http://127.0.0.1:7171/auth/login"
    url = "http://127.0.0.1:7272/patient/deidentifiedgetallpatients"
    # url = "http://data_service:7272/patient/deidentifiedgetallpatients"

    payload = f"{key}={value}"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    response = request("POST", url, data=payload, headers=headers)

    json_data = json.loads(response.text)

    patients = json_data['docs']

    if (json_data['pages'] > 1):
        
        for index in range(json_data['pages']+1):
            if index < 2:
                pass
            else:
                payload = f"{key}={value}&page={index}"
                response = request("POST", url, data=payload, headers=headers)
                json_data = json.loads(response.text)
                patients.extend(json_data['docs'])


    return patients


def get_bed_count(unit_id=None):
    # url = "http://127.0.0.1:7171/auth/login"
    url = "http://127.0.0.1:7474/institute/getbedcount"
    # url = "http://institute_service:7474/institute/getbedcount"

    payload = f"unitId={unit_id}"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    response = request("POST", url, data=payload, headers=headers)
    print(response.text)

    json_data = json.loads(response.text)

    return json_data


def get_all_units():
    # url = "http://127.0.0.1:7171/auth/login"
    url = "http://127.0.0.1:7474/institute/getAllUnits"
    # url = "http://institute_service:7474/institute/getAllUnits"

    payload = f"unitId=test"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    response = request("POST", url, data=payload, headers=headers)

    json_data = json.loads(response.text)

    return json_data


def get_vizdata(unit_id, month):
    url = "http://127.0.0.1:5000/vizhospital"
    # this exactly calls localhost, no need to bind to docker

    payload = f"unitId={unit_id}&month={month}"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    response = request("POST", url, data=payload, headers=headers)

    json_data = json.loads(response.text)

    return json_data

def get_vizRegion(month):
    url = "http://127.0.0.1:5000/VizDataRegional"
    # this exactly calls localhost, no need to bind to docker

    payload = f"month={month}"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    response = request("POST", url, data=payload, headers=headers)

    json_data = json.loads(response.text)

    return json_data

def get_validation_comp(payload):
    url = "http://127.0.0.1:5000/validationCompleteness"
    # this exactly calls localhost, no need to bind to docker

    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    response = request("POST", url, data=payload, headers=headers)

    json_data = json.loads(response.text)

    return json_data

def get_completeness_data(unit_id, month):
    url = "http://127.0.0.1:5000/completeness"
    # this exactly calls localhost, no need to bind to docker

    payload = f"unitId={unit_id}&month={month}"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    response = request("POST", url, data=payload, headers=headers)

    json_data = json.loads(response.text)

    return json_data


def get_qi_intervention_data(unit_id, month):
    url = "http://127.0.0.1:5000/QIIntervention"
    # this exactly calls localhost, no need to bind to docker

    payload = f"unitId={unit_id}&month={month}"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    response = request("POST", url, data=payload, headers=headers)

    json_data = json.loads(response.text)

    return json_data


def get_covid_registry_data(unit_id, month):
    url = "http://127.0.0.1:5000/covid_registry_stats"
    # this exactly calls localhost, no need to bind to docker

    payload = f"unitId={unit_id}&month={month}"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    response = request("POST", url, data=payload, headers=headers)

    json_data = json.loads(response.text)

    return json_data


def get_covid_unit_data(unit_id, month):
    url = "http://127.0.0.1:5000/covid_unit_stats"
    # this exactly calls localhost, no need to bind to docker

    payload = f"unitId={unit_id}&month={month}"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    response = request("POST", url, data=payload, headers=headers)

    json_data = json.loads(response.text)

    return json_data


def get_validation_dashboard_data(unit_id, fromDate, toDate):
    url = "http://127.0.0.1:5000/validationDashboard"
    # this exactly calls localhost, no need to bind to docker

    payload = f"hospitalId=&unitId={unit_id}&fromDate={fromDate}&toDate={toDate}"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    response = request("POST", url, data=payload, headers=headers)

    json_data = json.loads(response.text)

    return json_data


def get_test_unit_ids():
    # url = "http://conf_service:7676/asset/gettestunitids"
    url = "http://127.0.0.1:7676/asset/gettestunitids"

    payload = f"assetName=test_unit_ids"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    response = request("POST", url, data=payload, headers=headers)

    json_data = json.loads(response.text)
    keys = json_data['unitIds']

    return keys


def get_json_data_dict(unit_id):
    # url = "http://conf_service:7676/conf/getdd"
    url = "http://127.0.0.1:7676/conf/getdd"


    payload = f"unitId={unit_id}"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    response = request("POST", url, data=payload, headers=headers)

    json_data = json.loads(response.text)

    return json_data


if __name__ == "__main__":
    print('run')
    # get_all_patients('id',1)
    get_all_units()
