import calendar

from flask_restful import Resource
from .HttpCall import get_covid_registry_data, get_all_units
import datetime
from dateutil.relativedelta import relativedelta
import redis
import json


def generate_custom_rangers():

    current_date = datetime.datetime.now()
    current_date_str = current_date.strftime('%d/%m/%Y')
    current_month_str = '{:%m}'.format(current_date)
    current_year_str = '{:%Y}'.format(current_date)
    end_date_current_month = str(calendar.monthrange(int(current_year_str), int(current_month_str))[1])

    last_month_date = current_date - relativedelta(months=1)
    last_month_date_str = last_month_date.strftime('%d/%m/%Y')
    last_month_str = '{:%m}'.format(last_month_date)
    last_year_str = '{:%Y}'.format(last_month_date)
    end_date_last_month = str(calendar.monthrange(int(last_year_str), int(last_month_str))[1])

    eleven_months_ago_date = current_date - relativedelta(months=1)
    eleven_months_ago_month_str = '{:%m}'.format(eleven_months_ago_date)
    eleven_months_ago_year_str = '{:%Y}'.format(eleven_months_ago_date)


    last_31_days_range = f"{last_month_date_str} - {current_date_str}"
    last_30_days_range_str = (current_date - relativedelta(days=29)).strftime('%d/%m/%Y') + ' - ' + current_date_str
    this_month_range_str = f"01/{current_month_str}/{current_year_str} - {end_date_current_month}/{current_month_str}/{current_year_str}"
    last_month_range_str = f"01/{last_month_str}/{last_year_str} - {end_date_last_month}/{last_month_str}/{last_year_str}"
    last_12_month_range_str = f"01/{eleven_months_ago_month_str}/{eleven_months_ago_year_str} - {end_date_current_month}/{current_month_str}/{current_year_str}"
    this_year_range_str = f"01/01/{current_year_str} - 31/12/{current_year_str}"
    last_year_range_str = f"01/01/{str(int(current_year_str) - 1)} - 31/12/{str(int(current_year_str) - 1)}"

    list_custom_rangers = [last_30_days_range_str,
                           last_31_days_range,
                           this_month_range_str,
                           last_month_range_str,
                           last_12_month_range_str,
                           this_year_range_str,
                           last_year_range_str]

    return list_custom_rangers


def generate_month_rangers_last_12_months():

    current_date = datetime.datetime.now()
    list_of_date_rangers = []
    x = 0
    while x < 2:
        current_month_str = '{:%m}'.format(current_date)
        current_year_str = '{:%Y}'.format(current_date)
        end_date_current_month = str(calendar.monthrange(int(current_year_str), int(current_month_str))[1])

        date_range_str = f"01/{current_month_str}/{current_year_str} - {end_date_current_month}/{current_month_str}/{current_year_str}"
        list_of_date_rangers.append(date_range_str)
        current_date = current_date - relativedelta(months=1)
        x = x + 1

    return list_of_date_rangers

def generate_unit_ids():
    units = get_all_units()
    result = [unit['_id'] for unit in units]
    return result


def gen_cache():
    unit_ids = generate_unit_ids()
    date_rangers = generate_custom_rangers() + generate_month_rangers_last_12_months()
    # date_rangers = date_rangers[:2]
    cache_dict = {}
    for unit_id in unit_ids:
        for date_range in date_rangers:
            key = f'covid_registry_stats_{unit_id}_{date_range}'
            print(key)
            viz_result = get_covid_registry_data(unit_id, date_range)
            cache_dict[key] = viz_result
    return cache_dict


def save_cache(cache):
    r = redis.Redis(host='redis_service', port=6379, db=0)
    for key, value in cache.items():
        json_string = json.dumps(value)
        r.set(key, json_string)


def start_covid_registry_cache():
    print('cache started........')
    cache = gen_cache()
    save_cache(cache)
    print('cache is saved........')
    return cache


class covid_registry_data_cache(Resource):

    def post(self):
        return {'data': start_covid_registry_cache()}

    # ['5d5fa51e3a24ff00472ace57', '5d5fe2eba80a0c001b4eba44', '5d68e5d44c7220002695a030', '5d68f1abb0dbc20026d78d27', '5d6cd1b9b0dbc20026d78d29', '5d6e16a4b0dbc20026d78d2b', '5d6e16a6b0dbc20026d78d2c', '5d9c5a3da191cf001be7a97a', '5da558adf450790026cb95bf', '5da558c0f450790026cb95c0', '5db01c36f450790026cb95c2', '5e393f2ccdd561002668aba9', '5e609cc532dbc0001b09adbd']
