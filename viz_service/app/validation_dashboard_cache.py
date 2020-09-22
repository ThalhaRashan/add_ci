from datetime import datetime, timedelta
from flask_restful import Resource
from .HttpCall import get_all_units, get_validation_dashboard_data
import redis
import json


def generate_previous_week_date_ranges(number_weeks):
    x = 1
    week_ranges = []
    dt = datetime.now()
    start_this_week = dt - timedelta(days=dt.weekday())
    time_zone = ' GMT+0530 (India Standard Time)'
    time = ' 00:00:00'
    while x <= number_weeks:
        start = start_this_week - timedelta(days=(7*x))
        end = start + timedelta(days=6)
        time_dict = {'fromDate': start.strftime('%a %b %d %Y') + time + time_zone, 'toDate': end.strftime('%a %b %d %Y') + time + time_zone}
        week_ranges.append(time_dict)
        x += 1

    return week_ranges

def generate_unit_ids():
    units = get_all_units()
    result = [unit['_id'] for unit in units] + ['']
    return result


def gen_cache():
    unit_ids = generate_unit_ids()
    hospital_id = ''
    date_rangers = generate_previous_week_date_ranges(2)
    cache_dict = {}
    for unit_id in unit_ids:
        for date_range in date_rangers:
            viz_result = get_validation_dashboard_data(unit_id, date_range['fromDate'], date_range['toDate'])
            key = f'validation_dashboard_{hospital_id}_{unit_id}_{date_range["fromDate"][:15]}_{date_range["toDate"][:15]}'
            cache_dict[key] = viz_result
    return cache_dict


def save_cache(cache):
    r = redis.Redis(host='redis_service', port=6379, db=0)
    for key, value in cache.items():
        json_string = json.dumps(value)
        r.set(key, json_string)


def start_validation_dashboard_cache():
    print('cache started........')
    cache = gen_cache()
    save_cache(cache)
    print('cache is saved........')
    return cache


class ValidationDashboardCache(Resource):

    def post(self):
        return {'data': start_validation_dashboard_cache()}


# if __name__ == "__main__":
#     print('run')
#     start_cache()
    # get_all_patients('id',1)