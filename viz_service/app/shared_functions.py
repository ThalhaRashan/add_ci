from operator import itemgetter
import math
from collections import defaultdict
from datetime import datetime, timedelta
from numbers import Number

from dateutil import relativedelta

import pandas as pd
import numpy as np
from numpy import exp, log

from pandas import json_normalize

from .HttpCall import get_json_data_dict
from .constants import colors


def filter_for_month(data, date, test_units=[], unitId_list=None, ward=False):
    """This function gets a user input month and gets the start date of the month by adding -01 and the last day of
    of the month by using calendar.monthrange which gives the end date of the month given a month and year it then
    takes the data given and filters it based on the column specified using the start and and end """
    filtered_data = None

    data = data[~data['unitId'].isin(test_units)]
    data['unit_type'] = 'ICU'

    if unitId_list is None:
        unitId_list = data['unitId'].unique().tolist()

    for unit in unitId_list:
        column = 'admission.date_of_admission'
        unit_data = data.loc[data['unitId'] == unit]

        if date is not None:

            try:
                temp_data = unit_data.dropna(subset=[column])
            except:
                temp_data = pd.DataFrame()

            # check if we want to filter data if the unit is a ward and then check if the unit is a ward and
            # theck that we are looking at admission dates not the date of a episode

            if ward & (len(temp_data) < 1) & (column == 'admission.date_of_admission'):
                column = 'admission.date_of_admission_hospital'
                unit_data['unit_type'] = 'Ward'

            if len(date) == 23:
                dates = date.split(' - ')
                dates = [datetime.strptime(d, '%d/%m/%Y') for d in dates]
                start_date = str(dates[0])[:10]
                end_date = str(dates[1])[:10]
                unit_data = unit_data[(unit_data[column] >= start_date) & (unit_data[column] <= end_date)]
                filtered_data = pd.concat([filtered_data, unit_data])
            elif len(date) == 4:
                year = date
                end_date = year + '-12' + '-31'
                start_date = year + '-01' + '-01'
                unit_data = unit_data[(unit_data[column] >= start_date) & (unit_data[column] <= end_date)]
                filtered_data = pd.concat([filtered_data, unit_data])
            else:
                raise Exception('Invalid date input')
        else:
            raise Exception('Invalid date input')

    return filtered_data


def filter_before_month(data, column, date):
    """This function gets a user input month and gets the start date of the month by adding -01 and the last day of
    of the month by using calendar.monthrange which gives the end date of the month given a month and year it then
    takes the data given and filters it based on the column specified using the start and and end  """
    if date is not None:
        if len(date) == 23:
            dates = date.split(' - ')
            dates = [datetime.strptime(d, '%d/%m/%Y') for d in dates]
            end_date = str(dates[1])[:10]
            # end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            data = data[(data[column] <= end_date)]
        elif len(date) == 4:
            end_date = date + '-12' + '-31'
            data = data[(data[column] <= end_date)]

    else:
        raise Exception('Invalid date input')

    return data


def get_admission_data(patients, date, test_units=[], unitId_list=None, ward=False):
    """Takes json input and flattens the first nested layer of data and filters by 'A' month"""

    normalized_data = json_normalize(patients)
    number_patients = len(normalized_data)
    num = [1] * number_patients
    normalized_data['num'] = num

    column = 'admission.date_of_admission'

    # check if either the hospital or icu admission date is avalble
    if ward and column not in normalized_data:
        column = 'admission.date_of_admission_hospital'

    if number_patients > 0 and column in normalized_data and 'unitId' in normalized_data:
        if len(normalized_data) > 0:
            normalized_data = filter_for_month(normalized_data, date, test_units, unitId_list, ward)
            normalized_data = normalized_data.replace('', np.nan)
            normalized_data = join_sari_admission_variables(normalized_data)
            normalized_data = merge_different_age_columns_into_one(normalized_data)
        else:
            normalized_data = 'No data'
    else:
        normalized_data = 'No data'

    return normalized_data


def get_sari_qi_data(patients, date, test_units=[], unit_list=None, ward=False):
    assessment_list = []
    list_unique_id = []
    list_admission_date = []
    list_unit_id = []
    list_hospital_admission_date = []

    for patient in patients:
        if 'sariDailyAssessments' in patient:
            if len(patient['sariDailyAssessments']) > 0:
                for assessment in patient['sariDailyAssessments']:
                    unique_id = patient['admission']['patient_id']
                    unitId = patient['unitId']
                    try:
                        admission_date = patient['admission']['date_of_admission']
                    except:
                        admission_date = ''
                    try:
                        hospital_admission_date = patient['admission']['date_of_admission_hospital']
                    except:
                        hospital_admission_date = ''
                    if type(assessment) == dict:
                        assessment_list.append(assessment)
                        list_unique_id.append(unique_id)
                        list_admission_date.append(admission_date)
                        list_hospital_admission_date.append(hospital_admission_date)
                        list_unit_id.append(unitId)
                    elif type(assessment) == list:
                        for x in assessment:
                            assessment_list.append(x)
                            list_unique_id.append(unique_id)
                            list_admission_date.append(admission_date)
                            list_hospital_admission_date.append(hospital_admission_date)
                            list_unit_id.append(unitId)

    if len(assessment_list) > 0:
        data = pd.DataFrame(assessment_list)
        data['patient_id'] = list_unique_id
        data['admission.date_of_admission'] = list_admission_date
        data['admission.date_of_admission_hospital'] = list_hospital_admission_date
        data['unitId'] = list_unit_id
        data_for_month = filter_for_month(data, date, test_units, unit_list, ward)
        data_for_month['admission.date_of_admission'] = pd.to_datetime(data_for_month['admission.date_of_admission'],
                                                                       format='%Y-%m-%d', errors='coerce')
        data_for_month['admission.date_of_admission'] = data_for_month['admission.date_of_admission'].dt.strftime(
            '%Y-%m-%d')
        data_for_month = data_for_month.replace('', np.nan)

    else:
        return pd.DataFrame()

    return data_for_month


def get_qi_data(patients, date, test_units=[], unit_list=None, ward=False):
    assessment_list = []
    list_unique_id = []
    list_admission_date = []
    list_unit_id = []
    list_hospital_admission_date = []

    for patient in patients:
        if 'dailyAssessments' in patient:
            if len(patient['dailyAssessments']) > 0:
                for assessment in patient['dailyAssessments']:
                    unique_id = patient['admission']['patient_id']
                    unitId = patient['unitId']
                    try:
                        admission_date = patient['admission']['date_of_admission']
                    except:
                        admission_date = ''
                    try:
                        hospital_admission_date = patient['admission']['date_of_admission_hospital']
                    except:
                        hospital_admission_date = ''
                    if type(assessment) == dict:
                        assessment_list.append(assessment)
                        list_unique_id.append(unique_id)
                        list_admission_date.append(admission_date)
                        list_hospital_admission_date.append(hospital_admission_date)
                        list_unit_id.append(unitId)
                    elif type(assessment) == list:
                        for x in assessment:
                            assessment_list.append(x)
                            list_unique_id.append(unique_id)
                            list_admission_date.append(admission_date)
                            list_hospital_admission_date.append(hospital_admission_date)
                            list_unit_id.append(unitId)

    if len(assessment_list) > 0:
        data = pd.DataFrame(assessment_list)
        data['patient_id'] = list_unique_id
        data['admission.date_of_admission'] = list_admission_date
        data['admission.date_of_admission_hospital'] = list_hospital_admission_date
        data['unitId'] = list_unit_id
        data_for_month = filter_for_month(data, date, test_units, unit_list, ward)
        data_for_month['admission.date_of_admission'] = pd.to_datetime(data_for_month['admission.date_of_admission'],
                                                                       format='%Y-%m-%d', errors='coerce')
        data_for_month['admission.date_of_admission'] = data_for_month['admission.date_of_admission'].dt.strftime(
            '%Y-%m-%d')
        data_for_month = data_for_month.replace('', np.nan)

    else:
        return pd.DataFrame()

    return data_for_month


def get_investigation_data(patients, date, test_units=[], unit_list=None, ward=False):
    investigation_list = []
    list_unique_id = []
    list_admission_date = []
    list_unit_id = []
    list_hospital_admission_date = []

    for patient in patients:
        if 'investigations' in patient:
            if len(patient['investigations']) > 0:
                for assessment in patient['investigations']:
                    unique_id = patient['admission']['patient_id']
                    unitId = patient['unitId']
                    try:
                        admission_date = patient['admission']['date_of_admission']
                    except:
                        admission_date = ''
                    try:
                        hospital_admission_date = patient['admission']['date_of_admission_hospital']
                    except:
                        hospital_admission_date = ''
                    if type(assessment) == dict:
                        investigation_list.append(assessment)
                        list_unique_id.append(unique_id)
                        list_admission_date.append(admission_date)
                        list_hospital_admission_date.append(hospital_admission_date)
                        list_unit_id.append(unitId)
                    elif type(assessment) == list:
                        for x in assessment:
                            investigation_list.append(x)
                            list_unique_id.append(unique_id)
                            list_admission_date.append(admission_date)
                            list_hospital_admission_date.append(hospital_admission_date)
                            list_unit_id.append(unitId)

    if len(investigation_list) > 0:
        data = pd.DataFrame(investigation_list)
        data['patient_id'] = list_unique_id
        data['admission.date_of_admission'] = list_admission_date
        data['admission.date_of_admission_hospital'] = list_hospital_admission_date
        data['unitId'] = list_unit_id
        data_for_month = filter_for_month(data, date, test_units, unit_list, ward)
        data_for_month['admission.date_of_admission'] = pd.to_datetime(
            data_for_month['admission.date_of_admission'],
            format='%Y-%m-%d', errors='coerce')
        data_for_month['admission.date_of_admission'] = data_for_month['admission.date_of_admission'].dt.strftime(
            '%Y-%m-%d')
        data_for_month = data_for_month.replace('', np.nan)

    else:
        return pd.DataFrame()

    return data_for_month


def join_sari_admission_variables(all_data):
    if 'admission.sari' in all_data and 'sariAdmissionAssessment.sari' in all_data:
        all_data.loc[(all_data['admission.sari']).isna(), 'admission.sari'] = all_data['sariAdmissionAssessment.sari']
    elif 'sariAdmissionAssessment.sari' in all_data:
        all_data['admission.sari'] = all_data['sariAdmissionAssessment.sari']

    return all_data


def merge_different_age_columns_into_one(admission_data):
    if 'admission.age_ymd.year' in admission_data:

        if 'admission.age' not in admission_data:
            admission_data['admission.age'] = np.nan

        # replace all nan in adm admission.age_ymd
        age_ymd_cols = ['admission.age_ymd.year', 'admission.age_ymd.month', 'admission.age_ymd.day']

        admission_data[age_ymd_cols] = admission_data[age_ymd_cols].replace(np.nan, 0)

        admission_data['age_ymd'] = admission_data['admission.age_ymd.year'] + \
                                    (admission_data['admission.age_ymd.month'] / 12) + \
                                    (admission_data['admission.age_ymd.day'] / 365)

        admission_data['age_ymd'] = admission_data['age_ymd'].replace(0, np.nan)

        admission_data.loc[(admission_data['admission.age']).isna(), 'admission.age'] = admission_data['age_ymd']

    return admission_data


def merge_culture_columns(data):
    if 'type_of_culture' in data:
        if 'culture' in data:
            data.loc[data['type_of_culture'].isna(), 'type_of_culture'] = data['culture']
    else:
        data['type_of_culture'] = np.nan

    return data


def number_of_hospitals(data):
    number_of_hospitals = data['hospitalId'].nunique()
    return number_of_hospitals


def number_of_units(data):
    number_of_units = data['unitId'].nunique()
    return number_of_units


def number_of_beds(data, testUnits, date, unit_list=False):
    if 'totalBeds' in str(data):
        pandasData = pd.DataFrame(data)
        flattenedTotalBeds = pd.DataFrame({
            col: np.repeat(pandasData[col].values, pandasData['totalBeds'].str.len())
            for col in pandasData.columns.drop('totalBeds')}
        ).assign(**{'totalBeds': np.concatenate(pandasData['totalBeds'].values)})[pandasData.columns]
        # flattenedData = flattenedTotalBeds
        flattenedTotalBeds = flattenedTotalBeds.drop('createdAt', axis=1)
        flattenedTotalBeds = pd.concat(
            [flattenedTotalBeds.drop('totalBeds', axis=1), pd.DataFrame(flattenedTotalBeds['totalBeds'].tolist())],
            axis=1)
        flattenedData = flattenedTotalBeds[~flattenedTotalBeds['_id'].isin(testUnits)]
        filteredData = filter_before_month(flattenedData, 'createdAt', date)
        filteredData['createdAt'] = pd.to_datetime(filteredData['createdAt'])
        orderedData = filteredData.sort_values(by=['createdAt'], ascending=False)
        duplicateFreeData = orderedData.drop_duplicates('_id').sort_index()
        duplicateFreeData['totalBeds'] = pd.to_numeric(duplicateFreeData.totalBeds, errors='coerce').fillna(0)
        if (isinstance(unit_list, list)):
            if len(unit_list) > 0:
                duplicateFreeData = duplicateFreeData.loc[duplicateFreeData['_id'].isin(unit_list)]
            else:
                return 'No data'
        numberOfBeds = int(duplicateFreeData['totalBeds'].sum())
    else:
        numberOfBeds = 'No data'

    return numberOfBeds


def patient_satisfaction(data):
    """Gets the replacers the string level of satisfaction to number levels gets the mean level of satisfaction rounds
    it to the closest satisfaction and returns the string representation of that number """
    if 'postQols.overall_satisfaction' in data:
        satisfaction_levels = ['Not satisfied at all', 'Mostly dissatisfied', 'Somewhat satisfied', "Mostly satisfied",
                               'Highly satisfied']
        satisfaction_list = data['postQols.overall_satisfaction'].replace(satisfaction_levels, [1, 2, 3, 4, 5])
        mean_satisfaction = round(satisfaction_list.mean())
        if mean_satisfaction == 5:
            satisfaction = "Highly satisfied"
        elif mean_satisfaction == 4:
            satisfaction = "Mostly satisfied"
        elif mean_satisfaction == 3:
            satisfaction = "Somewhat satisfied"
        elif mean_satisfaction == 2:
            satisfaction = "Mostly dissatisfied"
        elif mean_satisfaction == 1:
            satisfaction = "Not satisfied at all"
        else:
            satisfaction = "No data"
    else:
        satisfaction = "No data"

    return satisfaction


def eq5d(data, admission_this_month):
    """Gets the percentage of completeness of preqols"""
    if pd.Series(['preQol.mobility', 'preQol.selfCare', 'preQol.usual_activities', 'preQol.pain_discomfort',
                  'preQol.anxiety_depression']).isin(data.columns).all():
        data = data.dropna(subset=['preQol.mobility', 'preQol.selfCare', 'preQol.usual_activities',
                                   'preQol.pain_discomfort', 'preQol.anxiety_depression'])
        score = len(data.index) / admission_this_month * 100
        score = round(score, 1)
    else:
        score = 'No data'

    return score


def pain_score(data):
    """Gets the percentage of patients who get pain information entered for each daily assessment"""
    if len(data) > 0 and 'pain' in data:
        data = data[['patient_id', 'pain']]
        mean_pain_per_patient = data.groupby("patient_id").apply(lambda x: x.notnull().mean())
        per = list(mean_pain_per_patient['pain']).count(1)
        score = per / len(mean_pain_per_patient.index) * 100
        score = round(score, 1)
    else:
        score = 'No data'

    return score


def apache_score(data):
    """Gets mean and standard deviation for apache score filtered by admission type"""
    if pd.Series(['admission.admission_type', 'admissionAssessment.apache_score']).isin(
            data.columns).all():
        planned_admission_data = data.loc[data['admission.admission_type'] == 'Planned']
        unplanned_admission_data = data.loc[data['admission.admission_type'] == 'Unplanned']
        apache_scores_planned = pd.to_numeric(planned_admission_data['admissionAssessment.apache_score'],
                                              errors='coerce')
        apache_scores_unplanned = pd.to_numeric(unplanned_admission_data['admissionAssessment.apache_score'],
                                                errors='coerce')
        mean_apache_score_planned = round(apache_scores_planned.mean(), 1)
        mean_apache_score_unplanned = round(apache_scores_unplanned.mean(), 1)
        std_apache_score_planned = round(apache_scores_planned.std(ddof=0), 1)
        std_apache_score_unplanned = round(apache_scores_unplanned.std(ddof=0), 1)
        if math.isnan(mean_apache_score_planned):
            mean_apache_score_planned = 'No data'
            std_apache_score_planned = 'No data'
        if math.isnan(mean_apache_score_unplanned):
            mean_apache_score_unplanned = 'No data'
            std_apache_score_unplanned = 'No data'
    else:
        mean_apache_score_planned = 'No data'
        std_apache_score_planned = 'No data'
        mean_apache_score_unplanned = 'No data'
        std_apache_score_unplanned = 'No data'

    return {'APACHE_planned': mean_apache_score_planned, 'APACHE_unplanned': mean_apache_score_unplanned,
            'stand_planned': std_apache_score_planned, 'stand_unplanned': std_apache_score_unplanned}


def pims_score(admission_data):
    requird_columns = ['admissionAssessment.pupil_size',
                       'admissionAssessment.light_reaction',
                       'admissionAssessment.mechanically_ventilated',
                       'admission.admission_type',
                       'admission.diagnosis_type',
                       'admission.bypass',
                       'admission.apache_diagnosis',
                       'admission.apache_diagnosis2',
                       'comorbid_conditions',
                       'comorbid_conditions2',
                       'comorbid_conditions3',
                       'comorbid_conditions4']

    if all(i in admission_data for i in requird_columns):

        apache_diagnosis_HRdiag = ["Cardiac arrest (with or without respiratory arrest; for respiratory arrest)",
                                   "Severe Combined Immunodeficiency (SCID)",
                                   "Leukemia, acute lymphocytic",
                                   "Leukemia, chronic lymphocytic",
                                   "Hemorrhage (for gastrointestinal bleeding)",
                                   "Cardiomyopathy",
                                   "Cardiomyopathy",
                                   "Myocarditis",
                                   "Neurodegenerative Disorder",
                                   "Hepatic failure, acute",
                                   "Hepatic failure, acute which is  associated with suspected or confirmed pandemic infection"]

        apache_diagnoisis_LRdiag = ["Asthma",
                                    "Bronchiolitis",
                                    "Croup",
                                    "Apnea, sleep",
                                    "Diabetic ketoacidosis"]

        admission_data['pupils'] = 0
        admission_data['mechVent'] = 0
        admission_data['elective'] = 0
        admission_data['recovery'] = 0
        admission_data['bypass'] = 0
        admission_data['HRdiag'] = 0
        admission_data['LRdiag'] = 0

        admission_data.loc[(admission_data['admissionAssessment.pupil_size'] == 'Yes' &
                            admission_data['admissionAssessment.light_reaction'] == 'Yes (both)'), 'pupils'] = 1
        admission_data.loc[
            (admission_data['admissionAssessment.mechanically_ventilated'] == 'Mechanical vent'), 'mechVent'] = 1
        admission_data.loc[(admission_data['admission.admission_type'] == 'Planned'), 'elective'] = 1
        admission_data.loc[(admission_data['admission.diagnosis_type'] == 'Post operative'), 'recovery'] = 1
        admission_data.loc[(admission_data['admission.bypass'] == 'Yes'), 'bypass'] = 1

        admission_data.loc[(admission_data['admission.apache_diagnosis'].isin(apache_diagnosis_HRdiag) |
                            admission_data['admission.apache_diagnosis2'].isin(apache_diagnosis_HRdiag) |
                            admission_data['comorbid_conditions'] == 'HIV' |
                            admission_data['comorbid_conditions2'] == 'HIV' |
                            admission_data['comorbid_conditions3'] == 'HIV' |
                            admission_data['comorbid_conditions4'] == 'HIV'), 'HRdiag'] = 1

        admission_data.loc[(admission_data['admission.apache_diagnosis'].isin(apache_diagnoisis_LRdiag) |
                            admission_data['admission.apache_diagnosis2'].isin(apache_diagnoisis_LRdiag)), 'LRdiag'] = 1

        admission_data['pims2'] = (0.01395 * (
            (admission_data['admissionAssessment.systolic_blood_pressure'] - 120).abs())) \
                                  + (3.0791 * admission_data['pupils']) \
                                  + (0.2888 * (
                100 * admission_data['admissionAssessment.fraction_inspired_oxygen'] / admission_data[
            'admissionAssessment.partial_pressure_arterial_oxygen'])) \
                                  + (0.1040 * (admission_data['admissionAssessment.be']).abs()) \
                                  + (1.3352 * admission_data['mechVent']) \
                                  - (0.9282 * admission_data['elective']) \
                                  - (1.0244 * admission_data['recovery']) \
                                  + (0.7507 * admission_data['bypass']) \
                                  + (1.6829 * admission_data['HRdiag']) \
                                  - (1.5770 * admission_data['LRdiag']) - 4.8841

        planned_admission_data = admission_data.loc[admission_data['admission.admission_type'] == 'Planned']
        planned_pim_score = planned_admission_data['pims2']
        mean_pims_score_planned = round(planned_pim_score.mean(), 1)
        std_pims_score_planned = round(planned_pim_score.std(ddof=0), 1)
        unplanned_admission_data = admission_data.loc[admission_data['admission.admission_type'] == 'Unplanned']
        unplanned_pim_score = unplanned_admission_data['pims2']
        mean_pims_score_unplanned = round(unplanned_pim_score.mean(), 1)
        std_pims_score_unplanned = round(unplanned_pim_score.std(ddof=0), 1)

        if math.isnan(mean_pims_score_planned):
            mean_pims_score_planned = 'No data'
            std_pims_score_planned = 'No data'

        if math.isnan(mean_pims_score_unplanned):
            mean_pims_score_unplanned = 'No data'
            std_pims_score_unplanned = 'No data'

    else:
        mean_pims_score_planned = 'No data'
        std_pims_score_planned = 'No data'
        mean_pims_score_unplanned = 'No data'
        std_pims_score_unplanned = 'No data'

    return {mean_pims_score_planned: mean_pims_score_planned,
            std_pims_score_planned: std_pims_score_planned,
            mean_pims_score_unplanned: mean_pims_score_unplanned,
            std_pims_score_unplanned: std_pims_score_unplanned}


def mec_vent_by_month(data, start_date=None, end_date=None):
    if 'admission.date_of_admission' in data and 'admissionAssessment.mechanically_ventilated' in data:
        data = data.dropna(subset=['admission.date_of_admission', 'admissionAssessment.mechanically_ventilated'])
        if len(data) > 0:
            data.loc[:, 'date_of_admission'] = pd.to_datetime(data['admission.date_of_admission'], format='%Y-%m-%d')

            if start_date and end_date:
                # convert date input to the correct string format '%m/%d/%y'
                start_date = datetime.strptime(start_date, '%d/%m/%Y')
                end_date = datetime.strptime(end_date, '%d/%m/%Y')
                date_range = relativedelta.relativedelta(end_date, start_date)

                if (date_range.months + (12 * date_range.years)) < 1:
                    start_date = start_date - relativedelta.relativedelta(months=1)

                start_date_str = start_date.strftime('%m/%d/%Y')
                end_date_str = end_date.strftime('%m/%d/%Y')

            else:
                # if no start and end date then use max and min dates
                start_date = data['date_of_admission'].min()
                end_date = data['date_of_admission'].max()
                date_range = relativedelta.relativedelta(end_date, start_date)

                if (date_range.months + (12 * date_range.years)) < 1:
                    start_date = start_date - relativedelta.relativedelta(months=1)

                start_date_str = start_date.strftime('%m/%d/%Y')
                end_date_str = end_date.strftime('%m/%d/%Y')

            data.loc[:, 'date_of_admission'] = data['date_of_admission'].dt.strftime('%m/%Y')
            data.loc[:, 'mechanically_ventilated'] = data['admissionAssessment.mechanically_ventilated'].replace(
                ['mechanical_vent', 'self_vent'],
                ['Mechanical vent', 'Self vent'])
            grouped_data = data.pivot_table(values='num', index='date_of_admission', columns='mechanically_ventilated',
                                            aggfunc='sum')
            grouped_data.fillna(0, inplace=True)
            idx = pd.date_range(start_date_str, end_date_str, freq='MS')
            grouped_data.index = pd.DatetimeIndex(grouped_data.index)
            grouped_data = grouped_data.reindex(idx, fill_value=0)
            grouped_data = grouped_data.reset_index().rename(columns={'index': 'date_of_admission'})
            grouped_data['date_of_admission'] = grouped_data['date_of_admission'].dt.strftime('%m/%Y')
            grouped_data = grouped_data.to_json(orient='records', date_format='iso', date_unit='s')
        else:
            grouped_data = "No data"
    else:
        grouped_data = "No data"

    return grouped_data


def mean_days_mechanically_ventilated(admission_data, daily_assessment_data):
    if 'admissionAssessment.mechanically_ventilated' in admission_data and 'mechanically_ventilated' in daily_assessment_data:
        admission_data = admission_data.rename(
            columns={'admissionAssessment.mechanically_ventilated': 'mechanically_ventilated'})
        data = pd.concat([admission_data, daily_assessment_data], ignore_index=True)
        days_mechanically_ventilated = (list(data['mechanically_ventilated']).count("mechanical_vent")) / data[
            'patient_id'].nunique()
        days_mechanically_ventilated = round(days_mechanically_ventilated, 1)

    elif 'admissionAssessment.mechanically_ventilated' in admission_data:
        days_mechanically_ventilated = (list(admission_data['admissionAssessment.mechanically_ventilated']).count(
            "mechanical_vent")) / \
                                       admission_data['patient_id'].nunique()
        days_mechanically_ventilated = round(days_mechanically_ventilated, 1)

    elif 'mechanically_ventilated' in daily_assessment_data:
        days_mechanically_ventilated = (list(daily_assessment_data['mechanically_ventilated']).count(
            "mechanical_vent")) / daily_assessment_data[
                                           'patient_id'].nunique()
        days_mechanically_ventilated = round(days_mechanically_ventilated, 1)

    else:
        days_mechanically_ventilated = "No data"

    return days_mechanically_ventilated


def count_mechanically_ventilated(data, admission_type=None):
    """Counts the percentage of patients on admission that got mechanically ventilated"""
    if pd.Series(['admissionAssessment.mechanically_ventilated', 'admission.admission_type']).isin(
            data.columns).all():
        data = filter_by_admission_type(data, admission_type)
        admission_this_month = len(data)
        if admission_this_month > 0:
            yes = list(data['admissionAssessment.mechanically_ventilated']).count("mechanical_vent")
            per = yes / admission_this_month * 100
            per = round(per, 1)
        else:
            yes = "No data"
            per = "No data"
    else:
        yes = "No data"
        per = "No data"

    return {'count': yes, 'per': per}


def time_on_antibiotics(data_on_admission, daily_assessment_data):
    if 'admissionAssessment.antibiotics' in data_on_admission and 'antibiotics' in daily_assessment_data:
        data_daily_s = daily_assessment_data[['patient_id', 'antibiotics']]
        data_on_admission_s = data_on_admission[['patient_id', 'admissionAssessment.antibiotics']]
        data_on_admission_s = data_on_admission_s.rename(columns={'admissionAssessment.antibiotics': 'antibiotics'})
        data = pd.concat([data_on_admission_s, data_daily_s], ignore_index=True)
        time = (list(data['antibiotics']).count("Yes")) / data['patient_id'].nunique()
        time = round(time, 1)

    elif 'admissionAssessment.antibiotics' in data_on_admission:
        time = (list(data_on_admission['admissionAssessment.antibiotics']).count("Yes")) / data_on_admission[
            'patient_id'].nunique()
        time = round(time, 1)

    elif 'antibiotics' in daily_assessment_data:
        time = (list(daily_assessment_data['antibiotics']).count("Yes")) / daily_assessment_data['patient_id'].nunique()
        time = round(time, 1)

    else:
        time = "No data"

    return time


def use_of_antibiotics(data, admission_this_month):
    """Counts the percentage of patients on admission that toke antibiotics"""
    if 'admissionAssessment.antibiotics' in data:
        yes = list(data['admissionAssessment.antibiotics']).count("Yes")
        no = yes - admission_this_month
        per_yes = round((yes / admission_this_month) * 100, 1)
        per_no = 100 - per_yes
    else:
        yes = "No data"
        no = "No data"
        per_yes = "No data"
        per_no = "No data"

    return {'count_yes': yes, 'per_yes': per_yes, 'count_no': no, 'per_no': per_no}


def cardiovascular_support_stats(data, admission_type=None):
    if 'admissionAssessment.cardiovascular_support' in data:
        data = filter_by_admission_type(data, admission_type)
        cardio_data = list(data['admissionAssessment.cardiovascular_support'].dropna().astype(str))
        patients = len(cardio_data)
        if patients > 0:
            count_yes = cardio_data.count("Yes")
            per_yes = round(count_yes / patients * 100, 1)
            count_no = patients - count_yes
            per_no = 100 - per_yes
        else:
            per_yes = "No data"
            count_yes = 'No data'
            count_no = 'No data'
            per_no = 'No data'
    else:
        per_yes = "No data"
        count_yes = 'No data'
        count_no = 'No data'
        per_no = 'No data'

    return {'per_yes': per_yes, 'count_yes': count_yes, 'count_no': count_no, 'per_no': per_no}


def admission_type_by_month(data, start_date=None, end_date=None):
    if 'admission.date_of_admission' in data and 'admission.admission_type' in data:
        data = data.dropna(subset=['admission.date_of_admission', 'admission.admission_type'])
        if len(data) > 0:
            data.loc[:, 'date_of_admission'] = pd.to_datetime(data['admission.date_of_admission'], format='%Y-%m-%d')

            if start_date and end_date:
                # convert date input to the correct string format '%m/%d/%y'
                start_date = datetime.strptime(start_date, '%d/%m/%Y')
                end_date = datetime.strptime(end_date, '%d/%m/%Y')
                date_range = relativedelta.relativedelta(end_date, start_date)

                if (date_range.months + (12 * date_range.years)) < 1:
                    start_date = start_date - relativedelta.relativedelta(months=1)

                start_date_str = start_date.strftime('%m/%d/%Y')
                end_date_str = end_date.strftime('%m/%d/%Y')

            else:
                # if no start and end date then use max and min dates
                start_date = data['date_of_admission'].min()
                end_date = data['date_of_admission'].max()
                date_range = relativedelta.relativedelta(end_date, start_date)

                if (date_range.months + (12 * date_range.years)) < 1:
                    start_date = start_date - relativedelta.relativedelta(months=1)

                start_date_str = start_date.strftime('%m/%d/%Y')
                end_date_str = end_date.strftime('%m/%d/%Y')

            data.loc[:, 'date_of_admission'] = data['date_of_admission'].dt.strftime('%m/%Y')
            data = data.reset_index()
            grouped_data = data.pivot_table(values='num', index='date_of_admission', columns='admission.admission_type',
                                            aggfunc='sum')
            grouped_data.fillna(0, inplace=True)
            idx = pd.date_range(start_date_str, end_date_str, freq='MS')
            grouped_data.index = pd.DatetimeIndex(grouped_data.index)
            grouped_data = grouped_data.reindex(idx, fill_value=0)
            grouped_data = grouped_data.reset_index().rename(columns={'index': 'date_of_admission'})
            grouped_data.loc[:, 'date_of_admission'] = grouped_data['date_of_admission'].dt.strftime('%m/%Y')
            grouped_data = grouped_data.to_json(orient='records', date_format='iso', date_unit='s')
        else:
            grouped_data = "No data"
    else:
        grouped_data = "No data"

    return grouped_data


def admission_type(data, number_of_admissions):
    """Returns the number ratio between Planned and Unplanned admissions"""
    if 'admission.admission_type' in data and data['admission.admission_type'].astype(str).str.contains(
            'Unplanned|Planned').any():
        number_planned = list(data['admission.admission_type']).count('Planned')
        number_unplanned = list(data['admission.admission_type']).count('Unplanned')
        per_planned = round(number_planned / number_of_admissions * 100)
        per_unplanned = round(number_unplanned / number_of_admissions * 100)

    else:
        number_planned = 'No data'
        number_unplanned = 'No data'
        per_planned = 'No data'
        per_unplanned = 'No data'

    return {'number_planned': number_planned, 'number_unplanned': number_unplanned,
            'percentage_planned': per_planned, 'percentage_unplanned': per_unplanned}


def admission_type_ratio(data):
    """Returns the number ratio between Planned and Unplanned admissions"""
    if 'admission.admission_type' in data and data['admission.admission_type'].astype(str).str.contains(
            'Unplanned|Planned').any():
        number_planned = list(data['admission.admission_type']).count('Planned')
        number_unplanned = list(data['admission.admission_type']).count('Unplanned')
        if number_planned == 0 or number_unplanned == 0:
            ratio_admission_type = {'planned': number_planned, 'unplanned': number_unplanned}
        elif number_planned > number_unplanned:
            planned_ratio = round(number_planned / number_unplanned)
            ratio_admission_type = {'planned': planned_ratio, 'unplanned': 1}
        else:
            unplanned_ratio = round(number_unplanned / number_planned)
            ratio_admission_type = {'planned': 1, 'unplanned': unplanned_ratio}
    else:
        ratio_admission_type = {'planned': 'No data', 'unplanned': 'No data'}

    return ratio_admission_type


def sbt(daily_data):
    if 'sbt' in daily_data and 'mechanically_ventilated' in daily_data:
        mec_vent_data = daily_data.loc[daily_data['mechanically_ventilated'] == 'mechanical_vent']
        mec_vent_patients = len(mec_vent_data)
        if mec_vent_patients > 0:
            sbt_patients = len(mec_vent_data.loc[mec_vent_data['sbt'] == 'Yes'])
            sbt_per = round((sbt_patients / mec_vent_patients) * 100, 1)
        else:
            sbt_patients = 'No data'
            sbt_per = 'No data'
    else:
        sbt_patients = 'No data'
        sbt_per = 'No data'

    return {'count': sbt_patients, 'per': sbt_per}


def cardiac_arrest(admission_data):
    number_patients = len(admission_data)
    if 'admission.apache_diagnosis' in admission_data and number_patients > 0:

        cardiac_arrest_count = int(len(admission_data.loc[
                                           admission_data['admission.apache_diagnosis'].astype(str).str.contains(
                                               'Cardiac arrest')]))
        per = round((cardiac_arrest_count / number_patients) * 100, 1)

        return {'count': cardiac_arrest_count, 'per': per}

    else:
        return {'count': 'No data', 'per': 'No data'}


def renal_replacement(daily_data, admissionType=None):
    daily_assessments = len(daily_data)
    if 'renal_replacement' in daily_data and daily_assessments > 0:

        daily_data = filter_by_admission_type(daily_data, admissionType)
        count = len(daily_data.loc[daily_data['renal_replacement'] == 'Yes'])
        per = (count / daily_assessments) * 100

    else:
        per = 'No data'
        count = 'No data'

    return {'count': count, 'per': per}


def blood_culture(daily_data):
    number_daily_assessments = len(daily_data)
    if 'culture' in daily_data and number_daily_assessments > 0:
        blood_culture_count = len(daily_data.loc[daily_data['culture'] == 'Blood'])
        per_blood_culture = round((blood_culture_count / number_daily_assessments) * 100, 1)

        return {'count': blood_culture_count, 'per': per_blood_culture}

    else:
        return {'count': 'No data', 'per': 'No data'}


def urine_culture(daily_data):
    number_daily_assessments = len(daily_data)
    if 'culture' in daily_data and number_daily_assessments > 0:
        urine_culture_count = len(daily_data.loc[daily_data['culture'] == 'Urine'])
        per_urine_culture = round((urine_culture_count / number_daily_assessments) * 100, 1)

        return {'count': urine_culture_count, 'per': per_urine_culture}

    else:
        return {'count': 'No data', 'per': 'No data'}


def csf_culture(daily_data):
    number_daily_assessments = len(daily_data)
    if 'culture' in daily_data and number_daily_assessments > 0:
        csf_culture_count = len(daily_data.loc[daily_data['culture'] == 'csf'])
        per_csf_culture = round((csf_culture_count / number_daily_assessments) * 100, 1)

        return {'count': csf_culture_count, 'per': per_csf_culture}

    else:
        return {'count': 'No data', 'per': 'No data'}


def bed_occupancy_custom_range(admission_this_month, los, beds, date):
    # Check that all inputs are of a numeric type
    if all(isinstance(i, (int, float, np.float64)) for i in [beds, los, admission_this_month]) and beds > 0:
        dates = date.split(' - ')
        dates = [datetime.strptime(d, '%d/%m/%Y') for d in dates]
        date_range = (dates[1] - dates[0]).days
        a = admission_this_month * los * 100
        b = beds * date_range
        bed_occupancy_per = round(a / b)
    else:
        bed_occupancy_per = 'No data'

    return bed_occupancy_per


def number_of_admissions(data):
    """give you the length of DataFrame"""
    if isinstance(data, pd.DataFrame):
        patients = len(data)
    else:
        patients = 0

    return patients


def top_ten_diagnosis_on_admission(data, exclusion_list=['']):
    if 'admission.apache_diagnosis' in data:
        data = data.dropna(subset=['admission.apache_diagnosis'])
        if len(data) > 0:
            admission_groups = pd.read_csv('app/systeam_diagnosis_joined.csv')
            # data['admission.system'] = data['admission.system'].str.lower()
            # data['admission.apache_diagnosis'] = data['admission.apache_diagnosis'].str.lower()
            # data['admission.diagnosis_type'] = data['admission.diagnosis_type'].str.lower()

            data = data.merge(admission_groups,
                              left_on=['admission.system', 'admission.apache_diagnosis', 'admission.diagnosis_type'],
                              right_on=['system', 'diagnosis_on_admission', 'diagnosis_type'])

            data = data.reset_index()
            try:
                data['admission_group'] = data['admission_group'].astype(str).str.replace('/', ' ')
            except:
                x = 'x'
            data = data.loc[~data['admission_group'].isin(exclusion_list)]
            grouped_data = data.groupby('admission_group')['num'].sum()
            grouped_data.fillna(0, inplace=True)
            grouped_data_key = grouped_data.nlargest(10).keys()

            grouped_data = grouped_data[grouped_data_key]
            grouped_data = grouped_data.reset_index().to_json(orient='records')
        else:
            grouped_data = "No data"
    else:
        grouped_data = "No data"

    return grouped_data


def length_of_stay(data, admission_type=None):
    """Returns the average length of stay by converting strings to datetime objects and subtracting admission and
    and discharge dates and returning it in days (IT IGNORES NA VALUES)"""

    admission_column = 'admission.date_of_admission'
    if admission_column not in data:
        admission_column = 'admission.date_of_admission_hospital'

    if all(i in data for i in
           ['discharge.date_of_discharge', admission_column, 'admission.admission_type']):
        data = filter_by_admission_type(data, admission_type)
        if len(data) > 0:
            data[['discharge.date_of_discharge', admission_column]] = data[
                ['discharge.date_of_discharge', admission_column]].apply(pd.to_datetime, format='%Y-%m-%d',
                                                                         errors='coerce')
            data = data[pd.notnull(data['discharge.date_of_discharge'])]
            if len(data) > 0:
                list_of_stay = (data['discharge.date_of_discharge'] - data[admission_column]).dt.days
                mean_stay = list_of_stay.mean()
                mean_stay = round(mean_stay, 1)
            else:
                mean_stay = "No data"
        else:
            mean_stay = "No data"

    else:
        mean_stay = "No data"

    return mean_stay


def filter_by_admission_type(data, admission_type):
    if admission_type:
        data = data.loc[data['admission.admission_type'] == admission_type]
    return data


def n_per_join(n, per):
    label = f'{n} ({per}%)'
    return label


def top_ten_blood_cultures(investigation_data):
    if 'organism' in investigation_data:
        investigation_data = investigation_data.dropna(subset=['organism'])
        if len(investigation_data) > 0:

            investigation_data = investigation_data.reset_index()
            investigation_data['organism'] = investigation_data['organism'].str.upper()
            grouped_data = investigation_data.groupby('organism')['patient_id'].count()
            # grouped_data.rename(columns={'organism': 'num'}, inplace=True)
            grouped_data.fillna(0, inplace=True)
            grouped_data_key = grouped_data.nlargest(10).keys()
            grouped_data = grouped_data[grouped_data_key]
            grouped_data = grouped_data.reset_index()
            grouped_data = grouped_data.to_json(orient='records')
        else:
            grouped_data = "No data"
    else:
        grouped_data = "No data"

    return grouped_data


def stress_ulcer_for_patient(daily_data):
    stress_ulcer_count = 0
    daily_data = daily_data.reset_index(drop=True)

    while len(daily_data) > 2:
        mask = daily_data.loc[daily_data['mechanically_ventilated'] == 'mechanical_vent']

        try:
            idx = mask.index[0]
        except:
            break
        # idx = next(iter(mask.index[mask]), 'not exist')

        # if idx == 'not exist':
        #     break

        first_date_mec_vent_datetime = daily_data.loc[idx]['date_of_daily_assessment']
        first_date_mec_vent_datetime = datetime.strptime(first_date_mec_vent_datetime, "%Y-%m-%d")
        second_date_mec_vent = str(first_date_mec_vent_datetime + timedelta(days=1))[:10]

        if len(daily_data.loc[
                   (daily_data['date_of_daily_assessment'] == second_date_mec_vent) &
                   (daily_data['mechanically_ventilated'] == 'mechanical_vent') &
                   (daily_data['stress_ulcer_prophylaxis'] == 'Yes')
               ]) > 0:
            stress_ulcer_count += 1

        mask = daily_data['mechanically_ventilated'] == 'self_vent'
        idx = next(iter(mask.index[mask]), 'not exist')

        if idx == 'not exist':
            break

        daily_data = daily_data.loc[idx + 1:]

    return stress_ulcer_count


def stress_ulcer_rate_for_dataset(daily_data):
    if 'mechanically_ventilated' in daily_data:

        mec_vent_patients = daily_data.loc[daily_data['mechanically_ventilated'] == 'mechanical_vent']
        mec_vent_patients_count = len(mec_vent_patients)
        if mec_vent_patients_count > 0:
            stress_ulcer_count = daily_data.groupby('patient_id').apply(
                stress_ulcer_for_patient).sum()
            return {'count': int(stress_ulcer_count),
                    'per': round((stress_ulcer_count / mec_vent_patients_count) * 100, 1)}
        else:
            return {'count': 'No data', 'per': 'No data'}
    else:
        return {'count': 'No data', 'per': 'No data'}


def unnplanned_reintubain(daily_data):
    if 'unplanned_extubation' in daily_data:
        data_mec_vent = daily_data[daily_data['mechanically_ventilated'] == 'mechanical_vent']
        count_mec_vent = len(data_mec_vent)
        if count_mec_vent > 0:
            count_unplanned_reintubain = len(data_mec_vent.loc[data_mec_vent['unplanned_extubation'] == 'Yes'])
            return {'count': int(count_unplanned_reintubain),
                    'per': round((count_unplanned_reintubain / count_mec_vent) * 100, 1)}
        else:
            return {'count': 'No data', 'per': 'No data'}
    else:
        return {'count': 'No data', 'per': 'No data'}


def venuos_thromboemboliasm_for_patient(daily_data):
    if len(daily_data) > 1:
        admission_date = daily_data['admission_date'].iloc[0]
        admission_date = datetime.strptime(admission_date, "%Y-%m-%d")
        daily_assessment_day_2 = str(admission_date + timedelta(days=1))[:10]

        if len(daily_data.loc[(daily_data['date_of_daily_assessment'] == daily_assessment_day_2) & (
                daily_data['vte_prophylaxis'].isin(['Mechanical', 'Pharmacological']))]) > 0:
            return 1
        else:
            return 0

    else:
        return 0


def venuos_thromboemboliasm(daily_data):
    if pd.Series(['admission_date', 'date_of_daily_assessment', 'mechanically_ventilated', 'contraindication']).isin(
            daily_data.columns).all():

        daily_data = daily_data.dropna(subset=['admission_date', 'date_of_daily_assessment'])
        mec_vent_patients = daily_data.loc[
            (daily_data['mechanically_ventilated'] == 'mechanical_vent') & (daily_data['contraindication'].isnull())]
        # exclude patients with contra
        number_patients = len(mec_vent_patients)
        if number_patients > 0:
            venuos_thromboemboliasm_count = daily_data.groupby('patient_id').apply(
                venuos_thromboemboliasm_for_patient).sum()
            per = round((venuos_thromboemboliasm_count / number_patients) * 100, 1)
            return {'count': int(venuos_thromboemboliasm_count), 'per': per}
        else:
            return {'count': 'No data', 'per': 'No data'}
    else:
        return {'count': 'No data', 'per': 'No data'}


def for_discharge_cols_fill_if_not_discharged(data):
    discharge_form_variables = [col for col in data if col.startswith('discharge_')]
    data.loc[(data['dischargeStatus'] != 'true'), discharge_form_variables] = 'filled'
    return data


def for_sariAdmission_cols_fill_if_not_sari(data):
    sariAdmissionAssessment_variables = [col for col in data if col.startswith('sari_admission_assessment')]
    data.loc[((data['admission_sari'] != 'Confirmed') & (
            data['admission_sari'] != 'Suspected')), sariAdmissionAssessment_variables] = 'filled'
    return data


def for_sariDischarge_cols_fill_if_not_sari(data):
    sariPreDischarge_variables = [col for col in data if col.startswith('sari_pre_discharge')]
    data.loc[((data['dischargeStatus'] != 'true') | (data['admission_sari'] != 'Confirmed') & (
            data['admission_sari'] != 'Suspected')), sariPreDischarge_variables] = 'filled'
    return data


def get_qi_completeness(admission_data, daily_assessment, investigation_data):
    """Get completeness of dataset"""
    if pd.Series(['investigation_white_blood_cells', 'investigation_culture', 'investigation_organism',
                  'investigation_coliform']).isin(investigation_data.columns).all() and pd.Series(
        ['admission_date_of_admission_hospital', 'admission_time_of_admission_hospital',
         'admission_date_of_admission', 'admission_time_of_admission', 'admission_readmission',
         'admission_date_of_pre_discharge', 'admission_admission_type',
         'admission_assessment_mechanically_ventilated', 'admission_assessment_antibiotics']).isin(
        admission_data.columns).all():
        admission_data = admission_data[['admission_date_of_admission_hospital', 'admission_time_of_admission_hospital',
                                         'admission_date_of_admission', 'admission_time_of_admission',
                                         'admission_readmission', 'admission_date_of_pre_discharge',
                                         'admission_admission_type', 'admission_assessment_mechanically_ventilated',
                                         'admission_assessment_antibiotics']]
        investigation_data = investigation_data[
            ['investigation_white_blood_cells', 'investigation_culture', 'investigation_organism',
             'investigation_coliform']]
        completeness_filled_total = [get_completeness_for_dataset(admission_data),
                                     get_completeness_for_dataset(daily_assessment),
                                     get_completeness_for_dataset(investigation_data)]

        # sum number of entries and Nan for all core forms
        total_entries = sum(form['total_number_of_entries'] for form in completeness_filled_total)
        filled_entries = sum(form['number_of_entries_filled'] for form in completeness_filled_total)

        if total_entries > 0:
            completeness = round((filled_entries / total_entries) * 100, 1)
        else:
            completeness = 'No data'

    else:
        completeness = 'No data'

    return completeness


def get_daily_assessment_form_completeness(data):
    if 'discharge_date_of_discharge' in data and 'admission_date_of_admission' in data:
        # drop patients with missing admission or discharge data
        data = data.dropna(subset=['discharge_date_of_discharge', 'admission_date_of_admission'])

        # Check if there are any patents
        if len(data) > 0:

            # convert admission and discharge dates to datetime if wrong format return NaN
            data[['discharge_date_of_discharge', 'admission_date_of_admission']] = data[
                ['discharge_date_of_discharge', 'admission_date_of_admission']].apply(pd.to_datetime, format='%Y-%m-%d',
                                                                                      errors='coerce')
            # Drop patients with wrongly formatted dates
            data = (data[data[['discharge_date_of_discharge', 'admission_date_of_admission']].notnull().all(1)])

            # Get number of days between admission and discharge dates
            data['los'] = (data['discharge_date_of_discharge'] - data['admission_date_of_admission']).dt.days

            # Get number of eligible patients
            eligible_patients = len(data)

            # get number of patients all there daily assessment forms are filled
            patients_form_filled = len(data[data['dailyAssessments'].map(len) == (data['los'])])

            # get per filled
            if eligible_patients > 0:
                qi_comp = round((patients_form_filled / eligible_patients) * 100, 1)

            else:
                qi_comp = 'No data'

        else:
            qi_comp = 'No data'

    else:
        qi_comp = 'No data'

    return qi_comp


def get_core_variables(data_dict):
    core_admission_cols = []
    core_daily_assessment_cols = []
    core_investigation_cols = []
    core_other_cols = []

    # drop rows without validation (if the column is core it would have validations)
    data_dict = data_dict.dropna(subset=['validation'])
    # convert data frame to dict so we can loop through it
    data_dict = data_dict.to_dict('records')

    # loop through data dict
    for x in data_dict:
        # get list of validation for current columns
        validations = x['validation']
        number_validations = len(validations)

        # if there are validations
        if number_validations > 0:

            # check if current column is core
            if validations[0]['method'] == 'required':

                # check which form this variable is filled in and append to correct list
                form_name = x['form']

                core_forms = ['admission',
                              'admission_assessment',
                              'discharge',
                              'sari_admission_assessment',
                              'sari_pre_discharge']

                if form_name in core_forms:
                    core_admission_cols.append(x['key'])

                elif form_name == 'daily_assessment':
                    core_daily_assessment_cols.append(x['key'])

                elif form_name == 'investigation':
                    core_investigation_cols.append(x['key'])

                else:
                    core_other_cols.append(x['key'])

    required_cols = {'required_admission_cols': core_admission_cols,
                     'required_daily_assessment_cols': core_daily_assessment_cols,
                     'required_investigations_cols': core_investigation_cols,
                     'required_other_cols': core_other_cols}

    return required_cols


def get_all_variables_from_data_dict(data_dict):
    core_forms_variables = []
    daily_assessment_variables = []
    investigation_variables = []
    sari_daily_assessment_variables = []
    sari_admission_variables = []
    sari_discharge_variables = []
    other_variables = []

    # convert data frame to dict so we can loop through it
    data_dict = data_dict.to_dict('records')

    # loop through data dict
    for x in data_dict:

        # check which form this variable is filled in and append to correct list
        form_name = x['form']

        core_forms = ['admission',
                      'admission_assessment',
                      'discharge']

        if form_name in core_forms:
            core_forms_variables.append(x['key'])

        elif form_name == 'daily_assessment':
            daily_assessment_variables.append(x['key'])

        elif form_name == 'investigation':
            investigation_variables.append(x['key'])

        elif form_name == 'sari_admission_assessment':
            sari_admission_variables.append(x['key'])

        elif form_name == 'sari_pre_discharge':
            sari_discharge_variables.append(x['key'])

        elif form_name == 'sari_daily_assessment':
            sari_daily_assessment_variables.append(x['key'])

        else:
            other_variables.append(x['key'])

        number_above_one = ('2', '3', '4', '5', '6', '7')

        core_forms_variables_cleaned = []
        daily_assessment_variables_cleaned = []
        investigation_variables_cleaned = []
        sari_daily_assessment_variables_cleaned = []
        sari_admission_variables_cleaned = []
        sari_discharge_variables_cleaned = []

        # remove possible duplicates and variables ending in 2 or above.
        # This is becasue when I looked at the data dict pcr apears mulitple times.
        [core_forms_variables_cleaned.append(x) for x in core_forms_variables if
         not x.endswith(number_above_one) and x not in core_forms_variables_cleaned]
        [daily_assessment_variables_cleaned.append(x) for x in daily_assessment_variables if
         not x.endswith(number_above_one) and x not in daily_assessment_variables_cleaned]
        [investigation_variables_cleaned.append(x) for x in investigation_variables if
         not x.endswith(number_above_one) and x not in investigation_variables_cleaned]
        [sari_daily_assessment_variables_cleaned.append(x) for x in sari_daily_assessment_variables if
         not x.endswith(number_above_one) and x not in sari_daily_assessment_variables_cleaned]
        [sari_admission_variables_cleaned.append(x) for x in sari_admission_variables if
         not x.endswith(number_above_one) and x not in sari_admission_variables_cleaned]
        [sari_discharge_variables_cleaned.append(x) for x in sari_discharge_variables if
         not x.endswith(number_above_one) and x not in sari_discharge_variables_cleaned]

        required_cols = {'core_forms_variables': core_forms_variables_cleaned,
                         'daily_assessment_variables': daily_assessment_variables_cleaned,
                         'investigation_variables': investigation_variables_cleaned,
                         'sari_daily_assessment_variables': sari_daily_assessment_variables_cleaned,
                         'sari_admission_variables': sari_admission_variables_cleaned,
                         'sari_discharge_variables': sari_discharge_variables_cleaned,
                         'other_variables': other_variables}

        return required_cols


def get_completeness_for_dataset(data):
    """Return the number of Nan entries and total entries after excludding the values based on branching logic"""
    number_filled_by_branching_logic = data.eq('filled').sum().sum()
    number_of_entries_filled = np.sum(data.count()) - number_filled_by_branching_logic
    total_number_of_entries = data.isna().sum().sum() + number_of_entries_filled
    return {'number_of_entries_filled': number_of_entries_filled,
            'total_number_of_entries': total_number_of_entries}


def get_completeness_core_data(admissionData, core_cols):
    """Get the completeness of core dataset by filtering admission, daily assessment and investigation data with
    core_col input sum the total entries and Nan values and return per Nan values """

    # Separate core_cols dict based on forms
    core_admission_cols = core_cols['required_admission_cols']

    if 'admission_readmission' in core_admission_cols:
        core_admission_cols = core_admission_cols + ['admission_date_of_pre_discharge',
                                                     'sari_admission_assessment_fraction_inspired_oxygen',
                                                     'sari_admission_assessment_renal_replacement',
                                                     'admission_symptom_date']
    else:
        core_admission_cols = core_admission_cols + ['sari_admission_assessment_fraction_inspired_oxygen',
                                                     'sari_admission_assessment_renal_replacement',
                                                     'admission_symptom_date']

    # filter form data based on core cols
    admissionData = admissionData[admissionData.columns.intersection(core_admission_cols)]

    completeness = get_completeness_for_dataset(admissionData)
    completeness = round((completeness['number_of_entries_filled'] / completeness['total_number_of_entries']) * 100, 1)

    return completeness


def get_completeness(admissionData, dailyAssessmentData, investigationData):
    # Get the number of Nan and number of entries for core forms and save in a list

    # drop columns containing forms
    admissionData = admissionData.drop(
        ['visits', 'preQol', 'postQols', 'notes', 'tracker', 'investigations', 'dailyAssessments', 'observations'],
        axis=1)

    # if the column ends with a number above 1 drop it
    number_above_one = ('2', '3', '4', '5')
    admissionData = admissionData.drop([x for x in admissionData if x.endswith(number_above_one)], 1)
    dailyAssessmentData = dailyAssessmentData.drop([x for x in dailyAssessmentData if x.endswith(number_above_one)], 1)
    investigationData = investigationData.drop([x for x in investigationData if x.endswith(number_above_one)], 1)

    completeness_filled_total = [get_completeness_for_dataset(admissionData),
                                 get_completeness_for_dataset(dailyAssessmentData),
                                 get_completeness_for_dataset(investigationData)]

    # sum number of entries and Nan for all core forms
    total_entries = sum(form['total_number_of_entries'] for form in completeness_filled_total)
    filled_entries = sum(form['number_of_entries_filled'] for form in completeness_filled_total)

    # get completeness percentage
    completeness = round((filled_entries / total_entries) * 100, 1)

    return completeness


def get_data_dict(unit_id):
    # Convert json data dict to pandas data frame
    # with open('app/default_01.21.2020_QI.json') as json_file:
    #     data = json.load(json_file)

    data = get_json_data_dict(unit_id)['formData']

    assessment_list = []
    form_name_list = []
    form_status_list = []

    for form_name in data:
        form = data[form_name]
        form_status = form['status']
        if len(form['fields']) > 0:
            for assessment in form['fields']:
                if type(assessment) == dict:
                    assessment_list.append(assessment)
                    form_name_list.append(form_name)
                    form_status_list.append(form_status)
                elif type(assessment) == list:
                    for x in assessment:
                        assessment_list.append(x)
                        form_name_list.append(form_name)
                        form_status_list.append(form_status)

    if len(assessment_list) > 0:
        data = pd.DataFrame(assessment_list)
        data['form'] = form_name_list
        data['form_status'] = form_status_list
        data = data.loc[data['form_status'] != False]
        data = data.drop(['type'], axis=1)

        data = data.join(data['dependent'].apply(pd.Series))
        data['data'] = data['data'].apply(str)
        # join the form name with variable id so it matchers dataset
        data['key'] = data.apply(lambda y: y['form'] + '_' + y['key'], 1)
        data['data'] = data.apply(lambda y: y['data'].replace("'key': '", "'key': '{}_".format(y['form'])), 1)
        # data['data'] = data['data'].apply(eval)

    else:
        data = None

    return data


def transform_data_column_names(admissionData,
                                dailyAssessmentData=pd.DataFrame(),
                                investigationData=pd.DataFrame(),
                                sariDailyAssessment=pd.DataFrame(),
                                how='default'):
    if how == 'Match_data_dict':
        dailyAssessmentData = dailyAssessmentData.add_prefix('daily_assessment_')
        sariDailyAssessment = sariDailyAssessment.add_prefix("sari_daily_assessment_")
        investigationData = investigationData.add_prefix('investigation_')
        admissionData.columns = admissionData.columns.str.replace(".", "_")
        admissionData.columns = admissionData.columns.str.replace("admissionAssessment", "admission_assessment")
        admissionData.columns = admissionData.columns.str.replace("sariAdmissionAssessment",
                                                                  "sari_admission_assessment")
        admissionData.columns = admissionData.columns.str.replace("sariPreDischarge", "sari_pre_discharge")

    elif how == 'default':
        dailyAssessmentData.columns = dailyAssessmentData.columns.str.replace('daily_assessment_', '')
        sariDailyAssessment.columns = sariDailyAssessment.columns.str.replace("sari_daily_assessment_", "")
        investigationData.columns = investigationData.columns.str.replace('investigation_', '')
        admissionData.columns = admissionData.columns.str.replace("admission_assessment", "admissionAssessment")
        admissionData.columns = admissionData.columns.str.replace('discharge_', 'discharge.', 1)
        admissionData.columns = admissionData.columns.str.replace('admission_', 'admission.', 1)
        admissionData.columns = admissionData.columns.str.replace('admissionAssessment_', 'admissionAssessment.', 1)
        admissionData.columns = admissionData.columns.str.replace("sari_admission_assessment",
                                                                  "sariAdmissionAssessment")
        admissionData.columns = admissionData.columns.str.replace("sari_pre_discharge", "sariPreDischarge")

        admissionData = admissionData.replace('filled', np.nan)
        dailyAssessmentData = dailyAssessmentData.replace('filled', np.nan)
        investigationData = investigationData.replace('filled', np.nan)

        if len(dailyAssessmentData.dropna(how='all')) == 0:
            dailyAssessmentData = pd.DataFrame()

        if len(investigationData.dropna(how='all')) == 0:
            investigationData = pd.DataFrame()

    return {'admissionData': admissionData,
            'dailyAssessmentData': dailyAssessmentData,
            'investigationData': investigationData,
            'sariDaily_assessment': sariDailyAssessment}


def fill_empty_all_columns_on_branching_logic(data_dict, admissionData=pd.DataFrame({}),
                                              dailyAssessmentData=pd.DataFrame({}), investigationData=pd.DataFrame({}),
                                              sariDaily_assessment=pd.DataFrame({})):
    data_dict = data_dict.dropna(subset=['dependent'])
    data_dict['data'] = data_dict['data'].apply(eval)
    data_dict = data_dict.to_dict('records')
    # x = 0
    # convert '' to nan for all dataset
    admissionData = admissionData.replace(r'^\s*$', np.nan, regex=True)
    if len(dailyAssessmentData) > 0:
        dailyAssessmentData = dailyAssessmentData.replace(r'^\s*$', np.nan, regex=True)
    if len(investigationData) > 0:
        investigationData = investigationData.replace(r'^\s*$', np.nan, regex=True)
    if len(sariDaily_assessment) > 0:
        sariDaily_assessment = sariDaily_assessment.replace(r'^\s*$', np.nan, regex=True)

    data = transform_data_column_names(admissionData=admissionData,
                                       dailyAssessmentData=dailyAssessmentData,
                                       investigationData=investigationData,
                                       sariDailyAssessment=sariDaily_assessment,
                                       how='Match_data_dict')

    admissionData = data['admissionData']
    dailyAssessmentData = data['dailyAssessmentData']
    investigationData = data['investigationData']
    sariDaily_assessment = data['sariDaily_assessment']

    admissionData = for_discharge_cols_fill_if_not_discharged(admissionData)
    admissionData = for_sariAdmission_cols_fill_if_not_sari(admissionData)
    admissionData = for_sariDischarge_cols_fill_if_not_sari(admissionData)

    # for each column in data dict check which form it belongs to and input the correct dataset
    for y in data_dict:
        form_name = y['form']
        core_forms = ['admission',
                      'admission_assessment',
                      'discharge',
                      'sari_admission_assessment',
                      'sari_pre_discharge']
        if form_name in core_forms:
            admissionData = fill_column_based_on_branching_logic(admissionData, y)

        elif form_name == 'daily_assessment':
            dailyAssessmentData = fill_column_based_on_branching_logic(dailyAssessmentData, y)

        elif form_name == 'investigation':
            investigationData = fill_column_based_on_branching_logic(investigationData, y)

        elif form_name == 'sari_daily_assessment':
            sariDaily_assessment = fill_column_based_on_branching_logic(sariDaily_assessment, y)

    admissionData = admissionData.replace(r'^\s*$', np.nan, regex=True)

    if len(dailyAssessmentData) > 0:
        dailyAssessmentData = dailyAssessmentData.replace(r'^\s*$', np.nan, regex=True)
    if len(investigationData) > 0:
        investigationData = investigationData.replace(r'^\s*$', np.nan, regex=True)
    if len(sariDaily_assessment) > 0:
        sariDaily_assessment = sariDaily_assessment.replace(r'^\s*$', np.nan, regex=True)

    data = {'admissionData': admissionData,
            'dailyAssessmentData': dailyAssessmentData,
            'investigationData': investigationData,
            'sariDaily_assessment': sariDaily_assessment}

    return data


def fill_column_based_on_branching_logic(data, data_dict, query=None):
    child_column = data_dict['key']

    # if child column not there create an nan one
    if child_column not in data.columns:
        data[child_column] = np.nan

    # dependency type (AND, OR) to simple letters to match python syntax
    dependency_type = data_dict['type'].lower()

    # switch 'and' and 'or' because we will use not equal later
    if dependency_type == 'and':
        dependency_type = 'or'

    elif dependency_type == 'or':
        dependency_type = 'and'

    # if dependency type is mix or and use specific function
    if dependency_type == 'mix-or-and':
        query = format_and_or(data_dict)

    else:
        # loop through all dependency's
        for dependency in data_dict['data']:

            # parent column is the column which this dependency is based on
            parent_column = dependency['key']

            # check column is in data other wise create it
            if parent_column not in data.columns:
                data[parent_column] = np.nan

            # check if query already exist if not define it
            if query is None:
                query = f"({parent_column} != '{dependency['value']}')"

            # if query already defined join existing query with new query using the dependency type
            else:
                query_section = f"({parent_column} != '{dependency['value']}')"
                query = "{} {} {}".format(query, dependency_type, query_section)

    # convert nan to '' because other wise getting an error when filling columns
    data[child_column] = data[child_column].fillna('')
    # filter data using query and fill child column with filled to show it is not filled based on branching logic
    data.loc[data.eval(query), child_column] = 'filled'
    # convert '' to nan so we can count nan to get completeness
    data[child_column].replace('', np.nan)

    return data


def format_and_or(data):
    # query: ((subQuery) or (subQuery))
    # subQuery: ((boolStatement) and (boolStatement))
    # boolStatement: parent_column != 'yes'
    subQuery = None
    query = None
    grouped_dependencies = defaultdict(list)
    # group dependencies by parent column name store like this
    # {'parent_col': [{'value': x, 'key': 'parent_col'}]}
    for parent_column in data['data']:
        grouped_dependencies[parent_column['key']].append(parent_column)

    # for all parent columns get all its dependencies
    for parent_column in grouped_dependencies:
        dependencies = grouped_dependencies[parent_column]
        # loop through all dependencies for a parent column
        for dependency in dependencies:

            # check if you have created a subQuery for this parent col if not create one
            if subQuery is None:
                subQuery = f"({parent_column} != '{dependency['value']}')"

            # if a subQuery exists then join the new boolStatement to existing subQuery
            else:
                boolStatement = f"({parent_column} != '{dependency['value']}')"
                subQuery = "{} {} {}".format(subQuery, 'and', boolStatement)

        # check if the query has been created if so join query with subQuery using a or statement
        if query is not None:
            query = query + ' or ' + f'({subQuery})'
        # if not define it as the subquery
        else:
            query = f'({subQuery})'

        subQuery = None

    return query


def los_stats(data, admissionType=None):
    if 'discharge.date_of_discharge' in data and 'admission.date_of_admission' in data:
        # drop patients with missing admission or discharge data
        data = data.dropna(subset=['discharge.date_of_discharge', 'admission.date_of_admission'])
        # Check if there are any patents
        if len(data) > 0:

            data = filter_by_admission_type(data, admissionType)
            # convert admission and discharge dates to datetime if wrong format return NaN
            data[['discharge.date_of_discharge', 'admission.date_of_admission']] = data[
                ['discharge.date_of_discharge', 'admission.date_of_admission']].apply(pd.to_datetime, format='%Y-%m-%d',
                                                                                      errors='coerce')
            # Drop patients with wrongly formatted dates
            data = (data[data[['discharge.date_of_discharge', 'admission.date_of_admission']].notnull().all(1)])
            # Get number of days between admission and discharge dates
            list_of_stay = (data['discharge.date_of_discharge'] - data['admission.date_of_admission'])
            if len(list_of_stay) > 0:
                # convert datetime to number of days
                list_of_stay = list_of_stay.dt.days
                # Get mean of pandas series
                mean_stay = round(list_of_stay.mean(), 1)
                # Get standard deviation
                std = round(list_of_stay.std(ddof=0), 1)
                # Get median
                median = round(list_of_stay.median(), 1)
                # get iqr
                iqr = round(np.subtract(*np.percentile(list_of_stay, [75, 25])), 1)

            else:
                mean_stay = 'No data'
                std = 'No data'
                median = 'No data'
                iqr = "No data"

        else:
            mean_stay = 'No data'
            std = 'No data'
            median = 'No data'
            iqr = "No data"

    else:
        mean_stay = 'No data'
        std = 'No data'
        median = 'No data'
        iqr = "No data"

    return {'mean_stay': mean_stay,
            'std': std,
            'median': median,
            'iqr': iqr}


def non_invasive_ventilation(data):
    if pd.Series(['admissionAssessment.mechanically_ventilated', 'admission.admission_type']).isin(data.columns).all():
        data = data.loc[data['admission.admission_type'] == 'Planned']
        admission_this_month = len(data)
        yes = list(data['admissionAssessment.mechanically_ventilated']).count("Non invasive vent")
        if admission_this_month > 0:
            per = yes / admission_this_month * 100
            per = round(per, 1)
        else:
            yes = "No data"
            per = "No data"
    else:
        yes = "No data"
        per = "No data"

    return {'count': yes, 'per': per}


def los_prior_to_icu(data, admissionType=None):
    required_column = ['admission.date_of_admission_hospital', 'admission.date_of_admission',
                       'admission.admission_type']
    if pd.Series(required_column).isin(data.columns).all():

        data = filter_by_admission_type(data, admissionType)

        if len(data) > 0:
            data[['admission.date_of_admission_hospital', 'admission.date_of_admission']] = data[
                ['admission.date_of_admission_hospital', 'admission.date_of_admission']].apply(pd.to_datetime,
                                                                                               format='%Y-%m-%d',
                                                                                               errors='coerce')
            data = (
                data[data[['admission.date_of_admission_hospital', 'admission.date_of_admission']].notnull().all(1)])
            if len(data) > 0:
                list_of_stay = (
                        data['admission.date_of_admission'] - data['admission.date_of_admission_hospital']).dt.days
                mean_stay = list_of_stay.mean()
                mean_stay = round(mean_stay, 1)
            else:
                print('los_prior_to_icu: No data after converting dates to datetime and droping Nan')
                mean_stay = "No data"
        else:
            print('los_prior_to_icu: No data after filtering by admission_type')
            mean_stay = "No data"

    else:
        print('los_prior_to_icu missing a required column')
        mean_stay = "No data"

    return mean_stay


def per_left_against_medical_advice(data):
    if pd.Series(['discharge.discharge_status', 'discharge.left_against_medical_advice']).isin(data.columns).all():
        data = data.loc[data['discharge.discharge_status'] == 'Alive']
        patients_discharged_alive = len(data)
        if patients_discharged_alive > 0:
            left_against_medical_advice_list = list(data['discharge.left_against_medical_advice'])
            count_yes = left_against_medical_advice_list.count('Yes')
            per_yes = round(count_yes / patients_discharged_alive, 1)
        else:
            count_yes = 'No data'
            per_yes = 'No data'
    else:
        count_yes = 'No data'
        per_yes = 'No data'

    return {'count_yes': count_yes, 'per_yes': per_yes}


def withdrawal_of_treatment(data, number_of_patients):
    if 'discharge.treatment_withdrawal' in data and number_of_patients > 0:
        treatment_withdrawal_list = list(data['discharge.treatment_withdrawal'])
        count_yes = treatment_withdrawal_list.count('Yes')
        count_no = treatment_withdrawal_list.count('No')
        per_yes = round(count_yes / number_of_patients, 1)
        per_no = round(count_no / number_of_patients, 1)
    else:
        count_yes = 'No data'
        count_no = 'No data'
        per_yes = 'No data'
        per_no = 'No data'

    return {'count_yes': count_yes,
            'count_no': count_no,
            'per_yes': per_yes,
            'per_no': per_no
            }


def smr(data, admission_type=None):
    # Check that all the columns we need are in the data set
    columns_requiem = ['admissionAssessment.systolic_blood_pressure', 'admissionAssessment.respiratory_rate',
                       'admissionAssessment.vasoactive_drugs', 'admissionAssessment.mechanically_ventilated',
                       'admissionAssessment.gcs_motor', 'admissionAssessment.gcs_verbal',
                       'admissionAssessment.gcs_eye', 'admissionAssessment.blood_urea',
                       'discharge.discharge_status', 'admissionAssessment.hemoglobin']

    # check required columns are available
    if pd.Series(columns_requiem).isin(data.columns).all():

        # filter for only discharge patients
        data = data.dropna(subset=['discharge.discharge_status'])

        # filter by admission.admission_type if input given
        if admission_type:
            data = data.loc[data['admission.admission_type'] == admission_type]

        # Check that we have at least one patient
        if len(data) > 0:

            numeric_cols = ['admissionAssessment.systolic_blood_pressure', 'admissionAssessment.respiratory_rate',
                            'admissionAssessment.blood_urea', 'admissionAssessment.hemoglobin']
            str_cols = ['admissionAssessment.vasoactive_drugs', 'admissionAssessment.mechanically_ventilated',
                        'admissionAssessment.gcs_motor', 'admissionAssessment.gcs_verbal',
                        'admissionAssessment.gcs_eye']

            # Convert numeric columns into int's and strings columns into strings
            data[numeric_cols] = data[numeric_cols].apply(pd.to_numeric, errors='coerce')
            data[str_cols] = data[str_cols].astype(str)

            # sbp
            # if systolic_blood_pressure is less then 50 sbp_TropICS equals NaN
            # if systolic_blood_pressure is more or equal to 90 and less then or equal to 180 sbp_TropICS equals zero
            # if systolic_blood_pressure is not zero and < 90 and more than 50 sbp_TropICS equals systolic_blood_pressure - 90
            # if systolic_blood_pressure is more than 180 sbp_TropICS equals systolic_blood_pressure - 180
            data['sbp_TropICS'] = data['admissionAssessment.systolic_blood_pressure']
            data.loc[((data['admissionAssessment.systolic_blood_pressure'] >= 90) & (
                    data['admissionAssessment.systolic_blood_pressure'] <= 180)), 'sbp_TropICS'] = 0
            data.loc[((data['admissionAssessment.systolic_blood_pressure'] != 0) & (
                    data['admissionAssessment.systolic_blood_pressure'] < 90)), 'sbp_TropICS'] = data[
                                                                                                     'admissionAssessment.systolic_blood_pressure'] - 90
            data.loc[(data['admissionAssessment.systolic_blood_pressure'] > 180), 'sbp_TropICS'] = data[
                                                                                                       'admissionAssessment.systolic_blood_pressure'] - 180

            # rr (respiratory rate) variable respiratory_rate
            data['rr_TropICS'] = data['admissionAssessment.respiratory_rate']
            data.loc[((data['admissionAssessment.respiratory_rate'] >= 12) & (
                    data['admissionAssessment.respiratory_rate'] <= 24)), 'rr_TropICS'] = 0
            data.loc[((data['admissionAssessment.respiratory_rate'] != 0) & (
                    data['admissionAssessment.respiratory_rate'] < 12)), 'rr_TropICS'] = data['admissionAssessment' \
                                                                                              '.respiratory_rate'] - 12
            data.loc[(data['admissionAssessment.respiratory_rate'] > 24), 'rr_TropICS'] = data['admissionAssessment' \
                                                                                               '.respiratory_rate'] - 24

            # blood urea
            data['blood_urea_TropICS'] = data['admissionAssessment.blood_urea']

            # Haemoglobin
            data['haemoglobin_TropICS'] = data['admissionAssessment.hemoglobin']

            # vasoactive
            vasoactive_levels = ['More than 2', '2', '1', 'None']
            data['vasoactive_drugs_score'] = data['admissionAssessment.vasoactive_drugs'].replace(vasoactive_levels,
                                                                                                  [1, 1, 1, 0])

            # mechanically_vent
            data['mechanically_vent_score'] = data['admissionAssessment.mechanically_ventilated'].replace(
                ['mechanical_vent', 'self_vent',
                 'Non invasive vent'], [1, 0, 1])

            # gcs
            gcs_motor_cat = ['No motor response', 'Extension to pain', 'Flexion in response to pain',
                             'Withdraws from pain', 'Locailzes to pain', 'Obeys Commands']
            gcs_motor_val = [1, 2, 3, 4, 5, 6]
            data['gcs_motor_val'] = data['admissionAssessment.gcs_motor'].replace(gcs_motor_cat, gcs_motor_val)

            gsc_veral_cat = ['None', 'Incomprehensible sounds', 'Inappropriate words', 'Confused', 'Oriented']
            gsc_veral_val = [1, 2, 3, 4, 5]
            data['gcs_verbal_val'] = data['admissionAssessment.gcs_verbal'].replace(gsc_veral_cat, gsc_veral_val)

            gcs_eye_cat = ['No eye opening', 'Eye opening in response to pain', 'Eye opening to Speech',
                           'Eye opening spontaneously']
            gsc_eye_val = [1, 2, 3, 4]
            data['gcs_eye_val'] = data['admissionAssessment.gcs_eye'].replace(gcs_eye_cat, gsc_eye_val)

            # convect all the values use in the score to numeric values if non numeric drop the row
            cols = ['sbp_TropICS', 'rr_TropICS', 'blood_urea_TropICS', 'haemoglobin_TropICS',
                    'vasoactive_drugs_score', 'mechanically_vent_score', 'gcs_motor_val', 'gcs_verbal_val',
                    'gcs_eye_val']
            data[cols] = data[cols].apply(pd.to_numeric, errors='coerce')

            data = data.dropna(subset=cols)

            data['sbp_TropICS'] = data['sbp_TropICS'].abs()
            data['rr_TropICS'] = data['rr_TropICS'].abs()

            if len(data) > 0:
                data['gcs_score'] = data['gcs_eye_val'] + data['gcs_verbal_val'] + data['gcs_motor_val']
                eTropics_score = 0.6164 + 0.060 * (data['rr_TropICS']) - 0.019 * (
                    data['sbp_TropICS']) - 0.099 * (data['gcs_score']) + 0.006 * log(
                    data['blood_urea_TropICS']) - 0.093 * \
                                 data['haemoglobin_TropICS'] + 1.057 * data['vasoactive_drugs_score'] + 1.429 * data[
                                     'mechanically_vent_score']
                mean_etropics_score = round(eTropics_score.mean(), 2)
                predicted_mortality = round((1 / ((1 / exp(eTropics_score)) + 1)).sum(), 2)
                real_mortality = len(data.loc[data['discharge.discharge_status'] == 'Dead'])
                smr_value = round(real_mortality / predicted_mortality, 1)
            else:
                mean_etropics_score = 'No data'
                predicted_mortality = 'No data'
                real_mortality = 'No data'
                smr_value = 'No data'
        else:
            mean_etropics_score = 'No data'
            predicted_mortality = 'No data'
            real_mortality = 'No data'
            smr_value = 'No data'
    else:
        mean_etropics_score = 'No data'
        predicted_mortality = 'No data'
        real_mortality = 'No data'
        smr_value = 'No data'

    return {'mean_etropics_score': mean_etropics_score, 'predicted_mortality': predicted_mortality,
            'real_mortality': real_mortality, 'smr': smr_value}



def create_columns_if_not_there(data, columns_needed):
    empty_column = pd.Series([None] * len(data))
    for column in columns_needed:
        if column not in data.columns:
            data[column] = empty_column
    return data


def completeness_cal(dataset, columns_needed, form='admission'):
    """ this function checks the number of non NaN
        and the percentage the input is the data set and column name
    """
    completeness_for_dataset = defaultdict(dict)
    if isinstance(dataset, pd.DataFrame):
        if len(dataset) > 0:
            dataset = create_columns_if_not_there(dataset, columns_needed)
            patients = len(dataset.index)
            for column in list(dataset.columns.astype(str)):
                if '.' in column:
                    split_name = column.split('.')
                    form_name = split_name[0]
                    variable_name = split_name[1]
                    number = patients - dataset[column].isna().sum().item()
                    per = round(number / patients * 100)
                    completeness_for_dataset[form_name][variable_name] = {"number": number, "per": per}
                else:
                    number = patients - dataset[column].isna().sum().item()
                    per = round(number / patients * 100)
                    completeness_for_dataset[column] = {"number": number, "per": per}
                # completeness_with_column_name = {column + '_completeness': completeness_for_column}
                # completeness_for_dataset.append(completeness_with_column_name)
            # print(completeness_for_dataset)
            # completeness_for_dataset = json.dumps(completeness_for_dataset)

        else:
            for column in columns_needed:
                if '.' in column:
                    split_name = column.split('.')
                    form_name = split_name[0]
                    variable_name = split_name[1]
                    completeness_for_dataset[form_name][variable_name] = {"number": 'No data', "per": 'No data'}
                else:
                    completeness_for_dataset[column] = {"number": 'No data', "per": 'No data'}

    else:
        completeness_for_dataset = 'No data'

    return completeness_for_dataset


def age(data, admissionType=None):
    if 'admission.age' in data and len(data['admission.age']) > 0:

        data = filter_by_admission_type(data, admissionType)
        age_data = pd.to_numeric(data['admission.age'], errors='coerce')
        mean = age_data.mean()
        standard_deviation = age_data.std(ddof=0)

        if not pd.isna(mean):
            mean = round(mean)
        else:
            mean = 'No data'

        if not pd.isna(standard_deviation):
            standard_deviation = round(standard_deviation)
        else:
            standard_deviation = 'No data'

    else:
        mean = 'No data'
        standard_deviation = 'No data'

    return {'std': standard_deviation, 'mean': mean}


def gender(data, admissionType=None):
    if 'admission.gender' in data and data['admission.gender'].astype(str).str.contains('Male|Female').any():

        data = filter_by_admission_type(data, admissionType)
        gender_list = list(data['admission.gender'])
        male = gender_list.count('Male')
        female = gender_list.count('Female')
        length = male + female
        if length > 0:
            per_male = round(male / length * 100)
            per_female = round(female / length * 100)

        else:
            male = 'No data'
            female = 'No data'
            per_female = 'No data'
            per_male = 'No data'

    else:
        male = 'No data'
        female = 'No data'
        per_female = 'No data'
        per_male = 'No data'

    return {'male': male, 'female': female, 'per_female': per_female, 'per_male': per_male}


def discharge_status(data):
    if 'discharge.discharge_status' in data and data['discharge.discharge_status'].astype(str).str.contains(
            'Alive|Dead').any():
        alive = (list(data['discharge.discharge_status']).count("Alive"))
        dead = (list(data['discharge.discharge_status']).count("Dead"))
        discharged_patients = alive + dead
        per_dead = round(dead / discharged_patients * 100)
        per_alive = round(alive / discharged_patients * 100)
    else:
        alive = "No data"
        dead = "No data"
        per_alive = "No data"
        per_dead = "No data"

    return {'alive': alive, 'dead': dead, 'per_alive': per_alive, 'per_dead': per_dead}


def get_discharge_details(data):
    if isinstance(data, pd.DataFrame) and len(data) > 0 and all(i in data for i in ['admission.date_of_admission',
                                                                                    'admission.medical_record_number',
                                                                                    'discharge.discharge_status',
                                                                                    'patient_id']):
        data = data[['admission.date_of_admission', 'admission.medical_record_number', 'discharge.discharge_status',
                     'patient_id']]
        data.columns = ['date_of_admission', 'medical_record_number', 'discharge_status', 'patient_id']
        json_data = data.to_json(orient='records')
    else:
        json_data = 'No data'

    return json_data


def tracheostomy_performed(data, daily_assessment, admissionType=None):
    if 'admissionAssessment.mechanically_ventilated_source' in data and 'mechanically_ventilated_source' in daily_assessment:
        merged_data = pd.concat([daily_assessment, data.rename(index=str,
                                                               columns={
                                                                   'admissionAssessment.mechanically_ventilated_source': 'mechanically_ventilated_source'})],
                                ignore_index=True)
        merged_data = filter_by_admission_type(merged_data, admissionType)
        merged_data = merged_data.loc[merged_data['mechanically_ventilated_source'] == 'Tracheostomy']
        tracheostomy = merged_data['patient_id'].nunique()

    elif 'admissionAssessment.mechanically_ventilated_source' in data:
        data = filter_by_admission_type(data, admissionType)
        data = data.loc[data['admissionAssessment.mechanically_ventilated_source'] == 'Tracheostomy']
        tracheostomy = data['patient_id'].nunique()

    elif 'mechanically_ventilated_source' in daily_assessment:
        data = filter_by_admission_type(data, admissionType)
        data = daily_assessment.loc[daily_assessment['mechanically_ventilated_source'] == 'Tracheostomy']
        tracheostomy = data['patient_id'].nunique()

    else:
        tracheostomy = "No data"

    return tracheostomy


def covid_count_by_unit(covid_data, start_date, end_date, unit_id):
    # convert date input to the correct string format '%m/%d/%y'
    start_date = datetime.strptime(start_date, '%d/%m/%Y').strftime('%m/%d/%Y')
    end_date = datetime.strptime(end_date, '%d/%m/%Y').strftime('%m/%d/%Y')

    # get all unique units rename them from unit 1 to unit x
    unique_units = covid_data['unitId'].unique()
    unit_df = pd.DataFrame({'unitId': unique_units})
    unit_df['unit_name'] = 'Unit'
    unit_df['unit_name'] = unit_df['unit_name'] + ' ' + (unit_df.index + 1).astype(str)

    # if unitid is my unit call unit name my unit
    unit_df.loc[(unit_df['unitId'] == unit_id), 'unit_name'] = 'My unit'

    # get unit names for keys later
    unit_names = unit_df['unit_name'].tolist()

    # merge unit info with full data to get the new colour and name coloumns into the main dataset
    covid_data = pd.merge(covid_data, unit_df, on='unitId')

    if 'My unit' in unit_names:
        ordered_units = [x for x in unit_names if x != 'My unit']
        ordered_units = ['My unit'] + ordered_units
    else:
        ordered_units = unit_names

    # reindex the dates to have a date for each day and make it a cumlitive count
    covid_data = covid_data.pivot_table(values='num', index='admission.date_of_admission', columns='unit_name',
                                        aggfunc='sum')
    covid_data = covid_data[ordered_units]
    idx = pd.date_range(start_date, end_date, freq='D')
    covid_data.index = pd.DatetimeIndex(covid_data.index)
    covid_data = covid_data.reindex(idx, fill_value=0)
    covid_data = covid_data.reset_index().rename(columns={'index': 'date_of_admission'})
    covid_data['date_of_admission'] = covid_data['date_of_admission'].dt.strftime('%Y-%m-%d')
    covid_data = covid_data.fillna(0)
    covid_data[unit_names] = covid_data[unit_names].cumsum()
    covid_json_data = covid_data.to_json(orient='records', date_format='iso', date_unit='s')

    # get unit color dict
    colours = {}

    for idx, unit in enumerate(unit_names):
        colours[unit] = colors[idx]

    return {'covid_json_data': covid_json_data, 'colours': colours}


def covid_count_for_unit(covid_data, start_date, end_date):
    # convert date input to the correct string format '%m/%d/%y'
    start_date = datetime.strptime(start_date, '%d/%m/%Y').strftime('%m/%d/%Y')
    end_date = datetime.strptime(end_date, '%d/%m/%Y').strftime('%m/%d/%Y')

    if 'admission.date_of_admission' in covid_data:
        column = 'admission.date_of_admission'
    else:
        column = 'admission.date_of_admission_hospital'

    # reindex the dates to have a date for each day and make it a cumlitive count
    covid_data = covid_data.pivot_table(values='num', index=column, aggfunc='sum')
    idx = pd.date_range(start_date, end_date, freq='D')
    covid_data.index = pd.DatetimeIndex(covid_data.index)
    covid_data = covid_data.reindex(idx, fill_value=0)
    covid_data = covid_data.reset_index().rename(columns={'index': 'date_of_admission'})
    covid_data['date_of_admission'] = covid_data['date_of_admission'].dt.strftime('%Y-%m-%d')
    covid_data = covid_data.fillna(0)
    covid_data['num'] = covid_data['num'].cumsum()
    covid_json_data = covid_data.to_json(orient='records', date_format='iso', date_unit='s')

    return covid_json_data


def number_of_clauti_for_patient(daily_assessment):
    # reset index
    daily_assessment = daily_assessment.reset_index(drop=True)

    # create a duplicate dataset to check for clabsi after patietns is off uc
    data_duplicate = daily_assessment

    # create another duplicate dataset to get the number of days ur
    xxx = daily_assessment

    # get patient_id to return
    try:
        patient_id = daily_assessment["patient_id"].iloc[0]
    except:
        patient_id = 'x'
    clauti_count = 0
    cvc_stat = ''
    date_of_admission = daily_assessment['admission_date'][0]
    number_ur_days = 0
    ur_stat_x = ''

    # get numbewr of cvc days
    while len(xxx) > 0:
        xxx = xxx.reset_index(drop=True)
        # find a the next ur if ur_stat_x is no
        if ur_stat_x in ["No", '', np.nan]:
            # find the first ur yes data point
            mask = xxx['urinary_catheterization'].isin(pd.Series(['New', 'Insitu']))
            try:
                # check that the point exists
                idx = next(iter(mask.index[mask]), 'not exist')
                # set the ur status as ur
                if idx == 'not exist':
                    break
                ur_stat_x = xxx["urinary_catheterization"].iloc[idx]
                # set the ur date as datetime
                ur_date = xxx["date"].iloc[idx]
                ur_date = datetime.strptime(ur_date, "%Y-%m-%d")
                # if ur stat is Insitu set ur date as a day before stated
                if ur_stat_x == "Insitu":
                    ur_date = ur_date - timedelta(days=1)
                # remove the data before we have a ur status
                xxx = xxx.loc[idx:].reset_index(drop=True)

                # find the end of the ur
                mask = xxx['urinary_catheterization'] == 'No'
                # check that the point exists
                idx = next(iter(mask.index[mask]), 'not exist')

                # if there is a no after the ur then use it to find out length of ur
                if idx != 'not exist':
                    ur_end_date = xxx["date"].iloc[idx]
                    ur_end_date = datetime.strptime(ur_end_date, "%Y-%m-%d")
                    ur_stat_x = 'No'
                    number_ur_days_x = (ur_end_date - ur_date)
                    number_ur_days_x = number_ur_days_x.days
                    number_ur_days = number_ur_days + number_ur_days_x
                    xxx = xxx.loc[idx:].reset_index(drop=True)

                # if no ur end use the max date to get number of ur days
                else:
                    ur_end_date = max(xxx['date'].dropna())
                    ur_end_date = datetime.strptime(ur_end_date, "%Y-%m-%d")
                    ur_end_date = ur_end_date + timedelta(days=1)
                    number_ur_days_x = (ur_end_date - ur_date)
                    number_ur_days_x = number_ur_days_x.days + 1
                    number_ur_days = number_ur_days + number_ur_days_x
                    ur_stat_x = 'No'
                    xxx = xxx.loc[idx:].reset_index(drop=True)

            except:
                break

    while len(daily_assessment) > 0:
        daily_assessment = daily_assessment.reset_index(drop=True)

        if cvc_stat in ["No", '', np.nan]:
            # find the first cvc yes data point
            mask = daily_assessment['urinary_catheterization'].isin(pd.Series(['New', 'Insitu']))
            try:
                # check that the point exists
                idx = next(iter(mask.index[mask]), 'not exist')
                # set the cvc status as cvc
                cvc_stat = daily_assessment["urinary_catheterization"].iloc[idx]
                # set the cvc date as datetime
                cvc_date = daily_assessment["date"].iloc[idx]
                cvc_date = datetime.strptime(cvc_date, "%Y-%m-%d")
                # if cvc stat is Insitu set cvc date as a day before stated
                if cvc_stat == "Insitu":
                    cvc_date = cvc_date - timedelta(days=1)
                # remove the data before we have a cvc status
                daily_assessment = daily_assessment.loc[idx:].reset_index(drop=True)
            except:
                break

        # get the date of this daily_assessment
        first_date_on_cvc = daily_assessment.loc[0]['date']

        # get first three dates in datetime format
        first_date_on_cvc = datetime.strptime(first_date_on_cvc, "%Y-%m-%d")
        second_date_on_cvc = first_date_on_cvc + timedelta(days=1)
        third_date_on_cvc = second_date_on_cvc + timedelta(days=1)

        # get first three dates in str format
        first_date_on_cvc_str = str(first_date_on_cvc)[:10]
        second_date_on_cvc_str = str(second_date_on_cvc)[:10]
        third_date_on_cvc_str = str(third_date_on_cvc)[:10]

        # get the number of days on cvc
        day_number = (first_date_on_cvc - cvc_date)
        day_number = day_number.days

        if day_number == 0 and len(daily_assessment) > 2:

            if len(daily_assessment.loc[(daily_assessment['date'] == second_date_on_cvc_str) & (
                    daily_assessment['date'] == 'No')]) < 1:

                third_day = daily_assessment.loc[
                    daily_assessment['date'] == third_date_on_cvc_str]

                if len(third_day) > 0:
                    clauti_validation = len(third_day.loc[
                                                (third_day['temperature'] > 38) &
                                                (third_day['type_of_culture'] == 'Urine') &
                                                (third_day['cfu'] > 104) &
                                                ((third_day['organism2'].isna()) | (third_day['organism2'] == 'None'))
                                                ]) > 0

                    if clauti_validation:
                        clauti_count += 1

                    cvc_stat = daily_assessment["urinary_catheterization"].iloc[0]

                daily_assessment = daily_assessment.loc[(daily_assessment['date'] > third_date_on_cvc_str)]

            else:
                cvc_stat = np.nan

                daily_assessment = daily_assessment.loc[(daily_assessment['date'] > second_date_on_cvc_str)]



        elif day_number == 1:

            third_day = daily_assessment.loc[daily_assessment['date'] == second_date_on_cvc_str]

            if len(third_day) > 0:
                clauti_validation = len(third_day.loc[
                                            (third_day['temperature'] > 38) &
                                            (third_day['type_of_culture'] == 'Urine') &
                                            (third_day['cfu'] > 104) &
                                            ((third_day['organism2'].isna()) | (third_day['organism2'] == 'None'))
                                            ]) > 0

                if clauti_validation:
                    clauti_count += 1

                cvc_stat = daily_assessment["urinary_catheterization"].iloc[0]

            daily_assessment = daily_assessment.loc[(daily_assessment['date'] > second_date_on_cvc_str)]


        elif day_number > 1:

            third_day = daily_assessment.loc[daily_assessment['date'] == first_date_on_cvc_str]

            if len(third_day) > 0:
                clauti_validation = len(third_day.loc[
                                            (third_day['temperature'] > 38) &
                                            (third_day['type_of_culture'] == 'Urine') &
                                            (third_day['cfu'] > 104) &
                                            (third_day['organism2'].isna())
                                            ]) > 0

                if clauti_validation:
                    clauti_count += 1

                cvc_stat = daily_assessment["urinary_catheterization"].iloc[0]

            daily_assessment = daily_assessment.loc[(daily_assessment['date'] > first_date_on_cvc_str)]

        else:
            break

    # check for CLABSI for patietns off cvc for 24 hours
    while len(data_duplicate) > 2:
        data_duplicate = data_duplicate.reset_index(drop=True)

        mask = data_duplicate['urinary_catheterization'].isin(pd.Series(['New', 'Insitu']))
        try:
            idx = next(iter(mask.index[mask]), 'not exist')
        except:
            break

        if idx == 'not exist':
            break

        # select data after the first cvc line
        data_duplicate = data_duplicate.loc[idx:].reset_index(drop=True)

        first_date_on_cvc = min(data_duplicate['date'].dropna())
        # if isinstance(first_date_on_cvc, float):
        #     first_date_on_cvc = data_duplicate.loc[idx]['date_of_investigation']

        last_date = max(data_duplicate['date'].dropna())
        # if isinstance(last_date, float):
        #     last_date = data_duplicate.loc[-1]['date_of_investigation']

        # get list of dates between first and last date so we can loop through and check if we have a cvc no
        dates = pd.date_range(start=first_date_on_cvc, end=last_date).astype(str).tolist()

        # loop through avery day of daily data
        for date in dates:

            # check for a day when cvc is no to start the timer for clabsi
            if len(data_duplicate.loc[
                       (data_duplicate['date'] == date) &
                       ((data_duplicate['urinary_catheterization'] == 'No'))
                   ]) > 0:

                # get the third day after patietn is off cvc
                first_date_off_cvc = datetime.strptime(date, "%Y-%m-%d")
                second_date_off_cvc = str(first_date_off_cvc + timedelta(days=2))[:10]

                second_day = data_duplicate.loc[data_duplicate['date'] == second_date_off_cvc]

                # do a clabsi check
                clauti_validation = len(second_day.loc[
                                            (second_day['temperature'] > 38) &
                                            (second_day['type_of_culture'] == 'Urine') &
                                            (second_day['cfu'] > 104) &
                                            (second_day['organism2'].isna())
                                            ]) > 0

                # add CLABSI if matchers
                if clauti_validation:
                    clauti_count = clauti_count + 1

                data_duplicate = data_duplicate.loc[
                    (data_duplicate['date'] > date)]

                # Look for the next day on cvc
                break

            # Look for the next day on cvc
            data_duplicate = data_duplicate.loc[
                (data_duplicate['date'] > date)]

    # return {"clauti_num": clauti_count, "eligible": patients_with_ur, "pwc": pwc, 'patient_id': patient_id}
    return {'clauti_count': clauti_count, 'admission_date': date_of_admission, 'days_on_x': number_ur_days,
            'patient_id': patient_id}


def clauti_count_for_dataset(daily_assessment, investigation):
    # data = pd.concat([daily_assessment, investigation], axis=0).sort_values(by=['patient_id'])
    required_cols = daily_assessment.columns
    required_cols = required_cols.append(investigation.columns)
    if pd.Series(['patient_id',
                  'admission_date',
                  'date_of_daily_assessment',
                  'date_of_investigation',
                  'urinary_catheterization',
                  'temperature',
                  'type_of_culture',
                  'cfu',
                  'organism2']).isin(required_cols).all() and len(daily_assessment) > 0:

        # difine organism data-type so we can merge saftly
        try:
            daily_assessment[['organism', 'organism1', 'organism2']] = daily_assessment[
                ['organism', 'organism1', 'organism2']].astype(str)
            investigation[['organism', 'organism1', 'organism2']] = investigation[
                ['organism', 'organism1', 'organism2']].astype(str)

            # merge daily assessment and investigation to get all daily_entered data
            data = pd.merge(daily_assessment, investigation, how='outer',
                            left_on=['patient_id', 'date_of_daily_assessment', 'organism', 'organism1', 'organism2'],
                            right_on=['patient_id', 'date_of_investigation', 'organism', 'organism1', 'organism2'])
        except:
            data = pd.merge(daily_assessment, investigation, how='outer',
                            left_on=['patient_id', 'date_of_daily_assessment'],
                            right_on=['patient_id', 'date_of_investigation'])

        # drop patients missing date_of_daily_assessment
        data = data.dropna(subset=["date_of_daily_assessment"])

        # replace string nan to nan
        data[['organism', 'organism1', 'organism2']] = data[['organism', 'organism1', 'organism2']].replace(
            'nan', np.nan, regex=True)

        data = merge_culture_columns(data)

        data = data[['patient_id',
                     'admission_date',
                     'date_of_daily_assessment',
                     'date_of_investigation',
                     'urinary_catheterization',
                     'temperature',
                     'type_of_culture',
                     'cfu',
                     'organism2']
        ]
        data['admission_date'] = pd.to_datetime(data['admission_date'], format='%Y-%m-%d')
        data['admission_date'] = data['admission_date'].dt.strftime('%m/%Y')

        # create a date coloumn which combines investigation and aily assessement dates to fill and missing dates
        data['date'] = data['date_of_daily_assessment']
        data.loc[(data['date_of_daily_assessment'].isna()), 'date'] = data['date_of_investigation']

        # if len(data.dropna(subset=['type_of_culture', 'cfu'])) > 0:

        number_of_clauti_per_patient = (data.groupby('patient_id').apply(number_of_clauti_for_patient)).tolist()
        clauti_dataframe = pd.DataFrame(number_of_clauti_per_patient)
        # filter patients with a ur
        clauti_dataframe = clauti_dataframe[clauti_dataframe['days_on_x'] > 0]
        clauti_dataframe['patients_with_clauti'] = 0
        clauti_dataframe.loc[((clauti_dataframe['clauti_count'] > 0)), 'patients_with_clauti'] = 100


    else:
        clauti_dataframe = 'No data'

    return clauti_dataframe


def clauti_rate_for_dataset(daily_assessment, clauti_dataframe):
    if isinstance(clauti_dataframe, pd.DataFrame) and 'urinary_catheterization' in daily_assessment:

        lower_quartile_rate = clauti_dataframe['clauti_count'].quantile(0.25)
        median_rate = clauti_dataframe['clauti_count'].median()
        upper_quartile_rate = clauti_dataframe['clauti_count'].quantile(0.75)

        quartile_range = upper_quartile_rate - lower_quartile_rate
        sixth_quartile_range = quartile_range / 6

        two_sixth = lower_quartile_rate + sixth_quartile_range
        three_sixth = lower_quartile_rate + (sixth_quartile_range * 2)
        four_sixth = lower_quartile_rate + (sixth_quartile_range * 3)
        five_sixth = lower_quartile_rate + (sixth_quartile_range * 4)

    else:
        median_rate = 'No data'
        lower_quartile_rate = 'No data'
        two_sixth = 'No data'
        three_sixth = 'No data'
        four_sixth = 'No data'
        five_sixth = 'No data'
        sixth_quartile_range = 'No data'

    return {'value': median_rate, 'min': lower_quartile_rate, 'twosixth': two_sixth, 'threesixth': three_sixth,
            'foursixth': four_sixth, 'fivesixth': five_sixth, 'max': sixth_quartile_range}


def clabsi_count_for_patient(daily_assessment):
    # reset index
    daily_assessment = daily_assessment.reset_index(drop=True)
    xxx = daily_assessment

    # create a duplicate dataset to check for clabsi after patietns is off cvc
    data_duplicate = daily_assessment
    days = []

    # get patient_id to return
    try:
        patient_id = daily_assessment["patient_id"].iloc[0]
    except:
        patient_id = 'x'

    clabsi_count = 0
    diagnosis_list = ['Diptheroids',
                      'Corynebacterium spp',
                      'Bacillus spp',
                      'Propionibacterium spp',
                      'coagulase-negative staphylococci',
                      'viridans group streptococci',
                      'Aerococcus spp',
                      'Micrococcus spp',
                      'Rhodococcus spp'
                      ]
    # cvc_status = daily_assessment["central_venous_catheter"].iloc[0]
    # cvc_start_date = daily_assessment["admission_date"].iloc[0]
    # cvc_start_date = datetime.strptime(cvc_start_date, "%Y-%m-%d")
    cvc_status = ''
    cvc_status_x = ''
    date_of_admission = daily_assessment['admission_date'][0]
    number_cvc_days = 0

    # get numbewr of cvc days
    while len(xxx) > 0:
        xxx = xxx.reset_index(drop=True)
        # find a the next cvc if cvc_stat_x is no
        if cvc_status_x in ["No", '', np.nan]:
            # find the first cvc yes data point
            mask = xxx['central_venous_catheter'].isin(pd.Series(['New', 'Insitu']))
            try:
                # check that the point exists
                idx = next(iter(mask.index[mask]), 'not exist')
                # set the cvc status as cvc
                if idx == 'not exist':
                    break
                cvc_status_x = xxx["central_venous_catheter"].iloc[idx]
                # set the cvc date as datetime
                cvc_start_date = xxx["date"].iloc[idx]
                cvc_start_date = datetime.strptime(cvc_start_date, "%Y-%m-%d")
                # if cvc stat is Insitu set cvc date as a day before stated
                if cvc_status_x == "Insitu":
                    cvc_start_date = cvc_start_date - timedelta(days=1)
                # remove the data before we have a cvc status
                xxx = xxx.loc[idx:].reset_index(drop=True)

                # find the end of the cvc
                mask = xxx['central_venous_catheter'] == 'No'
                # check that the point exists
                idx = next(iter(mask.index[mask]), 'not exist')

                # if there is a no after the cvc then use it to find out length of cvc
                if idx != 'not exist':
                    cvc_end_date = xxx["date"].iloc[idx]
                    cvc_end_date = datetime.strptime(cvc_end_date, "%Y-%m-%d")
                    cvc_status_x = 'No'
                    number_cvc_days_x = (cvc_end_date - cvc_start_date)
                    number_cvc_days_x = number_cvc_days_x.days
                    number_cvc_days = number_cvc_days + number_cvc_days_x
                    xxx = xxx.loc[idx:].reset_index(drop=True)

                # if no cvc end use the max date to get number of cvc days
                else:
                    cvc_end_date = max(xxx['date'].dropna())
                    cvc_end_date = datetime.strptime(cvc_end_date, "%Y-%m-%d")
                    cvc_end_date = cvc_end_date + timedelta(days=1)
                    number_cvc_days_x = (cvc_end_date - cvc_start_date)
                    number_cvc_days_x = number_cvc_days_x.days + 1
                    number_cvc_days = number_cvc_days + number_cvc_days_x
                    cvc_status_x = 'No'
                    xxx = xxx.loc[idx:].reset_index(drop=True)

            except:
                break

    while len(daily_assessment) > 0:
        daily_assessment = daily_assessment.reset_index(drop=True)

        if cvc_status in ["No", '', np.nan]:
            # find the first cvc yes data point
            mask = daily_assessment['central_venous_catheter'].isin(pd.Series(['New', 'Insitu']))
            try:
                # check that the point exists
                idx = next(iter(mask.index[mask]), 'not exist')
                # set the cvc status as cvc
                cvc_status = daily_assessment["central_venous_catheter"].iloc[idx]
                # set the cvc date as datetime
                cvc_start_date = daily_assessment["date"].iloc[idx]
                cvc_start_date = datetime.strptime(cvc_start_date, "%Y-%m-%d")
                # if cvc stat is Insitu set cvc date as a day before stated
                if cvc_status == "Insitu":
                    cvc_start_date = cvc_start_date - timedelta(days=1)
                # remove the data before we have a cvc day
                daily_assessment = daily_assessment.loc[idx:].reset_index(drop=True)
            except:
                break

        first_daily_assessment_date = daily_assessment.loc[0]['date']

        # get first three dates in datetime format
        first_daily_assessment_date = datetime.strptime(first_daily_assessment_date, "%Y-%m-%d")
        second_daily_assessment_date = first_daily_assessment_date + timedelta(days=1)
        third_daily_assessment_date = second_daily_assessment_date + timedelta(days=1)

        # get first three dates in str format
        first_daily_assessment_str = str(first_daily_assessment_date)[:10]
        second_daily_assessment_str = str(second_daily_assessment_date)[:10]
        third_daily_assessment_str = str(third_daily_assessment_date)[:10]

        day_number = (first_daily_assessment_date - cvc_start_date)
        day_number = day_number.days

        # add one because when we subtract the start and end date we exclude the start date
        days.append(day_number + 1)

        if day_number == 0 and len(daily_assessment) > 2:

            # Exclude this set of csv days if we have a record on the second day and the patient is off csv
            if len(daily_assessment.loc[(daily_assessment['date'] == second_daily_assessment_str) & (
                    daily_assessment['central_venous_catheter'] == 'No')]) < 1:

                third_day = daily_assessment.loc[
                    daily_assessment['date'] == third_daily_assessment_str]

                # Check that we have a record for the third day we cant check the nessasy critria if it is missing.
                if len(third_day) > 0:
                    clabsi_validation = (len(third_day.loc[
                                                 (third_day['temperature'] > 38) &
                                                 (third_day['type_of_culture'] == 'Blood') &
                                                 (~third_day['organism'].isin(diagnosis_list))]) +
                                         len(third_day.loc[
                                                 (third_day['type_of_culture'] == 'Blood') &
                                                 (third_day['organism'].isin(diagnosis_list))
                                                 ])) > 0

                    # check if the critira has been matched on the thrid day
                    if clabsi_validation:
                        clabsi_count += 1

                daily_assessment = daily_assessment.loc[(daily_assessment['date'] > third_daily_assessment_str)]


            else:
                cvc_status = 'No'

                # We filter daily_assessment date greater than second_daily_assessment_str because we know
                # first_daily_assessment is cvc so if we dont need to check when we loop through it again.
                # second_daily_assessment could be cvc or not but since we check we no longer need that record.
                # We cannot remoove the third daily assessment record because if the second day is no we never check
                # the cvc status for the third day
                daily_assessment = daily_assessment.loc[(daily_assessment['date'] > second_daily_assessment_str)]

        elif day_number == 1:
            third_day = daily_assessment.loc[daily_assessment['date'] == second_daily_assessment_str]

            if len(third_day) > 0:
                clabsi_validation = (len(third_day.loc[
                                             (third_day['temperature'] > 38) &
                                             (third_day['type_of_culture'] == 'Blood') &
                                             (~third_day['organism'].isin(diagnosis_list))]) +
                                     len(third_day.loc[
                                             (third_day['type_of_culture'] == 'Blood') &
                                             (third_day['organism'].isin(diagnosis_list))
                                             ])) > 0

                if clabsi_validation:
                    clabsi_count += 1

                cvc_status = daily_assessment["central_venous_catheter"].iloc[0]

            daily_assessment = daily_assessment.loc[(daily_assessment['date'] > second_daily_assessment_str)]

        elif day_number > 1:

            third_day = daily_assessment.loc[daily_assessment['date'] == first_daily_assessment_str]

            if len(third_day) > 0:
                clabsi_validation = (len(third_day.loc[
                                             (third_day['temperature'] > 38) &
                                             (third_day['type_of_culture'] == 'Blood') &
                                             (~third_day['organism'].isin(diagnosis_list))]) +
                                     len(third_day.loc[
                                             (third_day['type_of_culture'] == 'Blood') &
                                             (third_day['organism'].isin(diagnosis_list))
                                             ])) > 0

                if clabsi_validation:
                    clabsi_count += 1

                cvc_status = daily_assessment["central_venous_catheter"].iloc[0]

            daily_assessment = daily_assessment.loc[(daily_assessment['date'] > first_daily_assessment_str)]

        else:
            break

    # check for CLABSI for patietns off cvc for 24 hours
    while len(data_duplicate) > 2:
        data_duplicate = data_duplicate.reset_index(drop=True)

        mask = data_duplicate['central_venous_catheter'].isin(pd.Series(['New', 'Insitu']))
        try:
            idx = next(iter(mask.index[mask]), 'not exist')
        except:
            break

        if idx == 'not exist':
            break

        # select data after the first cvc line
        data_duplicate = data_duplicate.loc[idx:].reset_index(drop=True)

        first_daily_assessment_date = min(data_duplicate['date'].dropna())
        # if isinstance(first_date_on_cvc, float):
        #     first_date_on_cvc = data_duplicate.loc[idx]['date_of_investigation']

        last_date = max(data_duplicate['date'].dropna())
        # if isinstance(last_date, float):
        #     last_date = data_duplicate.loc[-1]['date_of_investigation']

        # get list of dates between first and last date so we can loop through and check if we have a cvc no
        dates = pd.date_range(start=first_daily_assessment_date, end=last_date).astype(str).tolist()

        # loop through avery day of daily data
        for date in dates:

            # check for a day when cvc is no to start the timer for clabsi
            if len(data_duplicate.loc[
                       (data_duplicate['date'] == date) &
                       ((data_duplicate['central_venous_catheter'] == 'No'))
                   ]) > 0:

                # get the third day after patietn is off cvc
                first_date_off_cvc = datetime.strptime(date, "%Y-%m-%d")
                second_date_off_cvc = str(first_date_off_cvc + timedelta(days=1))[:10]

                # do a clabsi check
                clabsi_validation = (len(data_duplicate.loc[
                                             ((data_duplicate['date'] == first_date_off_cvc) | (
                                                     data_duplicate['date'] == second_date_off_cvc)) &
                                             (data_duplicate['temperature'] > 38) &
                                             (data_duplicate['type_of_culture'] == 'Blood') &
                                             (data_duplicate['organism'].isin(diagnosis_list))]) +
                                     len(data_duplicate.loc[
                                             ((data_duplicate['date'] == first_date_off_cvc) | (
                                                     data_duplicate['date'] == second_date_off_cvc)) &
                                             (data_duplicate['type_of_culture'] == 'Blood') &
                                             (~data_duplicate['organism'].isin(diagnosis_list))])
                                     ) > 0

                # add CLABSI if matchers
                if clabsi_validation:
                    clabsi_count = clabsi_count + 1

                data_duplicate = data_duplicate.loc[
                    (data_duplicate['date'] > date)]

                # Look for the next day on cvc
                break

            # Look for the next day on cvc
            data_duplicate = data_duplicate.loc[
                (data_duplicate['date'] > date)]

    return {'clabsi_count': clabsi_count, 'admission_date': date_of_admission, 'days_on_x': number_cvc_days,
            'patient_id': patient_id}


def clabsi_count_for_dataset(daily_assessment, investigation):
    # data = pd.concat([daily_assessment, investigation], axis=0).sort_values(by=['patient_id'])
    available_columns = daily_assessment.columns
    available_columns = available_columns.append(investigation.columns)

    if pd.Series(['patient_id',
                  'admission_date',
                  'date_of_daily_assessment',
                  'date_of_investigation',
                  'central_venous_catheter',
                  'temperature',
                  'type_of_culture',
                  'organism']).isin(available_columns).all() and len(daily_assessment) > 0:

        # difine organism data-type so we can merge saftly
        try:
            daily_assessment[['organism', 'organism1', 'organism2']] = daily_assessment[
                ['organism', 'organism1', 'organism2']].astype(str)
            investigation[['organism', 'organism1', 'organism2']] = investigation[
                ['organism', 'organism1', 'organism2']].astype(str)

            # merge daily assessment and investigation to get all daily_entered data
            data = pd.merge(daily_assessment, investigation, how='outer',
                            left_on=['patient_id', 'date_of_daily_assessment', 'organism', 'organism1', 'organism2'],
                            right_on=['patient_id', 'date_of_investigation', 'organism', 'organism1', 'organism2'])

        except:
            data = pd.merge(daily_assessment, investigation, how='left',
                            left_on=['patient_id', 'date_of_daily_assessment'],
                            right_on=['patient_id', 'date_of_investigation'])

        # drop patients missing daily_assessment
        data = data.dropna(subset=["date_of_daily_assessment"])

        # replace string nan to nan
        data[['organism', 'organism1', 'organism2']] = data[['organism', 'organism1', 'organism2']].replace(
            'nan', np.nan, regex=True)

        data = data[
            ['patient_id',
             'admission_date',
             'date_of_daily_assessment',
             'date_of_investigation',
             'central_venous_catheter',
             'temperature',
             'type_of_culture',
             'organism'
             ]
        ]

        # data = data.dropna(subset=['date_of_daily_assessment'])
        data['admission_date'] = pd.to_datetime(data['admission_date'], format='%Y-%m-%d')
        data['admission_date'] = data['admission_date'].dt.strftime('%m/%Y')

        # create a date coloumn which combines investigation and daily assessement dates to fill and missing dates
        data['date'] = data['date_of_daily_assessment']
        data.loc[(data['date_of_daily_assessment'].isna()), 'date'] = data['date_of_investigation']

        clabsi_count_list = data.groupby('patient_id').apply(clabsi_count_for_patient).tolist()
        clabsi_dataframe = pd.DataFrame(clabsi_count_list)
        # filter patients with a cvc
        clabsi_dataframe = clabsi_dataframe[clabsi_dataframe['days_on_x'] > 0]
        clabsi_dataframe['patients_with_clabsi'] = 0
        clabsi_dataframe.loc[((clabsi_dataframe['clabsi_count'] > 0)), 'patients_with_clabsi'] = 100
        # clabsi_rate = (clabsi_dataframe['clabsi_count'].sum()/clabsi_dataframe['days_on_x'].sum()) * 100000


    else:
        clabsi_dataframe = 'No data'

    return clabsi_dataframe


def clabsi_rate_for_dataset(clabsi_dataframe):
    if isinstance(clabsi_dataframe, pd.DataFrame):

        lower_quartile_rate = clabsi_dataframe['clabsi_rate'].quantile(0.25)
        median_rate = clabsi_dataframe['clabsi_rate'].median()
        upper_quartile_rate = clabsi_dataframe['clabsi_rate'].quantile(0.75)

        quartile_range = upper_quartile_rate - lower_quartile_rate
        sixth_quartile_range = quartile_range / 6

        two_sixth = lower_quartile_rate + sixth_quartile_range
        three_sixth = lower_quartile_rate + (sixth_quartile_range * 2)
        four_sixth = lower_quartile_rate + (sixth_quartile_range * 3)
        five_sixth = lower_quartile_rate + (sixth_quartile_range * 4)

        mean = clabsi_dataframe['clabsi_rate'].mean()

    else:
        median_rate = 'No data'
        lower_quartile_rate = 'No data'
        two_sixth = 'No data'
        three_sixth = 'No data'
        four_sixth = 'No data'
        five_sixth = 'No data'
        sixth_quartile_range = 'No data'
        mean = ''

    return {'value': median_rate, 'min': lower_quartile_rate, 'twosixth': two_sixth, 'threesixth': three_sixth,
            'foursixth': four_sixth, 'fivesixth': five_sixth, 'max': sixth_quartile_range, 'mean': mean}


def ivac_count_for_patient(daily_assessment):
    # reset index
    daily_assessment = daily_assessment.reset_index(drop=True)

    daily_assessment['fio2_diff'] = daily_assessment['fraction_inspired_oxygen'].diff()
    daily_assessment['peep_diff'] = daily_assessment['partial_pressure_arterial_oxygen'].diff()
    # patientId = daily_assessment["patient_id"].iloc[0]
    admission_date = daily_assessment['admission_date'].iloc[0]
    full_admission_date = daily_assessment['date_of_admission'].iloc[0]
    eligible_patient = len(daily_assessment.loc[daily_assessment['mechanically_ventilated'] == 'mechanical_vent'])
    ivac_count = 0
    mec_vent_stat = ''

    while len(daily_assessment) > 2:

        daily_assessment = daily_assessment.reset_index(drop=True)

        if mec_vent_stat in ["No", '', np.nan]:
            # find the first mec vent  data point
            mask = ((daily_assessment['mechanically_ventilated'] == 'mechanical_vent') &
                    (daily_assessment['date_of_daily_assessment'] != full_admission_date))
            try:
                # check that the point exists
                idx = next(iter(mask.index[mask]), 'not exist')
                daily_assessment = daily_assessment.iloc[idx:].reset_index(drop=True)
            except:
                break

        # get the important dates
        first_date_mec_vent = daily_assessment.loc[0]['date_of_daily_assessment']
        first_date_mec_vent_datetime = datetime.strptime(first_date_mec_vent, "%Y-%m-%d")
        second_date_mec_vent = str(first_date_mec_vent_datetime + timedelta(days=1))[:10]
        third_date_mec_vent = str(first_date_mec_vent_datetime + timedelta(days=2))[:10]

        # get the peep/fio2 data for the second day mec vent
        first_day_df = daily_assessment.loc[daily_assessment['date_of_daily_assessment'] == first_date_mec_vent]

        # Set the peep/fio2 stats depending on there diff value
        peep_diff = len(first_day_df[first_day_df['peep_diff'] <= 0])
        fio2_diff = len(first_day_df[first_day_df['fio2_diff'] <= 0])

        if (peep_diff > 0) & (fio2_diff > 0):
            peep_stat = True
            fio2_stat = True
        elif peep_diff > 0:
            peep_stat = True
            fio2_stat = False
        elif fio2_diff > 0:
            fio2_stat = True
            peep_stat = False
        else:
            peep_stat = False
            fio2_stat = False

        if (peep_stat) or (fio2_stat):

            second_day_df = daily_assessment.loc[daily_assessment['date_of_daily_assessment'] == second_date_mec_vent]

            # Set the peep/fio2 stats depending on there diff value
            peep_diff = len(second_day_df[second_day_df['peep_diff'] <= 0])
            fio2_diff = len(second_day_df[second_day_df['fio2_diff'] <= 0])

            if (peep_diff > 0 & peep_stat) and (fio2_diff > 0 & fio2_stat):
                peep_stat = True
                fio2_stat = True
            elif (peep_diff > 0 & peep_stat):
                peep_stat = True
                fio2_stat = False
            elif (fio2_diff > 0 & fio2_stat):
                fio2_stat = True
                peep_stat = False
            else:
                peep_stat = False
                fio2_stat = False

            if (len(second_day_df.loc[(second_day_df['mechanically_ventilated'] == 'mechanical_vent')]) > 0) & (
                    (peep_stat) | (fio2_stat)):

                ivac_validation = len(daily_assessment.loc[
                                          (daily_assessment['date_of_daily_assessment'] == third_date_mec_vent) &
                                          (daily_assessment['temperature'] > 38) &
                                          (daily_assessment['antibiotics'] == 'Yes') &
                                          (((daily_assessment['fio2_diff'] >= 0.2) & (fio2_stat)) |
                                           ((daily_assessment['peep_diff'] >= 3) & (peep_stat)))
                                          ]) > 0

                if ivac_validation:
                    ivac_count += 1

        daily_assessment = daily_assessment.loc[daily_assessment['date_of_daily_assessment'] > first_date_mec_vent]

    return {'ivac_count': ivac_count, 'admission_date': admission_date, 'days_on_x': eligible_patient}


def ivac_count_for_dataset(daily_assessment, admission_assessment):
    if pd.Series(['patient_id',
                  'admission_date',
                  'date_of_daily_assessment',
                  'central_venous_catheter',
                  'temperature',
                  'fraction_inspired_oxygen',
                  'partial_pressure_arterial_oxygen',
                  'antibiotics',
                  'mechanically_ventilated']).isin(daily_assessment.columns).all() and len(daily_assessment) > 0:
        daily_assessment = daily_assessment[
            ['patient_id',
             'admission_date',
             'date_of_daily_assessment',
             'temperature',
             'fraction_inspired_oxygen',
             'partial_pressure_arterial_oxygen',
             'antibiotics',
             'mechanically_ventilated']
        ]

        # daily_assessment = daily_assessment.dropna(subset=['date_of_daily_assessment'])
        # daily_assessment['admission_date'] = pd.to_datetime(daily_assessment['admission_date'], format='%Y-%m-%d')
        # daily_assessment['date_of_admission'] = daily_assessment['admission_date'].dt.strftime('%Y-%m-%d')
        # daily_assessment['admission_date'] = daily_assessment['admission_date'].dt.strftime('%m/%Y')

        admission_assessment = admission_assessment[
            ['patient_id', 'admission.date_of_admission', 'admissionAssessment.fraction_inspired_oxygen',
             'admissionAssessment.partial_pressure_arterial_oxygen', 'admissionAssessment.mechanically_ventilated',
             'admissionAssessment.temperature', 'admissionAssessment.antibiotics']]
        admission_assessment = admission_assessment.rename(
            columns={"admission.date_of_admission": "date_of_daily_assessment",
                     "admissionAssessment.fraction_inspired_oxygen": "fraction_inspired_oxygen",
                     'admissionAssessment.partial_pressure_arterial_oxygen': 'partial_pressure_arterial_oxygen',
                     'admissionAssessment.temperature': 'temperature',
                     'admissionAssessment.antibiotics': 'antibiotics',
                     'admissionAssessment.mechanically_ventilated': 'mechanically_ventilated'})

        try:
            admission_assessment['date_of_daily_assessment'] = admission_assessment[
                'date_of_daily_assessment'].dt.strftime('%Y-%m-%d')
        except:
            pass
        admission_assessment['admission_date'] = admission_assessment['date_of_daily_assessment']

        daily_assessment = pd.concat([admission_assessment, daily_assessment], axis=0, ignore_index=True)

        daily_assessment = daily_assessment.dropna(subset=['date_of_daily_assessment'])
        daily_assessment['admission_date'] = pd.to_datetime(daily_assessment['admission_date'], format='%Y-%m-%d')
        daily_assessment['date_of_admission'] = daily_assessment['admission_date'].dt.strftime('%Y-%m-%d')
        daily_assessment['admission_date'] = daily_assessment['admission_date'].dt.strftime('%m/%Y')

        if len(daily_assessment.dropna(subset=['fraction_inspired_oxygen', 'partial_pressure_arterial_oxygen'])) > 0:
            ivac_count_list = daily_assessment.groupby('patient_id').apply(ivac_count_for_patient)
            ivac_count_list = ivac_count_list.tolist()
            ivac_dataframe = pd.DataFrame(ivac_count_list)
            # select patients with a mech vent
            ivac_dataframe = ivac_dataframe[ivac_dataframe['days_on_x'] > 0]
            ivac_dataframe['patients_with_ivac'] = 0
            ivac_dataframe.loc[((ivac_dataframe['ivac_count'] > 0)), 'patients_with_ivac'] = 100
            # ivac_dataframe['ivac_rate'] = (ivac_dataframe['ivac_count']/ivac_dataframe['days_on_x']) * 1000

        else:
            ivac_dataframe = 'No data'

    else:
        ivac_dataframe = 'No data'

    return ivac_dataframe


def ivac_rate_for_dataset(daily_assessment, ivac_dataframe):
    if isinstance(ivac_dataframe, pd.DataFrame) and 'mechanically_ventilated' in daily_assessment:

        lower_quartile_rate = ivac_dataframe['ivac_rate'].quantile(0.25)
        median_rate = ivac_dataframe['ivac_rate'].median()
        upper_quartile_rate = ivac_dataframe['ivac_rate'].quantile(0.75)

        quartile_range = upper_quartile_rate - lower_quartile_rate
        sixth_quartile_range = quartile_range / 6

        two_sixth = lower_quartile_rate + sixth_quartile_range
        three_sixth = lower_quartile_rate + (sixth_quartile_range * 2)
        four_sixth = lower_quartile_rate + (sixth_quartile_range * 3)
        five_sixth = lower_quartile_rate + (sixth_quartile_range * 4)

    else:
        median_rate = 'No data'
        lower_quartile_rate = 'No data'
        two_sixth = 'No data'
        three_sixth = 'No data'
        four_sixth = 'No data'
        five_sixth = 'No data'
        sixth_quartile_range = 'No data'

    return {'value': median_rate, 'min': lower_quartile_rate, 'twosixth': two_sixth, 'threesixth': three_sixth,
            'foursixth': four_sixth, 'fivesixth': five_sixth, 'max': sixth_quartile_range}


def percentage_change(rate_previous_month, rate):
    if isinstance(rate, Number) and isinstance(rate_previous_month, Number):

        if (rate > rate_previous_month) & (rate_previous_month > 0):
            percentage_change_int = 100 * (rate - rate_previous_month) / rate_previous_month
            percentage_change_str = f'{str(round(percentage_change_int, 1))}%'

        elif (rate > rate_previous_month) & (rate_previous_month == 0):
            percentage_change_int = 1
            percentage_change_str = f'100%'

        elif rate < rate_previous_month:
            percentage_change_int = 100 * (rate_previous_month - rate) / rate_previous_month
            percentage_change_str = f'{str(round(percentage_change_int, 1))}%'
            percentage_change_int = -1

        elif rate == rate_previous_month:
            percentage_change_int = 0
            percentage_change_str = 'No change'
        else:
            percentage_change_int = 1
            percentage_change_str = 'inf'

        if percentage_change_int > 0:
            return {'turnOver': percentage_change_str, 'icon': '&#9650;', 'color': 'green'}

        elif percentage_change_int < 0:
            return {'turnOver': percentage_change_str, 'icon': '&#9660;', 'color': 'red'}

        elif percentage_change_int == 0:
            return {'turnOver': percentage_change_str, 'icon': '', 'color': 'green'}

        else:
            return {'turnOver': percentage_change_str, 'icon': '&#9650;', 'color': 'green'}


    elif isinstance(rate, Number) and rate > 0:

        return {'turnOver': '100%', 'icon': '&#9650;', 'color': 'green'}

    elif isinstance(rate_previous_month, Number) and rate_previous_month > 0:

        return {'turnOver': '100%', 'icon': '&#9660;', 'color': 'red'}

    else:

        return {'turnOver': 'No data', 'icon': '', 'color': 'green'}


def icuTurnOver(numberOfAdmission, numberOfBeds):
    try:
        turnOver = round(numberOfAdmission / int(numberOfBeds['count']), 1)
    except:
        turnOver = 'No data'
    return turnOver


def readmission(data):
    columns_required = ['admission.readmission', 'admission.date_of_pre_discharge',
                        'admission.date_of_admission_hospital', 'admission.admission_type']
    if pd.Series(columns_required).isin(data.columns).all():

        data = data.loc[data['admission.readmission'] == 'Yes']
        data = data.loc[data['admission.admission_type'] == 'Unplanned']

        data['datetime_admission'] = pd.to_datetime(
            data['admission.date_of_admission'].astype(str) + ' ' + data['admission.time_of_admission'].astype(str),
            errors='coerce')
        data['admission.date_of_pre_discharge'] = pd.to_datetime(data['admission.date_of_pre_discharge'],
                                                                 format='%Y-%m-%d')

        data = data.dropna(subset=['datetime_admission', 'admission.date_of_pre_discharge'])

        if len(data) > 0:
            time_to_readmission = (data['datetime_admission'] - data['admission.date_of_pre_discharge']).dt.days
            number_of_readmission = round(int((time_to_readmission <= 2).sum()))

        else:
            number_of_readmission = 'No data'
    else:
        number_of_readmission = 'No data'

    return number_of_readmission


def patient_id_length_of_stay_greater_then(admission_data, length_of_stay):
    # if no discharge date get it to today.
    admission_data.loc[
        admission_data['discharge.date_of_discharge'].isna(), 'discharge.date_of_discharge'] = datetime.now().strftime(
        '%Y-%m-%d')

    # get discharge date
    if len(admission_data['discharge.date_of_discharge'].dropna()) > 0:

        # convert admission and discharge dates to datetime type
        admission_data[['discharge.date_of_discharge', 'admission.date_of_admission']] = admission_data[
            ['discharge.date_of_discharge', 'admission.date_of_admission']].apply(pd.to_datetime, format='%Y-%m-%d',
                                                                                  errors='coerce')
        # Drop patients with wrongly formatted dates
        admission_data = admission_data[
            admission_data[['discharge.date_of_discharge', 'admission.date_of_admission']].notnull().all(1)]

        # Get number of days between admission and discharge dates
        admission_data["length_of_stay"] = (admission_data['discharge.date_of_discharge'] - admission_data[
            'admission.date_of_admission']).dt.days

        # find patients who should have at least 3 daily_assessment
        patients_with_los_greater_then_zero = admission_data.loc[admission_data["length_of_stay"] > length_of_stay]
        patient_id_eligible_for_hai = patients_with_los_greater_then_zero["patient_id"].unique()

    else:
        patient_id_eligible_for_hai = []

    return patient_id_eligible_for_hai


def single_variable_completeness(data, columns, name_drop=['']):
    number_records = len(data)
    completeness_list = []
    completeness_not_recorded_list = []
    for column in columns:
        column_name = column
        for name in name_drop:
            if name in column_name:
                column_name = column_name.replace(name, '', 1)
        column_name = column_name.replace('_', ' ')
        column_name = column_name.lstrip()
        column_name = column_name.capitalize()
        if column in data:
            col = data[column]
            number_not_filled_branching_logic = len(col.loc[col == 'filled'])
            if number_not_filled_branching_logic != number_records:
                number_na = data[column].isna().sum().item()
                number_records_after_branching_logic = number_records - number_not_filled_branching_logic
                number_records_filled = number_records_after_branching_logic - number_na
                per = round((number_records_filled / number_records_after_branching_logic) * 100, 1)

                completeness_record = {'name': column_name, 'completeness': per}
                completeness_list.append(completeness_record)

            else:
                completeness_record = {'name': column_name, 'completeness': 'No data'}
                completeness_not_recorded_list.append(completeness_record)

        else:
            completeness_not_recorded_list.append({'name': column_name, 'completeness': 'No data'})

    sorted_completeness_list = sorted(completeness_list, key=itemgetter('completeness'), reverse=True)
    full_completeness_list = sorted_completeness_list + completeness_not_recorded_list

    return full_completeness_list


def create_index_for_daily_data_to_get_completeness(admission_data):
    if 'admission.date_of_admission' in admission_data:
        admission_data = admission_data[['admission.date_of_admission',
                                         'patient_id',
                                         'admission.date_of_admission_hospital',
                                         'discharge.date_of_discharge',
                                         'admission.sari']]

        admission_data.loc[admission_data[
                               'admission.date_of_admission'].isna(), 'admission.date_of_admission'] = 'admission.date_of_admission_hospital'

    else:
        admission_data['admission.date_of_admission'] = admission_data['admission.date_of_admission_hospital']

    admission_data.loc[
        admission_data['discharge.date_of_discharge'].isna(), 'discharge.date_of_discharge'] = datetime.now().strftime(
        '%Y-%m-%d')

    admission_data['discharge.date_of_discharge'] = pd.to_datetime(admission_data['discharge.date_of_discharge'],
                                                                   format='%Y-%m-%d')
    admission_data['admission.date_of_admission'] = pd.to_datetime(admission_data['admission.date_of_admission'],
                                                                   format='%Y-%m-%d')
    admission_data = admission_data.set_index('admission.date_of_admission')
    new_df = pd.DataFrame()
    for i, data in admission_data.iterrows():
        data = data.to_frame().transpose()
        data = data.reindex(pd.date_range(start=data.index[0], end=data['discharge.date_of_discharge'][0])).fillna(
            method='ffill').reset_index().rename(columns={'index': 'date_of_assessment'})
        new_df = pd.concat([new_df, data])

    new_df = new_df[['date_of_assessment',
                     'patient_id',
                     'discharge.date_of_discharge',
                     'admission.sari']]

    new_df['date_of_assessment'] = new_df['date_of_assessment'].dt.strftime('%Y-%m-%d')
    new_df['discharge.date_of_discharge'] = new_df['discharge.date_of_discharge'].dt.strftime('%Y-%m-%d')

    return new_df


def get_completeness_per(data):
    completeness = round((data['number_of_entries_filled'] / data['total_number_of_entries']) * 100, 1)
    return completeness
