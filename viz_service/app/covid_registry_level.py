from flask import request
from flask_restful import Resource
import pandas as pd

from .HttpCall import get_all_patients, get_all_units, get_test_unit_ids
from .constants import covid_registry_level_no_data

from .shared_functions import number_of_admissions, \
    length_of_stay, \
    bed_occupancy_custom_range, \
    n_per_join, \
    number_of_units, \
    number_of_beds, \
    covid_count_by_unit, \
    get_admission_data


class COVID_registry_stat(Resource):

    def post(self):

        # TODO Check that we have sari coloumns in the data set
        # TODO check with Abi / Issrah that we get the percentage if we are missing data
        # TODO check that the filter is including the first date

        date_range = request.form.get('month')
        unitId = request.form.get('unitId')
        raw_data = get_all_patients()
        test_units = get_test_unit_ids()
        all_data = get_admission_data(raw_data, date_range, test_units)

        if 'sariAdmissionAssessment.date' in all_data:

            # filter for patients that have sari admission date filled
            # covid_data = all_data.dropna(subset=['sariAdmissionAssessment.date'])

            if 'admission.sari' in all_data:
                # use admission covid as base covid status
                all_data['covid_status'] = all_data['admission.sari']

            if pd.Series(['sariPreDischarge.influenza_diagnosis', 'sariPreDischarge.influenza1',
                          'sariPreDischarge.influenza2', 'sariPreDischarge.sari_diagnosis',
                          'sariPreDischarge.sari1']).isin(all_data.columns).all():
                # if we have discharge covid status overwirte the admission status with No
                all_data.loc[((~all_data['sariPreDischarge.influenza_diagnosis'].isna()) |
                              (~all_data['sariPreDischarge.influenza1'].isna()) |
                              (~all_data['sariPreDischarge.influenza2'].isna()) |
                              (~all_data['sariPreDischarge.sari_diagnosis'].isna()) |
                              (~all_data['sariPreDischarge.sari1'].isna())), 'covid_status'] = 'No'

                # NoW populate the covid status with suspected or confired at discharged
                all_data.loc[
                    (((all_data['sariPreDischarge.influenza_diagnosis'] == "Yes- confirmed") &
                      ((all_data['sariPreDischarge.influenza1'] == "COVID-19") |
                       (all_data['sariPreDischarge.influenza2'] == "COVID-19"))) |
                     ((all_data['sariPreDischarge.sari_diagnosis'] == "Yes- confirmed") &
                      (((all_data['sariPreDischarge.sari1'] == "COVID-19") |
                        (all_data[
                             'sariPreDischarge.sari1'] == "COVID-2019/ SARS-CoV2"))))), 'covid_status'] = 'Confirmed'

                all_data.loc[(((all_data['sariPreDischarge.influenza_diagnosis'] == "Yes- probable") &
                               ((all_data['sariPreDischarge.influenza1'] == "COVID-19") |
                                (all_data['sariPreDischarge.influenza2'] == "COVID-19"))) |
                              ((all_data['sariPreDischarge.sari_diagnosis'] == "Yes- probable") &
                               (((all_data['sariPreDischarge.sari1'] == "COVID-19") |
                                 (all_data[
                                      'sariPreDischarge.sari1'] == "COVID-2019/ SARS-CoV2"))))), 'covid_status'] = 'Suspected'

            # filter to get suspected or confired COVID patietns
            covid_data = all_data.loc[
                ((all_data['covid_status'] == 'Confirmed') | (all_data['covid_status'] == 'Suspected'))]

            # reomve patients with sari form filled but admission.sari is none (previous data dict version)
            # covid_data = covid_data.loc[covid_data['admission.sari'] != 'None']

            # replace missing covid status with suspected (previous data dict)
            # covid_data['admission.sari'] = covid_data['admission.sari'].replace(['', np.nan, 'Yes'], ['Suspected', 'Suspected', 'Confirmed'])

            # get number of covid admissions
            covid_cases = number_of_admissions(covid_data)

            # get covid units
            covid_units = covid_data['unitId'].unique().tolist()

            if covid_cases > 0:

                # get the unit information so that we can filter by date and get the correct number of beds
                unit_data = get_all_units()

                #  get the number of units covid units
                number_covid_units = number_of_units(covid_data)

                # get number of suspected covid casses
                suspected_covid_count = len(covid_data.loc[covid_data['covid_status'] == 'Suspected'])
                suspected_covid_per = round((suspected_covid_count / covid_cases) * 100, 1)
                suspected_covid_label = n_per_join(suspected_covid_count, suspected_covid_per)

                # get number of confired covid casses
                confirmed_covid_count = len(covid_data.loc[covid_data['covid_status'] == 'Confirmed'])
                confirmed_covid_per = round((confirmed_covid_count / covid_cases) * 100, 1)
                confirmed_covid_label = n_per_join(confirmed_covid_count, confirmed_covid_per)

                # get percentage of patients that are male
                male_cases_count = len(covid_data.loc[covid_data['admission.gender'] == 'Male'])
                male_cases_per = round((male_cases_count / covid_cases) * 100, 1)
                male_cases_label = n_per_join(male_cases_count, male_cases_per)

                # get mean age
                age_data = pd.to_numeric(covid_data['admission.age'], errors='coerce')
                mean_age = round(age_data.mean(), 1)

                # get the mec ventilated per
                mec_vent_count = len(
                    covid_data.loc[covid_data['admissionAssessment.mechanically_ventilated'] == 'mechanical_vent'])
                mec_vent_per = round((mec_vent_count / covid_cases) * 100, 1)
                mec_vent_label = n_per_join(mec_vent_count, mec_vent_per)

                # get the non invasive per
                non_invasive_count = len(
                    covid_data.loc[
                        covid_data['admissionAssessment.mechanically_ventilated_source'] == 'Non invasive vent'])
                non_invasive_per = round((non_invasive_count / covid_cases) * 100, 1)
                non_invasive_label = n_per_join(non_invasive_count, non_invasive_per)

                # get per renal replacment terapy
                rrt_count = len(
                    covid_data.loc[covid_data['admissionAssessment.renal_replacement'] == 'Yes'])
                rrt_per = round((rrt_count / covid_cases) * 100, 1)
                rrt_label = n_per_join(rrt_count, rrt_per)

                # get cumilative number of admission by unit
                start_date, end_date = date_range.split(' - ')
                covid_admission_by_unit = covid_count_by_unit(covid_data, start_date, end_date, unitId)

                # get the covid discharge data
                covid_discharge_data = covid_data.loc[covid_data['dischargeStatus'] == 'true']

                # get the number of discharge_patients
                covid_discharge_count = len(covid_discharge_data)

                covid_in_patients = covid_cases - covid_discharge_count

                if covid_discharge_count > 0:
                    # get the patients outcoms
                    dead_count = len(
                        covid_discharge_data.loc[covid_discharge_data['discharge.discharge_status'] == 'Dead'])
                    dead_per = round((dead_count / covid_discharge_count) * 100, 1)
                    dead_label = n_per_join(dead_count, dead_per)

                    # get the patients outcome with mec vent
                    mec_vent_discharged = covid_discharge_data.loc[
                        covid_discharge_data['admissionAssessment.mechanically_ventilated'] == 'mechanical_vent']
                    mec_vent_discharged_count = len(mec_vent_discharged)

                    if mec_vent_discharged_count > 0:
                        mec_vent_dead_count = len(
                            mec_vent_discharged.loc[mec_vent_discharged['discharge.discharge_status'] == 'Dead'])
                        mec_vent_dead_per = round((mec_vent_dead_count / mec_vent_discharged_count) * 100, 1)
                        mec_vent_dead_label = n_per_join(mec_vent_dead_count, mec_vent_dead_per)
                    else:
                        mec_vent_dead_per = 'No data'
                        mec_vent_dead_label = 'No data'

                    # get length of stay
                    los = length_of_stay(covid_discharge_data)

                    # get bed occupancy
                    bed_occupancy = bed_occupancy_custom_range(covid_cases, los,
                                                               number_of_beds(unit_data, test_units, date_range,
                                                                              covid_units), date_range)
                else:
                    dead_label = 'No data'
                    mec_vent_dead_label = 'No data'
                    los = 'No data'
                    bed_occupancy = 'No data'

                return {
                    'covid_cases': covid_cases,
                    'number_covid_units': number_covid_units,
                    'covid_in_patients': covid_in_patients,
                    'bed_occupancy': bed_occupancy,
                    'suspected_covid_label': suspected_covid_label,
                    'confirmed_covid_label': confirmed_covid_label,
                    'male_cases_label': male_cases_label,
                    'mean_age': mean_age,
                    'mec_vent_label': mec_vent_label,
                    'non_invasive_label': non_invasive_label,
                    'rrt_label': rrt_label,
                    'covid_admission_by_unit': covid_admission_by_unit,
                    'covid_discharge_count': covid_discharge_count,
                    'dead_label': dead_label,
                    'mec_vent_dead_label': mec_vent_dead_label,
                    'los': los
                }

            else:
                return covid_registry_level_no_data
        else:
            return covid_registry_level_no_data
