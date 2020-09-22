from datetime import datetime
import json

min_date = datetime.strptime('2020-09-01', '%Y-%m-%d')
max_date = datetime.strptime('2020-09-30', '%Y-%m-%d')
patients_outside_date_rate = 0

non_sari_discharged_patients_qi = 0
non_sari_discharged_patients_no_qi = 0
non_sari_in_patients_qi = 0
non_sari_in_patients_no_qi = 0

sari_discharged_patients_qi = 0
sari_discharged_patients_no_qi = 0
sari_in_patients_qi = 0
sari_in_patients_no_qi = 0

unit_json_data = ['unit_json_data']

json_icu_test_data = []

for patient in unit_json_data:
    admission_date = datetime.strptime(patient['admission']['date_of_admission'], '%Y-%m-%d')

    if min_date <= admission_date <= max_date:
        sari = False
        discharged = False
        qi_form = False
        sari_qi_form = False

        try:
            if patient['admission']['sari'] in ['Suspected', 'Confirmed']:
                sari = True
        except:
            pass

        try:
            if len(patient['dailyAssessments']) > 0:
                qi_form = True
        except:
            pass

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


        if sari and discharged and sari_qi_form and qi_form and sari_discharged_patients_qi < 1:
            json_icu_test_data.append(patient)
            sari_discharged_patients_qi += 1

        elif sari and discharged and not sari_qi_form and not qi_form and sari_discharged_patients_no_qi < 1:
            json_icu_test_data.append(patient)
            sari_discharged_patients_no_qi += 1

        elif sari and not discharged and sari_qi_form and qi_form and sari_in_patients_qi < 1:
            json_icu_test_data.append(patient)
            sari_in_patients_qi += 1

        elif sari and not discharged and not sari_qi_form and not qi_form and sari_in_patients_no_qi < 1:
            json_icu_test_data.append(patient)
            sari_in_patients_no_qi += 1

        elif not sari and discharged and qi_form and non_sari_discharged_patients_qi < 1:
            json_icu_test_data.append(patient)
            non_sari_discharged_patients_qi += 1

        elif not sari and discharged and not qi_form and non_sari_discharged_patients_no_qi < 1:
            json_icu_test_data.append(patient)
            non_sari_discharged_patients_no_qi += 1

        elif not sari and not discharged and qi_form and non_sari_in_patients_qi < 1:
            json_icu_test_data.append(patient)
            non_sari_in_patients_qi += 1

        elif not sari and not discharged and not qi_form and non_sari_in_patients_no_qi < 1:
            json_icu_test_data.append(patient)
            non_sari_in_patients_no_qi += 1




        # Not doing it like because it is less scalable and readable.

        # if sari:
        #     if discharged:
        #         if sari_qi_form:
        #
        #         else:
        #
        #     else:
        #         if sari_qi_form:
        #
        #         else:
        #
        # else:
        #     if discharged:
        #         if qi_form:
        #
        #         else:
        #
        #     else:
        #         if qi_form:
        #
        #         else:



    elif (patients_outside_date_rate < 2) and (admission_date < min_date or admission_date > max_date):
         json_icu_test_data.append(patient)
         patients_outside_date_rate += 1


json_icu_test_data_str = json.dumps(json_icu_test_data)
with open(r'icu_json_test_data.json', 'w') as f:
     f.write(json_icu_test_data_str)