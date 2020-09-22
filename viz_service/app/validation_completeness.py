import math
from datetime import datetime

from flask_restful import Resource
from flask import request

from .HttpCall import get_all_patients
from .shared_functions import number_of_admissions, get_core_variables, \
    get_completeness_core_data, \
    get_data_dict, \
    fill_empty_all_columns_on_branching_logic, get_admission_data


class validationCompleteness(Resource):

    def post(self):
        client_data = request.json
        unit_ids = client_data["unitIds"]
        # get to and from date and convert to correct date format
        fromDate = datetime.strptime(client_data["from"][:24], "%a %b %d %Y %H:%M:%S").strftime('%d/%m/%Y')
        toDate = datetime.strptime(client_data["to"][:24], "%a %b %d %Y %H:%M:%S").strftime('%d/%m/%Y')
        date_input = f'{fromDate} - {toDate}'
        # get the full registry data
        raw_unit_data = get_all_patients()
        registry_admission_data = get_admission_data(raw_unit_data, date_input, [], unit_ids, True)
        number_of_admission = number_of_admissions(registry_admission_data)
        # define the output dict
        registry_core_variable_completeness = {}
        if number_of_admission > 0:

            for unit in unit_ids:
                data_dictionary = get_data_dict(unit)
                core_variables = get_core_variables(data_dictionary)

                unit_admission_data = registry_admission_data.loc[registry_admission_data['unitId'] == unit]

                unit_data = fill_empty_all_columns_on_branching_logic(data_dict=data_dictionary, admissionData=unit_admission_data)
                unit_admission_data = unit_data['admissionData']

                unit_core_variable_completeness = get_completeness_core_data(unit_admission_data, core_variables)
                if math.isnan(unit_core_variable_completeness):
                    unit_core_variable_completeness = '100'

                unit_core_variable_completeness = str(unit_core_variable_completeness)

                registry_core_variable_completeness[unit] = unit_core_variable_completeness

        else:
            for unit in unit_ids:
                registry_core_variable_completeness[unit] = '100'


        return {'unit_core_variable_completeness': registry_core_variable_completeness}
