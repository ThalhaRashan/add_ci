from flask import Flask
from flask_restful import Api
from flask_apscheduler import APScheduler
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask import request
from flask_restful import Resource

from .VizDataHospital import VizDataHospital
from .VizDataRegional import VizDataRegional
from .Completeness import Completeness
from .QI_intervention import QIIntervention
from .validation_completeness import validationCompleteness
from .validation_dashboard import validationDashboard
from .covid_unit_level import COVID_unit_stat
from .covid_registry_level import COVID_registry_stat
from .VizDataCache import VizDataCache, start_cache
from .completeness_data_cache import completeness_data_cache, start_completeness_cache
from .QI_intervention_data_cache import QI_intervention_Cache, start_qi_intervention_cache
from .covid_registry_cache import start_covid_registry_cache, covid_registry_data_cache
from .covid_unit_cache import start_covid_unit_cache, covid_unit_data_cache
from .validation_dashboard_cache import start_validation_dashboard_cache, ValidationDashboardCache
from .CsvData import CsvData

from .send_x_requests import send_requests

import tracemalloc


def create_app():
    tracemalloc.start(15)
    s1 = None
    s2 = None



    app = Flask(__name__, static_url_path='',
                static_folder='public',
                template_folder='public')
    # app.config["MONGO_URI"] = "mongodb://ishara1:ishara1@ds127704.mlab.com:27704/protect_cardiac"
    # app.config["MONGO_URI"] = "mongodb://139.59.62.22:27017/patients"
    app.config["MONGO_URI"] = "mongodb://mongo:27017/patients"
    mongo = PyMongo(app)
    app.db = mongo
    CORS(app)
    api = Api(app)

    # scheduler = APScheduler()
    # # it is also possible to enable the API directly
    # # scheduler.api_enabled = True
    # scheduler.init_app(app)
    # scheduler.start()
    # app.apscheduler.add_job(func=start_cache, trigger={
    #     'type': 'cron',
    #     'hour': 22,
    #     'minute': 00
    #     }, args=[], id='my_id_viz_unit')
    #
    # app.apscheduler.add_job(func=start_completeness_cache, trigger={
    #     'type': 'cron',
    #     'hour': 23,
    #     'minute': 00
    # }, args=[], id='my_id_com_report')
    #
    # app.apscheduler.add_job(func=start_qi_intervention_cache, trigger={
    #     'type': 'cron',
    #     'hour': 00,
    #     'minute': 00
    # }, args=[], id='my_id_qi_intervention_report')
    #
    # app.apscheduler.add_job(func=start_covid_registry_cache, trigger={
    #     'type': 'cron',
    #     'hour': 1,
    #     'minute': 00
    # }, args=[], id='my_id_covid_registry_data')
    #
    # app.apscheduler.add_job(func=start_covid_unit_cache, trigger={
    #     'type': 'cron',
    #     'hour': 2,
    #     'minute': 00
    # }, args=[], id='my_id_covid_unit_data')
    #
    # app.apscheduler.add_job(func=start_validation_dashboard_cache, trigger={
    #     'type': 'cron',
    #     'hour': 3,
    #     'minute': 00
    # }, args=[], id='my_id_validation_dasbhoard_data')


    @app.route("/check_memory", methods=['POST'])
    def check_m():
        global s1, s2
        trace = request.form.get('trace')
        filename = request.form.get('output_filename')

        if trace == 's2':
            s2 = tracemalloc.take_snapshot()
            with open(f"{filename}.txt", "w") as f:
                for i in s2.compare_to(s1, 'lineno')[:10]:
                    print(i)
                    f.write(f'{i} \n')
        elif trace == 's1':
            s1 = tracemalloc.take_snapshot()

        return f's2:'


    api.add_resource(VizDataHospital, '/vizhospital')
    api.add_resource(VizDataRegional, '/VizDataRegional')
    api.add_resource(Completeness, '/completeness')
    api.add_resource(QIIntervention, '/QIIntervention')
    api.add_resource(validationCompleteness, "/validationCompleteness")
    api.add_resource(validationDashboard, "/validationDashboard")
    api.add_resource(COVID_registry_stat, "/covid_registry_stats")
    api.add_resource(COVID_unit_stat, "/covid_unit_stats")
    api.add_resource(VizDataCache, '/vizcache')
    api.add_resource(completeness_data_cache, '/completeness_cache')
    api.add_resource(QI_intervention_Cache, '/QI_intervention_Cache')
    api.add_resource(covid_registry_data_cache, '/covid_registry_data_cache')
    api.add_resource(covid_unit_data_cache, '/covid_unit_data_cache')
    api.add_resource(ValidationDashboardCache, '/ValidationDashboardCache')
    api.add_resource(CsvData, '/csvdata')

    api.add_resource(send_requests, '/send_requests')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', debug=True)
