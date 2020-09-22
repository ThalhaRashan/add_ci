import calendar

from dateutil.relativedelta import relativedelta
from flask_restful import Resource
from .HttpCall import get_all_units, get_vizdata
import datetime
import redis
import json


def generate_custom_rangers():

    current_date = datetime.datetime.now()
    current_date_str = current_date.strftime('%d/%m/%Y')
    current_month_str = '{:%m}'.format(current_date)
    current_year_str = '{:%Y}'.format(current_date)
    end_date_current_month = str(calendar.monthrange(int(current_year_str), int(current_month_str))[1])

    last_month_date = current_date - relativedelta(months=1)
    last_month_str = '{:%m}'.format(last_month_date)
    last_year_str = '{:%Y}'.format(last_month_date)
    end_date_last_month = str(calendar.monthrange(int(last_year_str), int(last_month_str))[1])

    eleven_months_ago_date = current_date - relativedelta(months=1)
    eleven_months_ago_month_str = '{:%m}'.format(eleven_months_ago_date)
    eleven_months_ago_year_str = '{:%Y}'.format(eleven_months_ago_date)


    last_30_days_range_str = (current_date - relativedelta(days=29)).strftime('%d/%m/%Y') + ' - ' + current_date_str
    this_month_range_str = f"01/{current_month_str}/{current_year_str} - {end_date_current_month}/{current_month_str}/{current_year_str}"
    last_month_range_str = f"01/{last_month_str}/{last_year_str} - {end_date_last_month}/{last_month_str}/{last_year_str}"
    last_12_month_range_str = f"01/{eleven_months_ago_month_str}/{eleven_months_ago_year_str} - {end_date_current_month}/{current_month_str}/{current_year_str}"
    this_year_range_str = f"01/01/{current_year_str} - 31/12/{current_year_str}"
    last_year_range_str = f"01/01/{str(int(current_year_str) - 1)} - 31/12/{str(int(current_year_str) - 1)}"

    list_custom_rangers =   [last_30_days_range_str,
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
    cache_dict = {}
    for unit_id in unit_ids:
        for date_range in date_rangers:
            viz_result = get_vizdata(unit_id, date_range)
            key = 'unit_dashboard' + unit_id + date_range
            cache_dict[key] = viz_result
    return cache_dict


def save_cache(cache):
    r = redis.Redis(host='redis_service', port=6379, db=0)
    for key, value in cache.items():
        json_string = json.dumps(value)
        r.set(key, json_string)


def start_cache():
    print('cache started........')
    cache = gen_cache()
    save_cache(cache)
    print('cache is saved........')
    return cache


class VizDataCache(Resource):

    def post(self):
        return {'data': start_cache()}


# if __name__ == "__main__":
#     print('run')
#     start_cache()
    # get_all_patients('id',1)
