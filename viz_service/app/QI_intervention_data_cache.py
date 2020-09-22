from flask_restful import Resource
from .HttpCall import get_all_units, get_qi_intervention_data
import datetime
import redis
import json


def generate_month_array(curr_mon):
    months = []
    count = 0
    while count < 6:
        months.append(curr_mon - count)
        count += 1

    return months


def generate_unit_ids():
    units = get_all_units()
    result = [unit['_id'] for unit in units]
    return result


def generate_months_years():
    current_date = datetime.datetime.now()
    month_number = current_date.month
    year = current_date.year

    month_array = generate_month_array(month_number)
    months_years = []
    for item in month_array:
        if item > 0:
            if len(str(item)) == 2:
                _temp = str(year) + '-' + str(item)
            else:
                _temp = str(year) + '-0' + str(item)
            months_years.append(_temp)
        else:
            _prev_month = 12 + item
            _prev_year = year - 1
            if len(str(_prev_month)) == 2:
                _temp = str(_prev_year) + '-' + str(_prev_month)
            else:
                _temp = str(_prev_year) + '-0' + str(_prev_month)
            months_years.append(_temp)
    return months_years


def gen_cache():
    unit_ids = generate_unit_ids()
    month_years = generate_months_years()
    cache_dict = {}
    for unit_id in unit_ids:
        for month_year in month_years:
            viz_result = get_qi_intervention_data(unit_id, month_year)
            key = unit_id + month_year
            cache_dict[key] = viz_result
    return cache_dict


def save_cache(cache):
    r = redis.Redis(host='redis_service', port=6379, db=0)
    for key, value in cache.items():
        json_string = json.dumps(value)
        r.set(key, json_string)


def start_qi_intervention_cache():
    print('cache started........')
    cache = gen_cache()
    save_cache(cache)
    print('cache is saved........')
    return cache


class QI_intervention_Cache(Resource):

    def post(self):
        return {'data': start_qi_intervention_cache()}


# if __name__ == "__main__":
#     print('run')
#     start_cache()
    # get_all_patients('id',1)
