
### Plan
1. Move all functions into one shared functions file  
2. Look for simlar/duplicate functions and try to merge them into one  
3. Look for no longer used functions and remove them  
4  Use more specific function names to help readablity  
5. Store constant ouput for each endpoint when no data is availble in constant.py file
6. Test new output with frontend. (more detail at the bottom)
5. Create a document for each endpoint with pointer to function used
5. Think about how we can use classers (After speaking to Jon not reuqired)

### Progress
1. I have moved all functions into the shared function file.
2. Merge similar function my adding filter options. Creating dict outputs so we can have a single function instead of three.
3. Delete function no longer used.
4. I have changed variable names to try and create a alignment accross the code.
5. Moved constant no data output to a different file.
6. 


### Backend testing
1. Vizhospital works
2. Vizregistry works
3. my covid unit works
4. my covid registry works
5. QI HAI runs (can't confirm works till data has been added)
6. Completeness works
7. Validation (will be removed because of the adition of the validation dashbaord)
8. Validation dasbhaord


### Front end testing

1. Vizhospital works
2. Vizregistry works
3. my covid unit works
4. my covid registry works
5. QI HAI runs (can't confirm works till data has been added)
6 Completeness (Need to share the new output with Darshana to update the pdf report)
7. Validation (not going to test as it is being removed)
8. Validation dashboard not yet tested.



## My unit
### Output
**Total admission**   
**Bed occupancy**  
**Length of stay (admission type)**  
**Admission type (ratio)**  
**ICU turn over**  
**Admission type (by month)**  
**Apache II score (admission type)**  
**Ventilation (by month)**  
**Antibiotics (percentage list)**  
**Antibiotics use (days)**
**Reason for admission**  
**Cardiovascular support (percentage list)**  

### Data required

**Admission dataset**

**Daily assessment**
  
  
## My registry
### Output
**Number of hospitals**
**Number of units**
**Number of beds**
**Total admission**   
**Admission type (by month)**  
**Length of stay (admission type)**  
**Ventilation (by month)**  
**Ventilation (percentage)**  
**Antibiotics (percentage list)**  
**Antibiotics use (days)**
**Reason for admission**  
**Cardiovascular support (percentage list)**  

### Date required 

**Admission dataset**

**Daily assessment**
  
  
  
  
## Report
### Output
**Total admission**   
**Bed occupancy**  
**ICU turnover**  
**Unplanned readmission**  
**Admission type (ratio n, per)**  
**Top ten diagnosis**  
**Withdrawal of treatment**  
**Left against medical advice**  
**Cardiac arrest**  


**Age (mean, sd) PLANNED**  
**Gender (ratio) PLANNED**  
**Length of stay prior to icu admission PLANNED**  
**Invasive ventilation PLANNED**  
**Non invasive ventilation PLANNED**  
**Renal replacement therapy PLANNED**  
**APACHE II PLANNED**  
**Length of stay (mean, SD, median, IQR) PLANNED**  
**Tracheostomies count PLANNED**  

**Age (mean, sd) UNPLANNED**  
**Gender (ratio) UNPLANNED**  
**Length of stay prior to icu admission UNPLANNED**  
**Invasive ventilation UNPLANNED**  
**Non invasive ventilation UNPLANNED**  
**Renal replacement therapy UNPLANNED**  
**APACHE II UNPLANNED**  
**Length of stay (mean, SD, median, IQR) UNPLANNED**  
**Tracheostomies count UNPLANNED**  


**CLABSI**  
**CLAUTI**  
**IVAC**  

**Venuos thromboemboliasm prophylaxis**  
**Duration of mechanical vent**  
**Unplanned reintubain within 24 hrs**  
**Stress ulcer prophylaxis**  
**Trial of spontaneous breathing**  
**Duration of ABx use**  


**Overall completeness UNIT**  
**Core data completeness UNIT**  
**Availability of daily assessment (% of admissions who had a daily assessment on each day of in patient ICU stay) UNIT**  
**Availability of data to calculate QIs (% of eligible episodes) UNIT**  
**Overall completeness REGISTRY**  
**Core data completeness REGISTRY**  
**Availability of daily assessment (% of admissions who had a daily assessment on each day of in patient ICU stay) REGISTRY**  
**Availability of data to calculate QIs (% of eligible episodes) REGISTRY**  



**Number of hospitals**
**Number of units**
**Number of beds**
**Admission type (by month)**  
**Length of stay (admission type)**  
**Ventilation (by month)**  
**Ventilation (percentage)**  
**Antibiotics (percentage list)**  
**Antibiotics use (days)**
**Reason for admission**  
**Cardiovascular support (percentage list)**  

### Date required 

**Admission dataset**

**Daily assessment**
  
  
## My unit COVID
### Output
**Number of suspected/confirmed covid patients**  
**Bed occupancy**  
**Number of covid suspcted patients (n, per of suspected/confirmed)**  
**Number of covid comfirmed patients (n, per of suspected/confirmed)**  
**Male (n, per of suspected/confirmed)**  
**Mean age**  
**Mechanically ventilated (n, per of suspected/confirmed)**  
Invasive + non invasive patients.  
**Non invasive (n, per of suspected/confirmed)**  
**Renal replacement therapy (n, per of suspected/confirmed)**  
**In ICU patents**  
**ICU mortality (n, per of discharged covid suspected/confirmed)**  
**ICU mortality mechanically ventilated (n, per of discharged covid suspected/confirmed MV)**  
**Length of stay**  
**Cumulative count of covid patients by day**  


### Date required 

**Admission dataset**





### My registry COVID
### Output
**Number of suspected/confirmed covid patients**  
**Number of units capturing COVID data**  
**Bed occupancy**  
**Number of covid suspcted patients (n, per of suspected/confirmed)**  
**Number of covid comfirmed patients (n, per of suspected/confirmed)**  
**Male (n, per of suspected/confirmed)**  
**Mean age**  
**Mechanically ventilated (n, per of suspected/confirmed)**  
Invasive + non invasive patients.  
**Non invasive (n, per of suspected/confirmed)**  
**Renal replacement therapy (n, per of suspected/confirmed)**  
**In ICU patents**  
**ICU mortality (n, per of discharged covid suspected/confirmed)**  
**ICU mortality mechanically ventilated (n, per of discharged covid suspected/confirmed MV)**  
**Length of stay**  
**Cumulative count of covid patients by day and unit**  


### Date required 

**Admission dataset**
  
  
## QI HAI
### Output
**Number of eligible patients for CLABSI**  
**Percentage of incidence CLABSI**  
**Percentage change in number of incidence CLABSI**  
**CLABSI per 1000 device days**  
**Percentage change in CLABSI per 1000 device days**  
  
**Number of eligible patients for CAUTI**    
**Percentage of incidence CAUTI**  
**Percentage change in number of incidence CAUTI**  
**CAUTI per 1000 device days**  
**Percentage change in CAUTI per 1000 device days**  
  
**Number of eligible patients for IVAC**  
**Percentage of incidence IVAC**  
**Percentage change in number of incidence IVAC**  
**IVAC per 1000 device days**  
**Percentage change in IVAC per 1000 device days**  


### Data required
**Admission data**
**Daily assessment data**
**Investigation data**
  
  
## Validation dashboard
### Output
**Completeness for every core variable and every variable from the sari admission, sari discharge, sari qi and qi forms.** 
**Overall completeness core data**  
**Overall completeness qi data**  
**Overall completeness sari admission discharge forms**  
**Overall completeness sari qi data**  

### Required data
**Data dict**
**Admission data**
**Daily assessment**
**Sari daily assessment**
  
  
## Validation dashboard
###Output
**Core data completness for list of units**  

###Data required
**Data dict**
**Admission data**






### Starting functions 
sbt
cardiac_arrest
renal_replacement
blood_culture
urine_culture
csf_culture
top_ten_blood_cultures
stress_ulcer_for_patient
stress_ulcer_rate_for_dataset
unnplanned_reintubain
venuos_thromboemboliasm_for_patient
venuos_thromboemboliasm
for_discharge_cols_fill_if_not_discharged
for_sariAdmission_cols_fill_if_not_sari
for_sariDischarge_cols_fill_if_not_sari
get_qi_completeness
get_daily_assessment_form_completeness
get_core_variables
get_completeness_for_dataset
get_completeness_core_data
get_completeness
get_data_dict
transform_data_column_names
fill_empty_all_columns_on_branching_logic
fill_column_based_on_branching_logic
format_and_or
los_stats
non_invasive_ventilation
los_prior_to_icu
per_left_against_medical_advice
withdrawal_of_treatment
smr
count_diagnosis_type
create_columns_if_not_there
completeness_cal
dishcharge_commplitnece
comp_mechanically_ventilated_source
comp_vasioactive_drugs
comp_antibiotic_type
age
gender
month_year
discharge_status
get_discharge_details
admission_type
tracheostomy_performed
number_of_clauti_for_patient
clauti_count_for_dataset
clauti_rate_over_year
percentage_clauti_patients_over_year
clauti_rate_for_dataset
clauti_compared_to_previous_month
percentage_clauti_patients_compered_to_previous_month
clabsi_count_for_patient
clabsi_count_for_dataset
clabsi_rate_over_year
clabsi_percentage_of_patients_over_year
clabsi_rate_for_dataset
clabsi_count_compared_to_previous_month
clabsi_patients_compared_to_previous_month
ivac_count_for_patient
ivac_count_for_dataset
ivac_rate_over_year
percentage_of_ivac_patients_over_year
ivac_rate_for_dataset
ivac_compared_to_previous_month
percentage_of_ivac_patients_compared_to_previous_month
getPreviousMonth
getPreviousYear
numberOfAdmissionComparedToLastMonth
icuTurnOver
icuTurnOverComparedToLastMonth
admission_type_percentage
readmission
smr
patient_id_length_of_stay_greater_then
percentage_change
merge_culture_columns
filter_for_month
test_unit_id
get_json_data
get_admission_data
get_daily_assessment_data
get_investigation_data
length_of_stay
bed_occupancy_month
bed_occupancy_custom_range
eq5d
pain_score
mean_days_mechanically_ventilated
time_on_antibiotics
patient_satisfaction
number_of_admissions
count_mechanically_ventilated
apache_score
antibiotics_on_ad
mec_vent_by_month
fio2_by_month
fio2_iqr_range
per_high_fio2
top_ten_diagnosis_on_admission
cardiovascular_support_percentage
cardiovascular_support_count
admission_type_by_month
length_of_stay_admission_type
filter_by_admission_type
merge_different_age_columns_into_one
n_per_join
pims_score
join_sari_admission_variables
filter_for_month
getAdmissionData
filter_for_month
getAdmissionData
get_daily_assessment_data
admission_type_ratio
diagnosis_type
count_cardiovascular_support
use_of_antibiotics
hierarchical_chart_level1
hierarchical_chart_level2
mortality_rate
filter_for_month
filter_for_year
filter_before_month
test_unit_id
get_json_data
getAdmissionData
get_daily_assessment_data
number_of_hospitals
number_of_units
number_of_beds