from flask_restful import Resource
from flask import request
from .HttpCall import get_all_units, get_all_patients
from .constants import completeness_report_no_data
from .shared_functions import icuTurnOver,\
    readmission,\
    number_of_beds, age, \
    gender, \
    admission_type, \
    withdrawal_of_treatment, \
    per_left_against_medical_advice, \
    los_prior_to_icu, \
    non_invasive_ventilation, \
    los_stats, \
    tracheostomy_performed, \
    get_data_dict, \
    fill_empty_all_columns_on_branching_logic, \
    get_core_variables, \
    get_completeness_core_data, \
    get_completeness, \
    get_qi_completeness, \
    get_daily_assessment_form_completeness, \
    transform_data_column_names, \
    renal_replacement, \
    cardiac_arrest, \
    unnplanned_reintubain, \
    venuos_thromboemboliasm, \
    stress_ulcer_rate_for_dataset, \
    sbt, \
    number_of_admissions, \
    time_on_antibiotics, \
    mean_days_mechanically_ventilated, \
    count_mechanically_ventilated, \
    bed_occupancy_custom_range, \
    get_qi_data, \
    length_of_stay, \
    apache_score, \
    get_admission_data, \
    top_ten_diagnosis_on_admission, \
    get_investigation_data

import json

class Completeness(Resource):

    def post(self):

        unit_id = request.form.get("unitId")
        date_input = request.form.get('month')
        raw_unit_data = get_all_patients('unitId', unit_id)
        unit_admission_data = get_admission_data(raw_unit_data, date_input)
        number_of_admission = number_of_admissions(unit_admission_data)
        if number_of_admission > 0:
            data_dictionary = get_data_dict(unit_id)
            core_variables = get_core_variables(data_dictionary)

            unit_investigation_data = get_investigation_data(raw_unit_data, date_input)
            unit_daily_assessment_data = get_qi_data(raw_unit_data, date_input)
            unit_data = fill_empty_all_columns_on_branching_logic(data_dict=data_dictionary,
                                                                  admissionData=unit_admission_data,
                                                                  dailyAssessmentData=unit_daily_assessment_data,
                                                                  investigationData=unit_investigation_data)
            unit_admission_data = unit_data['admissionData']
            unit_daily_assessment_data = unit_data['dailyAssessmentData']
            unit_investigation_data = unit_data['investigationData']

            unit_core_variable_completeness = get_completeness_core_data(unit_admission_data, core_variables)
            unit_overall_completeness = get_completeness(unit_admission_data, unit_daily_assessment_data,
                                                         unit_investigation_data)
            unit_QI_variable_completeness = get_qi_completeness(unit_admission_data, unit_daily_assessment_data,
                                                                unit_investigation_data)
            unit_QI_form_completeness = get_daily_assessment_form_completeness(unit_admission_data)

            unit_data = transform_data_column_names(admissionData=unit_admission_data,
                                                    dailyAssessmentData=unit_daily_assessment_data,
                                                    how='default')

            unit_admission_data = unit_data['admissionData']
            unit_daily_assessment_data = unit_data['dailyAssessmentData']

            unit_admission_data_planned = unit_admission_data.loc[
                unit_admission_data['admission.admission_type'] == 'Planned']
            unit_admission_data_unplanned = unit_admission_data.loc[
                unit_admission_data['admission.admission_type'] == 'Unplanned']

            raw_registry_data = get_all_patients()
            registry_admission_data = get_admission_data(raw_registry_data, date_input)
            registry_investigation_data = get_investigation_data(raw_registry_data, date_input)
            registry_daily_assessment_data = get_qi_data(raw_registry_data, date_input)
            registry_data = fill_empty_all_columns_on_branching_logic(data_dict=data_dictionary,
                                                                      admissionData=registry_admission_data,
                                                                      dailyAssessmentData=registry_daily_assessment_data,
                                                                      investigationData=registry_investigation_data)
            registry_admission_data = registry_data['admissionData']
            registry_daily_assessment_data = registry_data['dailyAssessmentData']
            registry_investigation_data = registry_data['investigationData']

            registry_core_variable_completeness = get_completeness_core_data(registry_admission_data, core_variables)
            registry_overall_completeness = get_completeness(registry_admission_data, registry_daily_assessment_data,
                                                             registry_investigation_data)
            registry_QI_variable_completeness = get_qi_completeness(registry_admission_data,
                                                                    registry_daily_assessment_data,
                                                                    registry_investigation_data)
            registry_QI_form_completeness = get_daily_assessment_form_completeness(registry_admission_data)

            unit_data = get_all_units()
            bed_count = number_of_beds(unit_data, ['testUnits'], date_input, [unit_id])
            mean_length_of_stay = length_of_stay(unit_admission_data)

            with open(r'report_output.json', 'w') as f:
                f.write(json.dumps({
                'number_of_beds': bed_count,
                'number_admission': number_of_admission,
                'bed_occupancy': bed_occupancy_custom_range(number_of_admission, mean_length_of_stay,
                                                            bed_count, date_input),
                'icu_turn_over': icuTurnOver(number_of_admission, bed_count),
                'unplanned_readmission': readmission(unit_admission_data),
                'admission_type': admission_type(unit_admission_data, number_of_admission),
                'top_ten_diagnosis': top_ten_diagnosis_on_admission(unit_admission_data, ['Other']),
                'treatment_withdrawn': withdrawal_of_treatment(unit_admission_data, number_of_admission),
                'left_against_medical_advice': per_left_against_medical_advice(unit_admission_data),
                'cardiac_arrest': cardiac_arrest(unit_admission_data),

                'age_planned': age(unit_admission_data_planned),
                'age_unplanned': age(unit_admission_data_unplanned),
                'gender_planned': gender(unit_admission_data_planned),
                'gender_unplanned': gender(unit_admission_data_unplanned),
                'los_prior_to_icu_planned': los_prior_to_icu(unit_admission_data_planned),
                'los_prior_to_icu_unplanned': los_prior_to_icu(unit_admission_data_unplanned),
                'mechanically_ventilated_planned': count_mechanically_ventilated(unit_admission_data_planned),
                'mechanically_ventilated_unplanned': count_mechanically_ventilated(unit_admission_data_unplanned),
                'non_invasive_ventilation_planned': non_invasive_ventilation(unit_admission_data),
                'renal_replacement_planned': renal_replacement(unit_daily_assessment_data),
                'renal_replacement_unplanned': renal_replacement(unit_daily_assessment_data),
                'apache_score': apache_score(unit_admission_data),  # contains planned and unplanned variables
                'los_stats_planned': los_stats(unit_admission_data_planned),
                'los_stats_unplanned': los_stats(unit_admission_data_unplanned),
                'tracheostomies_performed_planned': tracheostomy_performed(unit_admission_data_planned,
                                                                           unit_daily_assessment_data),
                'tracheostomies_performed_unplanned': tracheostomy_performed(unit_admission_data_unplanned,
                                                                             unit_daily_assessment_data),

                'clabsi_rate': 'No data',
                'clauti_rate': 'No data',
                'ivac_rate': 'No data',

                'venuos_thromboemboliasm': venuos_thromboemboliasm(unit_daily_assessment_data),
                'Mean_duration_of_mechanical_ventilation': mean_days_mechanically_ventilated(
                    unit_admission_data, unit_daily_assessment_data),
                'unnplanned_reintubain': unnplanned_reintubain(unit_daily_assessment_data),
                'stress_ulcer': stress_ulcer_rate_for_dataset(unit_daily_assessment_data),
                'sbt': sbt(unit_daily_assessment_data),
                'Mean_duration_on_antibiotics': time_on_antibiotics(unit_admission_data,
                                                                    unit_daily_assessment_data),

                'completeness_core_variables': unit_core_variable_completeness,
                'completeness': unit_overall_completeness,
                'QI_assessment': unit_QI_variable_completeness,
                'completeness_QI_form_completeness': unit_QI_form_completeness,
                'registry_completeness_core_variables': registry_core_variable_completeness,
                'registry_completeness': registry_overall_completeness,
                'registry_QI_assessment': registry_QI_variable_completeness,
                'registry_completeness_QI_form_completeness': registry_QI_form_completeness}))

            return {
                'number_of_beds': bed_count,
                'number_admission': number_of_admission,
                'bed_occupancy': bed_occupancy_custom_range(number_of_admission, mean_length_of_stay,
                                                            bed_count, date_input),
                'icu_turn_over': icuTurnOver(number_of_admission, bed_count),
                'unplanned_readmission': readmission(unit_admission_data),
                'admission_type': admission_type(unit_admission_data, number_of_admission),
                'top_ten_diagnosis': top_ten_diagnosis_on_admission(unit_admission_data, ['Other']),
                'treatment_withdrawn': withdrawal_of_treatment(unit_admission_data, number_of_admission),
                'left_against_medical_advice': per_left_against_medical_advice(unit_admission_data),
                'cardiac_arrest': cardiac_arrest(unit_admission_data),

                'age_planned': age(unit_admission_data_planned),
                'age_unplanned': age(unit_admission_data_unplanned),
                'gender_planned': gender(unit_admission_data_planned),
                'gender_unplanned': gender(unit_admission_data_unplanned),
                'los_prior_to_icu_planned': los_prior_to_icu(unit_admission_data_planned),
                'los_prior_to_icu_unplanned': los_prior_to_icu(unit_admission_data_unplanned),
                'mechanically_ventilated_planned': count_mechanically_ventilated(unit_admission_data_planned),
                'mechanically_ventilated_unplanned': count_mechanically_ventilated(unit_admission_data_unplanned),
                'non_invasive_ventilation_planned': non_invasive_ventilation(unit_admission_data),
                'renal_replacement_planned': renal_replacement(unit_daily_assessment_data),
                'renal_replacement_unplanned': renal_replacement(unit_daily_assessment_data),
                'apache_score': apache_score(unit_admission_data),  # contains planned and unplanned variables
                'los_stats_planned': los_stats(unit_admission_data_planned),
                'los_stats_unplanned': los_stats(unit_admission_data_unplanned),
                'tracheostomies_performed_planned': tracheostomy_performed(unit_admission_data_planned,
                                                                           unit_daily_assessment_data),
                'tracheostomies_performed_unplanned': tracheostomy_performed(unit_admission_data_unplanned,
                                                                             unit_daily_assessment_data),

                'clabsi_rate': 'No data',
                'clauti_rate': 'No data',
                'ivac_rate': 'No data',

                'venuos_thromboemboliasm': venuos_thromboemboliasm(unit_daily_assessment_data),
                'Mean_duration_of_mechanical_ventilation': mean_days_mechanically_ventilated(
                    unit_admission_data, unit_daily_assessment_data),
                'unnplanned_reintubain': unnplanned_reintubain(unit_daily_assessment_data),
                'stress_ulcer': stress_ulcer_rate_for_dataset(unit_daily_assessment_data),
                'sbt': sbt(unit_daily_assessment_data),
                'Mean_duration_on_antibiotics': time_on_antibiotics(unit_admission_data,
                                                                    unit_daily_assessment_data),

                'completeness_core_variables': unit_core_variable_completeness,
                'completeness': unit_overall_completeness,
                'QI_assessment': unit_QI_variable_completeness,
                'completeness_QI_form_completeness': unit_QI_form_completeness,
                'registry_completeness_core_variables': registry_core_variable_completeness,
                'registry_completeness': registry_overall_completeness,
                'registry_QI_assessment': registry_QI_variable_completeness,
                'registry_completeness_QI_form_completeness': registry_QI_form_completeness}
        else:
            return completeness_report_no_data
