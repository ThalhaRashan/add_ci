from datetime import datetime
import json

min_date = datetime.strptime('2020-07-01', '%Y-%m-%d')
max_date = datetime.strptime('2020-09-30', '%Y-%m-%d')
patients_outside_date_rate = 0

sari_discharged_patients_qi = 0
sari_in_patients_qi = 0

unit_json_data = # import json data

ward_icu_test_data = []

for patient in unit_json_data:
    admission_date = datetime.strptime(patient['admission']['date_of_admission_hospital'], '%Y-%m-%d')

    if min_date <= admission_date <= max_date:
        discharged = False
        # qi_form = False
        sari_qi_form = False

        # try:
        #     if len(patient['dailyAssessments']) > 0:
        #         qi_form = True
        # except:
        #     pass

        try:
            if len(patient['sariDailyAssessments']) > 0:
                sari_qi_form = True
        except:
            pass

        try:
            if patient['dischargeStatus'] == 'true':
                discharged = True
        except:
            pass

        if discharged and sari_qi_form and sari_discharged_patients_qi < 8:
            ward_icu_test_data.append(patient)
            sari_discharged_patients_qi += 1

        elif not discharged and sari_qi_form and sari_in_patients_qi < 4:
            ward_icu_test_data.append(patient)
            sari_in_patients_qi += 1


    elif (patients_outside_date_rate < 2) and (admission_date < min_date or admission_date > max_date):
        ward_icu_test_data.append(patient)
        patients_outside_date_rate += 1

json_ward_test_data_str = json.dumps(ward_icu_test_data)
with open(r'ward_json_test_data.json', 'w') as f:
    f.write(json_ward_test_data_str)