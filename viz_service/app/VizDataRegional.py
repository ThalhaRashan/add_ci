from flask import request
from flask_restful import Resource

from .HttpCall import get_all_patients, get_all_units, get_test_unit_ids
from .constants import vizregonal_no_data
from .shared_functions import number_of_admissions, \
    count_mechanically_ventilated, \
    mec_vent_by_month, \
    top_ten_diagnosis_on_admission, \
    time_on_antibiotics, \
    admission_type_by_month, \
    get_admission_data, \
    get_qi_data, \
    number_of_units, number_of_beds, number_of_hospitals, cardiovascular_support_stats, length_of_stay, \
    use_of_antibiotics


class VizDataRegional(Resource):

    def post(self):

        date_input = request.form.get('month')
        raw_data = get_all_patients()
        test_units = get_test_unit_ids()
        dataset_this_month = get_admission_data(raw_data, date_input, test_units)
        admission_this_month = number_of_admissions(dataset_this_month)
        if admission_this_month > 0:
            daily_assessment = get_qi_data(raw_data, date_input, test_units)
            days_on_antibiotics = time_on_antibiotics(dataset_this_month, daily_assessment)
            unit_data = get_all_units()

            antibiotics_per = use_of_antibiotics(dataset_this_month, admission_this_month)
            antibiotics_per_list = [antibiotics_per['per_yes'], antibiotics_per['per_no']]

            cardiovascular_per = cardiovascular_support_stats(dataset_this_month)
            cardiovascular_per_list = [cardiovascular_per['per_yes'], cardiovascular_per['per_no']]

            return {'admission_type_by_month': admission_type_by_month(dataset_this_month),
                    'mechanically_ventilated_by_month': mec_vent_by_month(dataset_this_month),
                    'mechanically_ventilated_per': count_mechanically_ventilated(dataset_this_month, admission_this_month)['per'],
                    'antibiotics': antibiotics_per_list,
                    'los_planned': length_of_stay(dataset_this_month, "Planned"),
                    'los_unplanned': length_of_stay(dataset_this_month, "Unplanned"),
                    'cardiovascular_support': cardiovascular_per_list,
                    'top_ten_diagnosis': top_ten_diagnosis_on_admission(dataset_this_month),
                    'time_on_antibiotics': days_on_antibiotics,
                    'number_units': number_of_units(dataset_this_month),
                    'number_beds': number_of_beds(unit_data, test_units, date_input),
                    'number_hospitals': number_of_hospitals(dataset_this_month),
                    'total_admissions': admission_this_month}
        else:
            return vizregonal_no_data

