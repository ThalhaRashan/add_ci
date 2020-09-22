from datetime import datetime
import pandas as pd
import json

from flask_restful import Resource
from flask import request

from .constants import completeness_core_variables_to_exclude,\
    completeness_sari_variables_to_exclude,\
    completeness_sari_daily_variables_to_exclude,\
    completeness_daily_assessment_variables_to_exclude
from .HttpCall import get_all_patients, get_test_unit_ids
from .shared_functions import get_admission_data, get_sari_qi_data, get_qi_data, single_variable_completeness, \
    get_completeness_per, create_index_for_daily_data_to_get_completeness, get_core_variables, \
    get_data_dict, \
    fill_empty_all_columns_on_branching_logic, get_all_variables_from_data_dict, get_completeness_for_dataset


class validationDashboard(Resource):

    def post(self):
        # Get user input information
        unit_id = request.form.get("unitId")
        hospital_id = request.form.get("hospitalId")
        test_units = get_test_unit_ids()
        # get to and from date and convert to correct date format
        fromDate = datetime.strptime(request.form.get("fromDate")[:24], "%a %b %d %Y %H:%M:%S").strftime('%d/%m/%Y')
        toDate = datetime.strptime(request.form.get("toDate")[:24], "%a %b %d %Y %H:%M:%S").strftime('%d/%m/%Y')
        date_input = f'{fromDate} - {toDate}'

        data_dict_status = False

        # check if we are using a hospital or unit filter and set keys
        if unit_id != '':
            key = 'unitId'
            value = unit_id
            unit_types = ['Ward', 'ICU']
        elif hospital_id != '':
            key = 'hospitalId'
            value = hospital_id
            unit_types = ['ICU']
        else:
            key = None
            value = None
            unit_types = ['ICU']

        # get the full registry data
        raw_unit_data = get_all_patients(key, value)
        admission_data = get_admission_data(raw_unit_data, date_input, test_units=test_units, ward=True)

        sari_qi_data = get_sari_qi_data(raw_unit_data, date_input, test_units=test_units, ward=True)
        qi_data = get_qi_data(raw_unit_data, date_input, test_units=test_units, ward=True)

        if 'Ward' in unit_types:
            units = [value]
        else:
            try:
                units = admission_data['unitId'].unique()
            except:
                units = [test_units[0]]

            if len(units) < 1:
                units = [raw_unit_data[0]['unitId']]

        del raw_unit_data

        core_data = pd.DataFrame()
        daily_assessment_data = pd.DataFrame()
        sari_data = pd.DataFrame()
        sari_daily_assessment_data = pd.DataFrame()


        # Now that we have all patient data we need we get the data dictonaryes for the
        # indiviual units

        for unit in units:

            if 'unitId' in admission_data:

                # filter for single unit and check it is a ICU or ward depending on if the user selected a unit or
                # multiple units
                unit_admission_data = admission_data.loc[(admission_data['unitId'] == unit) &
                                                         (admission_data['unit_type'].isin(unit_types))]

            else:
                unit_admission_data = pd.DataFrame()

            if not data_dict_status:
                data_dictionary = get_data_dict(unit)
                core_variables = get_core_variables(data_dictionary)
                variables = get_all_variables_from_data_dict(data_dictionary)

                core_variables = core_variables['required_admission_cols']
                core_variables = [x for x in core_variables if 'sari_' not in x]
                core_variables = [x for x in core_variables if x not in completeness_core_variables_to_exclude]

                sari_variables = variables['sari_admission_variables'] + variables['sari_discharge_variables']
                sari_variables = [x for x in sari_variables if x not in completeness_sari_variables_to_exclude]

                sari_daily_variables = variables['sari_daily_assessment_variables']
                sari_daily_variables = [x for x in sari_daily_variables if x not in completeness_sari_daily_variables_to_exclude]

                daily_assessment_variables = variables['daily_assessment_variables']
                daily_assessment_variables = [x for x in daily_assessment_variables if
                                              x not in completeness_daily_assessment_variables_to_exclude]

                data_dict_status = True

            else:
                data_dict_status = True

            if len(unit_admission_data) > 0:
                if data_dict_status:
                    data_dictionary = get_data_dict(unit)
                    core_variables = get_core_variables(data_dictionary)
                    variables = get_all_variables_from_data_dict(data_dictionary)

                    core_variables = core_variables['required_admission_cols']
                    core_variables = [x for x in core_variables if 'sari_' not in x]
                    core_variables = [x for x in core_variables if x not in completeness_core_variables_to_exclude]

                    sari_variables = variables['sari_admission_variables'] + variables['sari_discharge_variables']
                    sari_variables = [x for x in sari_variables if x not in completeness_sari_variables_to_exclude]

                    sari_daily_variables = variables['sari_daily_assessment_variables']
                    sari_daily_variables = [x for x in sari_daily_variables if x not in completeness_sari_daily_variables_to_exclude]

                    daily_assessment_variables = variables['daily_assessment_variables']
                    daily_assessment_variables = [x for x in daily_assessment_variables if
                                                  x not in completeness_daily_assessment_variables_to_exclude]

                # try and get list of all variables from the data dict so we can select the variables we need completes
                # from

                # get patient id's so we can select patients the correct qi and sari qi patient records
                patients_ids = unit_admission_data['patient_id'].unique()

                daily_dataset_index = create_index_for_daily_data_to_get_completeness(unit_admission_data)
                sari_daily_dataset_index = daily_dataset_index.loc[
                    daily_dataset_index['admission.sari'].isin(['Suspected', 'Confirmed'])]

                unit_qi_data = qi_data.loc[qi_data['patient_id'].isin(patients_ids)]

                unit_qi_data = unit_qi_data.merge(daily_dataset_index[['patient_id', 'date_of_assessment']],
                                                  left_on=['patient_id', 'date_of_daily_assessment'],
                                                  right_on=['patient_id', 'date_of_assessment'],
                                                  how='outer').reset_index(drop=True)

                unit_sari_qi_data = sari_qi_data.loc[sari_qi_data['patient_id'].isin(patients_ids)]

                unit_sari_qi_data = unit_sari_qi_data.merge(
                    sari_daily_dataset_index[['patient_id', 'date_of_assessment']],
                    left_on=['patient_id', 'date_of_sari_daily_assessment'],
                    right_on=['patient_id', 'date_of_assessment'],
                    how='outer').reset_index(drop=True)

                unit_data = fill_empty_all_columns_on_branching_logic(data_dict=data_dictionary,
                                                                      admissionData=unit_admission_data,
                                                                      dailyAssessmentData=unit_qi_data,
                                                                      sariDaily_assessment=unit_sari_qi_data)

                unit_admission_data = unit_data['admissionData']
                unit_sari_data = unit_admission_data.loc[unit_admission_data['admission_sari'].isin(['Confirmed', 'Suspected'])]
                unit_qi_data = unit_data['dailyAssessmentData']
                unit_sari_qi_data = unit_data['sariDaily_assessment']

                core_data = pd.concat([core_data, unit_admission_data[core_variables]])
                daily_assessment_data = pd.concat([daily_assessment_data, unit_qi_data[daily_assessment_variables]])
                sari_data = pd.concat([sari_data, unit_sari_data[sari_variables]])
                sari_daily_assessment_data = pd.concat(
                    [sari_daily_assessment_data, unit_sari_qi_data[sari_daily_variables]])

        core_overall_completeness = get_completeness_per(get_completeness_for_dataset(core_data))
        if core_overall_completeness != core_overall_completeness:
            core_overall_completeness = 'No data'

        daily_assessment_overall_completeness = get_completeness_per(
            get_completeness_for_dataset(daily_assessment_data))
        if daily_assessment_overall_completeness != daily_assessment_overall_completeness:
            daily_assessment_overall_completeness = 'No data'

        sari_overall_completeness = get_completeness_per(get_completeness_for_dataset(sari_data))
        if sari_overall_completeness != sari_overall_completeness:
            sari_overall_completeness = 'No data'

        sari_daily_assessment_overall_completeness = get_completeness_per(
            get_completeness_for_dataset(sari_daily_assessment_data))
        if sari_daily_assessment_overall_completeness != sari_daily_assessment_overall_completeness:
            sari_daily_assessment_overall_completeness = 'No data'


        variable_completeness = []

        core_variable_completeness = single_variable_completeness(core_data, core_variables,
                                                                  ['admission_assessment',
                                                                   'discharge_', 'admission_', '1'])
        if len(core_variable_completeness) > 0:
            variable_completeness.append({'name': f'Core forms (Number of patients = {len(core_data)})', 'completeness': ''})
            variable_completeness = variable_completeness + core_variable_completeness
            variable_completeness.append({'name': 'Overall completeness', 'completeness': core_overall_completeness})

        daily_assessment_variable_completeness = single_variable_completeness(daily_assessment_data,
                                                                              daily_assessment_variables,
                                                                              ['daily_assessment_', '1'])
        if len(daily_assessment_variable_completeness) > 0:
            variable_completeness.append(
                {'name': f'Daily Q form (Number of daily assessment = {len(daily_assessment_data)})', 'completeness': ''})
            variable_completeness = variable_completeness + daily_assessment_variable_completeness
            variable_completeness.append(
                {'name': 'Overall completeness', 'completeness': daily_assessment_overall_completeness})

        sari_variable_completeness = single_variable_completeness(sari_data, sari_variables,
                                                                  ['sari_admission_assessment_',
                                                                   'sari_pre_discharge_', '1'])
        if len(sari_variable_completeness) > 0:
            variable_completeness.append(
                {'name': f'SARI admission and discharge form (Number of SARI patients = {len(sari_data)})', 'completeness': ''})
            variable_completeness = variable_completeness + sari_variable_completeness
            variable_completeness.append({'name': 'Overall completeness', 'completeness': sari_overall_completeness})


        sari_daily_assessment_variable_completeness = single_variable_completeness(sari_daily_assessment_data,
                                                                                   sari_daily_variables,
                                                                                   ['sari_daily_assessment_', '1'])
        if len(sari_daily_assessment_variable_completeness) > 0:
            variable_completeness.append(
                {'name': f'SARI daily form (Number of SARI daily assessments = {len(sari_daily_assessment_data)})', 'completeness': ''})
            variable_completeness = variable_completeness + sari_daily_assessment_variable_completeness
            variable_completeness.append(
                {'name': 'Overall completeness', 'completeness': sari_daily_assessment_overall_completeness})

        return json.dumps(variable_completeness)
