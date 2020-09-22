from flask import request
from flask_restful import Resource

from .HttpCall import get_all_units, get_json_data_dict, get_all_patients
from .constants import vizhospital_no_data
from .shared_functions import number_of_admissions, \
    time_on_antibiotics, \
    count_mechanically_ventilated, \
    bed_occupancy_custom_range, \
    apache_score, \
    length_of_stay, \
    top_ten_diagnosis_on_admission, \
    admission_type_by_month, \
    mec_vent_by_month, \
    cardiovascular_support_stats, \
    use_of_antibiotics, pims_score, icuTurnOver, admission_type_ratio, \
    get_admission_data, get_qi_data, number_of_beds, readmission


class VizDataHospital(Resource):

    def post(self):
        unit_id = request.form.get("unitId")
        front_end_date_input = request.form.get("month")
        patients = get_all_patients('unitId', unit_id)
        admission_data = get_admission_data(patients, front_end_date_input)
        admission_this_month = number_of_admissions(admission_data)
        try:
            dd_type = get_json_data_dict(unit_id)['type']
        except:
            dd_type = 'normal'
        if admission_this_month > 0:
            start_date, end_date = front_end_date_input.split(' - ')
            daily_assessment_data = get_qi_data(patients, front_end_date_input)
            unit_data = get_all_units()
            bed_count = number_of_beds(unit_data, ['testUnits'], front_end_date_input, [unit_id])
            mean_length_of_stay = length_of_stay(admission_data)

            antibiotics_per = use_of_antibiotics(admission_data, admission_this_month)
            antibiotics_per_list = [antibiotics_per['per_yes'], antibiotics_per['per_no']]

            cardiovascular_per = cardiovascular_support_stats(admission_data)
            cardiovascular_per_list = [cardiovascular_per['per_yes'], cardiovascular_per['per_no']]

            return {
                'unplanned_readmissions': readmission(admission_data),
                'total_admissions': admission_this_month,
                'bed_occupancy': bed_occupancy_custom_range(admission_this_month, mean_length_of_stay, bed_count,
                                                            front_end_date_input),
                'length_of_stay': mean_length_of_stay,
                'admission_type': admission_type_ratio(admission_data),
                'admission_type_per_month': admission_type_by_month(admission_data, start_date, end_date),
                'los_planned': length_of_stay(admission_data, "Planned"),
                'los_unplanned': length_of_stay(admission_data, "Unplanned"),
                'apache_score': apache_score(admission_data),
                'pims_score': pims_score(admission_data),
                'mechanically_ventilated_by_month': mec_vent_by_month(admission_data, start_date, end_date),
                'mechanically_ventilated_on_admission': count_mechanically_ventilated(admission_data,
                                                                                      admission_this_month),
                'antibiotics_on_admission': antibiotics_per_list,
                'time_on_antibiotics': time_on_antibiotics(admission_data, daily_assessment_data),
                'top_ten_diagnosis': top_ten_diagnosis_on_admission(admission_data),
                'icu_turn_over': icuTurnOver(admission_this_month, bed_count),
                'cardiovascular_support_on_admission': cardiovascular_per_list,
                'dd_type': dd_type
            }

        else:
            vizhospital_no_data['dd_type'] = dd_type

            return vizhospital_no_data
