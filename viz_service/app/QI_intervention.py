import calendar
from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta
from flask import request
from flask_restful import Resource
from .HttpCall import get_all_patients
from .constants import qi_intervention_no_data
from .shared_functions import get_qi_data, \
    get_investigation_data, \
    get_admission_data, \
    clauti_count_for_dataset, \
    clabsi_count_for_dataset, \
    ivac_count_for_dataset, \
    patient_id_length_of_stay_greater_then, \
    percentage_change


class QIIntervention(Resource):

    def post(self):

        unit_id = request.form.get("unitId")
        date_range = request.form.get("month")

        if len(date_range) == 23:

            # get the data for the previous month
            start_date, end_date = date_range.split(' - ')
            start_date = datetime.strptime(start_date, '%d/%m/%Y')

            start_date_previous_month = start_date - relativedelta(months=1)
            end_date_previous_month = start_date - relativedelta(days=1)
            start_date_previous_month = datetime.strftime(start_date_previous_month, '%d/%m/%Y')
            end_date_previous_month = datetime.strftime(end_date_previous_month, '%d/%m/%Y')
            date_range_previous_month = f'{start_date_previous_month} - {end_date_previous_month}'

        elif len(date_range) == 7:
            year, month = date_range.split('-')
            year = int(year)
            month = int(month)
            end_day = calendar.monthrange(year, month)[1]
            start_date = date_range + '-01'
            end_date = date_range + '-' + str(end_day)

            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            start_date_previous_month = start_date - relativedelta(months=1)
            end_date_previous_month = start_date - relativedelta(days=1)

            start_date = datetime.strftime(start_date, '%d/%m/%Y')
            start_date_previous_month = datetime.strftime(start_date_previous_month, '%d/%m/%Y')
            end_date_previous_month = datetime.strftime(end_date_previous_month, '%d/%m/%Y')

            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = datetime.strftime(end_date, '%d/%m/%Y')

            date_range = f'{start_date} - {end_date}'
            date_range_previous_month = f'{start_date_previous_month} - {end_date_previous_month}'



        json_patient_data = get_all_patients('unitId', unit_id)

        unit_daily_data = get_qi_data(json_patient_data, date_range)
        unit_daily_data_previous_month = get_qi_data(json_patient_data, date_range_previous_month)
        if len(unit_daily_data) > 0 or len(unit_daily_data_previous_month) > 0:

            patients_with_daily_assessment = unit_daily_data['patient_id'].unique()

            admission_data = get_admission_data(json_patient_data, date_range)
            unit_investigation_data = get_investigation_data(json_patient_data, date_range)

            # get list of patients ids with length of stay greater then 2
            eligible_patient_ids = patient_id_length_of_stay_greater_then(admission_data, 2)
            # find patients eligible and with a daily assesment
            eligible_patient_ids = [x for x in eligible_patient_ids if x in patients_with_daily_assessment]

            # filter admision_data to only include patients with a daily_assessment
            admission_data = admission_data[admission_data["patient_id"].isin(eligible_patient_ids)]
            unit_daily_data = unit_daily_data[unit_daily_data["patient_id"].isin(eligible_patient_ids)]

            if 'patient_id' in unit_investigation_data:
                unit_investigation_data = unit_investigation_data[unit_investigation_data["patient_id"].isin(eligible_patient_ids)]


            clabsi_dataset = clabsi_count_for_dataset(unit_daily_data, unit_investigation_data)
            if isinstance(clabsi_dataset, pd.DataFrame):
                eligible_clabsi_patients = len(clabsi_dataset)
                per_clabsi_patients = round(clabsi_dataset['patients_with_clabsi'].mean(), 1)
                clabsi_rate = round((clabsi_dataset['clabsi_count'].sum()/clabsi_dataset['days_on_x'].sum()) * 1000, 2)
            else:
                eligible_clabsi_patients = 'No data'
                per_clabsi_patients = 'No data'
                clabsi_rate = 'No data'


            clauti_dataset = clauti_count_for_dataset(unit_daily_data, unit_investigation_data)
            if isinstance(clauti_dataset, pd.DataFrame):
                eligible_clauti_patients = len(clauti_dataset)
                per_clauti_patients = round(clauti_dataset['patients_with_clauti'].mean(), 1)
                clauti_rate = round((clauti_dataset['clauti_count'].sum() / clauti_dataset['days_on_x'].sum()) * 1000, 2)
            else:
                eligible_clauti_patients = 'No data'
                per_clauti_patients = 'No data'
                clauti_rate = 'No data'


            ivac_dataset = ivac_count_for_dataset(unit_daily_data, admission_data)
            if isinstance(ivac_dataset, pd.DataFrame):
                eligible_ivac_patients = len(ivac_dataset)
                per_ivac_patients = round(ivac_dataset['patients_with_ivac'].mean(), 1)
                ivac_rate = round((ivac_dataset['ivac_count'].sum() / ivac_dataset['days_on_x'].sum()) * 1000, 2)
            else:
                eligible_ivac_patients = 'No data'
                per_ivac_patients = 'No data'
                ivac_rate = 'No data'



            patients_with_daily_assessment = unit_daily_data_previous_month['patient_id'].unique()

            admission_data_previous_month = get_admission_data(json_patient_data, date_range_previous_month)
            unit_investigation_data_previous_month = get_investigation_data(json_patient_data, date_range_previous_month)

            # get list of patients ids with length of stay greater then 2
            eligible_patient_ids = patient_id_length_of_stay_greater_then(admission_data_previous_month, 2)
            # find patients eligible and with a daily assesment
            eligible_patient_ids = [x for x in eligible_patient_ids if x in patients_with_daily_assessment]

            # filter admision_data to only include patients with a daily_assessment
            admission_data_previous_month = admission_data_previous_month[admission_data_previous_month["patient_id"].isin(eligible_patient_ids)]
            unit_daily_data_previous_month = unit_daily_data_previous_month[unit_daily_data_previous_month["patient_id"].isin(eligible_patient_ids)]
            if 'patient_id' in unit_investigation_data_previous_month:
                unit_investigation_data_previous_month = unit_investigation_data_previous_month[
                unit_investigation_data_previous_month["patient_id"].isin(eligible_patient_ids)]


            clabsi_dataset_previous_month = clabsi_count_for_dataset(unit_daily_data_previous_month, unit_investigation_data_previous_month)
            if isinstance(clabsi_dataset_previous_month, pd.DataFrame):
                per_clabsi_patients_previous_month = round(clabsi_dataset_previous_month['patients_with_clabsi'].mean(), 1)
                clabsi_rate_previous_month = round((clabsi_dataset_previous_month['clabsi_count'].sum()/clabsi_dataset_previous_month['days_on_x'].sum()) * 1000, 2)

            else:
                per_clabsi_patients_previous_month = 'No data'
                clabsi_rate_previous_month = 'No data'


            clauti_dataset_previous_month = clauti_count_for_dataset(unit_daily_data_previous_month, unit_investigation_data_previous_month)
            if isinstance(clauti_dataset_previous_month, pd.DataFrame):
                per_clauti_patients_previous_month = round(clauti_dataset_previous_month['patients_with_clauti'].mean(), 1)
                clauti_rate_previous_month = round((clauti_dataset_previous_month['clauti_count'].sum() / clauti_dataset_previous_month['days_on_x'].sum()) * 1000, 2)

            else:
                per_clauti_patients_previous_month = 'No data'
                clauti_rate_previous_month = 'No data'


            ivac_dataset_previous_month = ivac_count_for_dataset(unit_daily_data_previous_month, admission_data_previous_month)
            if isinstance(ivac_dataset_previous_month, pd.DataFrame):
                per_ivac_patients_previous_month = round(ivac_dataset_previous_month['patients_with_ivac'].mean(), 1)
                ivac_rate_previous_month = round((ivac_dataset_previous_month['ivac_count'].sum() / ivac_dataset_previous_month['days_on_x'].sum()) * 1000, 2)

            else:
                per_ivac_patients_previous_month = 'No data'
                ivac_rate_previous_month = 'No data'


            clabsi_per_change = percentage_change(per_clabsi_patients_previous_month, per_clabsi_patients)
            clauti_per_change = percentage_change(per_clauti_patients_previous_month, per_clauti_patients)
            ivac_per_change = percentage_change(per_ivac_patients_previous_month, per_ivac_patients)

            clabsi_rate_change = percentage_change(clabsi_rate_previous_month, clabsi_rate)
            clauti_rate_change = percentage_change(clauti_rate_previous_month, clauti_rate)
            ivac_rate_change = percentage_change(ivac_rate_previous_month, ivac_rate)



            return {
                'eligible_clabsi_patients': eligible_clabsi_patients,
                'per_clabsi_patients': per_clabsi_patients,
                'clabsi_rate': clabsi_rate,
                'clabsi_per_change': clabsi_per_change,
                'clabsi_rate_change': clabsi_rate_change,

                'eligible_clauti_patients': eligible_clauti_patients,
                'per_clauti_patients': per_clauti_patients,
                'clauti_rate': clauti_rate,
                'clauti_per_change': clauti_per_change,
                'clauti_rate_change': clauti_rate_change,

                'eligible_ivac_patients': eligible_ivac_patients,
                'per_ivac_patients': per_ivac_patients,
                'ivac_rate': ivac_rate,
                'ivac_per_change': ivac_per_change,
                'ivac_rate_change': ivac_rate_change
            }

        else:
            return qi_intervention_no_data




# ICU Turnover
# Occupancy
# Venous thromboembolism prophylaxis
# Duration of mechanical ventilation/ ventilator free days- (will combine with SBT)
# Unplanned reintubation within 24 hrs of extubation
# Stress ulcer prophylaxis

# Duration of antimicrobial use
# Length of ICU stay
# Unplanned readmission within 48hrs of discharge


