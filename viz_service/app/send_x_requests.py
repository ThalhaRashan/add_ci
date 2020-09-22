from flask import request
from flask_restful import Resource

from app.HttpCall import get_vizdata, get_qi_intervention_data, get_validation_dashboard_data, get_covid_registry_data, \
    get_covid_unit_data, get_completeness_data, get_vizRegion, get_validation_comp


class send_requests(Resource):

    def post(self):
        endpoint = request.form.get('endpoint')
        n = int(request.form.get('n'))
        x = 0
        unitId = '5d5fa51e3a24ff00472ace57'
        date_range = '01/08/2019 - 31/07/2020'
        month = '2020-06'
        fromDate = 'Wed Jan 01 2020 00:00:00 GMT+0530 (India Standard Time)'
        toDate = 'Wed Aug 17 2020 00:00:00 GMT+0530 (India Standard Time)'
        payload = {"unitIds": [unitId], "to": toDate, "from": fromDate}

        if endpoint == 'vizhospital':
            while x < n:
                get_vizdata(unitId, date_range)
                x += 1
        elif endpoint == 'VizDataRegional':
            while x < n:
                get_vizRegion(date_range)
                x += 1

        elif endpoint == 'completeness':
            while x < n:
                get_completeness_data(unitId, date_range)
                x += 1
        elif endpoint == 'QIIntervention':
            while x < n:
                get_qi_intervention_data(unitId, month)
                x += 1
        elif endpoint == 'validationCompleteness':
            while x < n:
                get_validation_comp(payload)
                x += 1

        elif endpoint == 'validationDashboard':
            while x < n:
                get_validation_dashboard_data(unitId, fromDate, toDate)
                x += 1
        elif endpoint == 'covid_registry_stats':
            while x < n:
                get_covid_registry_data(unitId, date_range)
                x += 1
        elif endpoint == 'covid_unit_stats':
            while x < n:
                get_covid_unit_data(unitId, date_range)
                x += 1

        return f'{n} requests sent to {endpoint}'
