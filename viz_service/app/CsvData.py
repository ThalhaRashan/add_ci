import zipfile
from io import BytesIO

import numpy as np
import pandas as pd
from flask_restful import Resource
from flask import request, send_file
from pandas.io.json import json_normalize
from .HttpCall import get_all_patients, get_all_patients_de_identified
from .shared_functions import merge_different_age_columns_into_one


def filter_for_month(data, column, fromD, toD, column_two, fromDate, toDate):
    """This function gets a user input month and gets the start date of the month by adding -01 and the last day of
    of the month by using calendar.monthrange which gives the end date of the month given a month and year it then
    takes the data given and filters it based on the column specified using the start and and end  """

    if fromD != 'Invalid Date' and fromDate != 'Invalid Date':
        data = data[((data[column] >= fromD) | (data[column_two] >= fromDate)) &
                    ((data[column] <= toD) | (data[column_two] <= toDate))]

    elif fromD != 'Invalid Date':
        data = data[(data[column] >= fromD) & (data[column] <= toD)]

    elif fromDate != 'Invalid Date':
        data = data[(data[column_two] >= fromDate) & (data[column_two] <= toDate)]

    return data



def data_this_month(patients, fromDate, toDate, fromDateHospital, toDateHospital, is_de_identified=False):
    """Takes json input and flattens the first nested layer of data and filters by 'A' month"""
    normalized_data = json_normalize(patients)
    num = [1] * len(normalized_data)
    normalized_data['num'] = num

    if (is_de_identified):
        normalized_data = normalized_data.drop(
            columns=['sariDailyAssessments', 'dailyAssessments', 'postQols', 'preQol', 'investigations', 'notes',
                     'observations', 'tracker', 'visits', 'admission.patient_name', 'admission.nic_number',
                     'admission.contact_number'])
    else:
        normalized_data = normalized_data.drop(
            columns=['sariDailyAssessments', 'dailyAssessments', 'postQols', 'preQol', 'investigations', 'notes',
                     'observations', 'tracker', 'visits'])

    normalized_data = filter_for_month(normalized_data, 'admission.date_of_admission', fromDate, toDate, 'admission.date_of_admission_hospital', fromDateHospital, toDateHospital)

    normalized_data = merge_different_age_columns_into_one(normalized_data)

    csv = normalized_data

    return csv


def get_daily_assessment_data(patients, fromDate, endDate, fromDateHospital, toDateHospital):
    assessment_list = []
    list_unique_id = []
    list_admission_date = []
    list_admission_type = []
    list_hospital_admission_date = []

    for patient in patients:
        if len(patient['dailyAssessments']) > 0:
            for assessment in patient['dailyAssessments']:
                unique_id = patient['admission']['patient_id']
                try:
                    admission_date = patient['admission']['date_of_admission']
                except:
                    admission_date = np.nan
                try:
                    hospital_admission_date = patient['admission']['date_of_admission_hospital']
                except:
                    hospital_admission_date = np.nan
                admission_type = patient['admission']['admission_type']
                if type(assessment) == dict:
                    assessment_list.append(assessment)
                    list_unique_id.append(unique_id)
                    list_admission_date.append(admission_date)
                    list_hospital_admission_date.append(hospital_admission_date)
                    list_admission_type.append(admission_type)
                elif type(assessment) == list:
                    for x in assessment:
                        assessment_list.append(x)
                        list_unique_id.append(unique_id)
                        list_admission_date.append(admission_date)
                        list_hospital_admission_date.append(hospital_admission_date)
                        list_admission_type.append(admission_type)

    if len(assessment_list) > 0:
        data = pd.DataFrame(assessment_list)
        data['patient_id'] = list_unique_id
        data['admission_date'] = list_admission_date
        data['hospital_admission_date'] = list_hospital_admission_date
        data['admission.admission_type'] = list_admission_type
        data_for_month = filter_for_month(data, 'admission_date', fromDate, endDate, 'hospital_admission_date', fromDateHospital, toDateHospital)
        data_for_month['admission_date'] = pd.to_datetime(data_for_month['admission_date'],
                                                          format='%Y-%m-%d', errors='coerce')
        data_for_month = data_for_month[pd.notnull(data_for_month['admission_date'])]
        data_for_month['admission_date'] = data_for_month['admission_date'].dt.strftime('%Y-%m-%d')
        data_for_month = data_for_month.replace('', np.nan)
        data_for_month = data_for_month

    else:
        return pd.DataFrame()

    return data_for_month


def get_investigation_data(patients, fromDate, endDate, fromDateHospital, toDateHospital):
    investigation_list = []
    list_unique_id = []
    list_admission_date = []
    list_hospital_admission_date = []

    for patient in patients:
        if len(patient['dailyAssessments']) > 0:
            for assessment in patient['investigations']:
                unique_id = patient['admission']['patient_id']
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
                elif type(assessment) == list:
                    for x in assessment:
                        investigation_list.append(x)
                        list_unique_id.append(unique_id)
                        list_admission_date.append(admission_date)
                        list_hospital_admission_date.append(hospital_admission_date)

    if len(investigation_list) > 0:
        data = pd.DataFrame(investigation_list)
        data['patient_id'] = list_unique_id
        data['admission_date'] = list_admission_date
        data['hospital_admission_date'] = list_hospital_admission_date
        data_for_month = filter_for_month(data, 'admission_date', fromDate, endDate, 'hospital_admission_date', fromDateHospital, toDateHospital)
        data_for_month['date_of_investigation'] = pd.to_datetime(data_for_month['date_of_investigation'],
                                                                 format='%Y-%m-%d', errors='coerce')
        data_for_month = data_for_month.loc[pd.notnull(data_for_month['date_of_investigation'])]
        data_for_month['date_of_investigation'] = data_for_month['date_of_investigation'].dt.strftime('%Y-%m-%d')
        data_for_month = data_for_month.replace('', np.nan)
        data_for_month = data_for_month

    else:
        return pd.DataFrame()

    return data_for_month


def get_sari_qi_data(patients, fromDate, toDate, fromDateHospital, toDateHospital):
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
        data['admission_date'] = list_admission_date
        data['hospital_admission_date'] = list_hospital_admission_date
        data['unitId'] = list_unit_id
        data_for_month = filter_for_month(data, 'admission_date', fromDate, toDate, 'hospital_admission_date', fromDateHospital, toDateHospital)
        data_for_month['admission_date'] = pd.to_datetime(data_for_month['admission_date'],
                                                          format='%Y-%m-%d', errors='coerce')
        data_for_month = data_for_month[pd.notnull(data_for_month['admission_date'])]
        data_for_month['admission_date'] = data_for_month['admission_date'].dt.strftime('%Y-%m-%d')
        data_for_month = data_for_month.replace('', np.nan)

    else:
        return pd.DataFrame()

    return data_for_month


def get_post_qol_data(patients, fromDate, toDate, fromDateHospital, toDateHospital):
    assessment_list = []
    list_unique_id = []
    list_admission_date = []
    list_unit_id = []
    list_hospital_admission_date = []

    for patient in patients:
        if 'postQols' in patient:
            if len(patient['postQols']) > 0:
                for assessment in patient['postQols']:
                    unique_id = patient['admission']['patient_id']
                    try:
                        admission_date = patient['admission']['date_of_admission']
                    except:
                        admission_date = ''
                    try:
                        hospital_admission_date = patient['admission']['date_of_admission_hospital']
                    except:
                        hospital_admission_date = ''
                    unitId = patient['unitId']
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
        data['admission_date'] = list_admission_date
        data['hospital_admission_date'] = list_hospital_admission_date
        data['unitId'] = list_unit_id
        data_for_month = filter_for_month(data, 'admission_date', fromDate, toDate, 'hospital_admission_date', fromDateHospital, toDateHospital)
        data_for_month['admission_date'] = pd.to_datetime(data_for_month['admission_date'],
                                                          format='%Y-%m-%d', errors='coerce')
        data_for_month = data_for_month[pd.notnull(data_for_month['admission_date'])]
        data_for_month['admission_date'] = data_for_month['admission_date'].dt.strftime('%Y-%m-%d')
        data_for_month = data_for_month.replace('', np.nan)

    else:
        return pd.DataFrame()

    return data_for_month


def get_pre_qol_data(patients, fromDate, toDate, fromDateHospital, toDateHospital):
    assessment_list = []
    list_unique_id = []
    list_admission_date = []
    list_unit_id = []
    list_hospital_admission_date = []

    for patient in patients:
        if 'preQol' in patient:
            if len(patient['preQol']) > 0:
                for assessment in patient['preQol']:
                    unique_id = patient['admission']['patient_id']
                    try:
                        admission_date = patient['admission']['date_of_admission']
                    except:
                        admission_date = ''
                    try:
                        hospital_admission_date = patient['admission']['date_of_admission_hospital']
                    except:
                        hospital_admission_date = ''
                    unitId = patient['unitId']
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
        data['admission_date'] = list_admission_date
        data['hospital_admission_date'] = list_hospital_admission_date
        data['unitId'] = list_unit_id
        data_for_month = filter_for_month(data, 'admission_date', fromDate, toDate, 'hospital_admission_date', fromDateHospital, toDateHospital)
        data_for_month['admission_date'] = pd.to_datetime(data_for_month['admission_date'],
                                                          format='%Y-%m-%d', errors='coerce')
        data_for_month = data_for_month[pd.notnull(data_for_month['admission_date'])]
        data_for_month['admission_date'] = data_for_month['admission_date'].dt.strftime('%Y-%m-%d')
        data_for_month = data_for_month.replace('', np.nan)

    else:
        return pd.DataFrame()

    return data_for_month


def get_notes_data(patients, fromDate, toDate, fromDateHospital, toDateHospital):
    assessment_list = []
    list_unique_id = []
    list_admission_date = []
    list_unit_id = []
    list_hospital_admission_date = []

    for patient in patients:
        if len(patient['notes']) > 0:
            for assessment in patient['notes']:
                unique_id = patient['admission']['patient_id']
                try:
                    admission_date = patient['admission']['date_of_admission']
                except:
                    admission_date = ''
                try:
                    hospital_admission_date = patient['admission']['date_of_admission_hospital']
                except:
                    hospital_admission_date = ''
                unitId = patient['unitId']
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
        data['admission_date'] = list_admission_date
        data['hospital_admission_date'] = list_hospital_admission_date
        data['unitId'] = list_unit_id
        data_for_month = filter_for_month(data, 'admission_date', fromDate, toDate, 'hospital_admission_date', fromDateHospital, toDateHospital)
        data_for_month['admission_date'] = pd.to_datetime(data_for_month['admission_date'],
                                                          format='%Y-%m-%d', errors='coerce')
        data_for_month = data_for_month[pd.notnull(data_for_month['admission_date'])]
        data_for_month['admission_date'] = data_for_month['admission_date'].dt.strftime('%Y-%m-%d')
        data_for_month = data_for_month.replace('', np.nan)

    else:
        return pd.DataFrame()

    return data_for_month


class CsvData(Resource):

    def post(self):
        unit_id = request.form.get("unitId")
        isDeIdentified = request.form.get("isDeIdentified")
        fromDate = request.form.get("fromDate")
        toDate = request.form.get("toDate")
        fromDateHospital = request.form.get("FromDateHospital")
        toDateHospital = request.form.get("ToDateHospital")

        forms = []
        forms_left = True
        form_count = 0
        while forms_left:
            form = request.form.get(f'forms[{form_count}]')
            if form:
                forms.append(form)
                form_count += 1
            else:
                forms_left = False


        if (isDeIdentified == 'true'):
            isDeIdentified = True
        else:
            isDeIdentified = False

        folder_name = "data.zip"

        if (isDeIdentified):
            json_data = get_all_patients_de_identified('unitId', unit_id)

        else:
            json_data = get_all_patients('unitId', unit_id)



        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            if 'Core data' in forms:
                data = data_this_month(json_data, fromDate, toDate, fromDateHospital, toDateHospital,
                                       isDeIdentified).to_csv(index=False, compression='zip')
                zf.writestr('admission_data.csv', data)

            if 'QI' in forms:
                daily_data = get_daily_assessment_data(json_data, fromDate, toDate, fromDateHospital,
                                                       toDateHospital).to_csv(index=False, compression='zip')
                zf.writestr('daily_assessment_data.csv', daily_data)

            if 'Investigations' in forms:
                investigation_data = get_investigation_data(json_data, fromDate, toDate, fromDateHospital,
                                                            toDateHospital).to_csv(index=False, compression='zip')
                zf.writestr('investigation_data.csv', investigation_data)

            if 'SARI QI' in forms:
                sari_qi_data = get_sari_qi_data(json_data, fromDate, toDate, fromDateHospital, toDateHospital).to_csv(
                    index=False, compression='zip')
                zf.writestr('sari_qi_data.csv', sari_qi_data)

            if 'Post QOL' in forms:
                post_qol_data = get_post_qol_data(json_data, fromDate, toDate, fromDateHospital, toDateHospital).to_csv(
                    index=False, compression='zip')
                zf.writestr('post_qol_data.csv', post_qol_data)

            if 'Pre QOL' in forms:
                pre_qol_data = get_pre_qol_data(json_data, fromDate, toDate, fromDateHospital, toDateHospital).to_csv(
                    index=False, compression='zip')
                zf.writestr('pre_qol_data.csv', pre_qol_data)

            if 'Notes' in forms:
                notes = get_notes_data(json_data, fromDate, toDate, fromDateHospital, toDateHospital).to_csv(
                    index=False, compression='zip')
                zf.writestr('notes.csv', notes)

        memory_file.seek(0)
        return send_file(memory_file, attachment_filename=folder_name, as_attachment=True)

