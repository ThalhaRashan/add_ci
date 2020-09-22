 
# CLABSI

## Variables used

**Admission form**

1. patient_id  
2. admission_date

**Daily form**
1. date_of_daily_assessment
2. date_of_investigation
3. central_venous_catheter
4. temperature
5. type_of_culture
6. organism

**Legacy data**  
In the past organism was captured in the investigation form it was entered in a very messy free text manner.
Should we include that data of shall we drop it?

## Calculation
### Definition

The patient should have be on a CVC line for over 48 hours  
OR  
should been taken off a CVC line in the last 48hours.  

If the patient meets ether of the following critira then we count it as CLABSI.  
  
1. Temperature > 38C
2. Culture == Blood
3. Organism not in list

OR 

1. Culture == Blood
2. Organism in in List

This is a reuccuring calculation so after 72 hours we check for CLABSI again.
We also check against the above critria 24 hours and 48 hours after being taken off a CVC line.  

### Method

**Data imported:**

1. Daily assessment
2. Investigation

**Merge outer the daily and investigation form on:**

1. patient_id,  
2. daily_assessment_data  
3. investigation_date
4. 'organism', 'organism1', 'organism2'

**Select required columns**

1. patient_id
2. admission_date
3. date_of_daily_assessment
4. date_of_investigation
5. central_venous_catheter
6. temperature
7. type_of_culture
8. organism


**Get CLABSI infomation**


Convert column into correct data types.  
Create new column 'Date' which combinds date_of_daily_assessment and date_of_investigation

Groupby patient_id: 
1. Look for CLABSI while patient is still on CVC.  
   Find the first CVC day, remove records for previous days  .
   Check 

2. Look for CLABSI in 48 hours after CVC removed.   












**Output a table with CLABSI infomation**  

Columns:
1. CLABSI count
2. CVC days
3. Patient Id
4. Admission date


## Values displayed on dashboard
### Eligible CLABSI patients  
Number of patients with LoS greater than 2 and a CVC line for a minimum of a day
### Percentage of CLABSI patients  
Number of pattients with CLABSI / Number of eligible patients
### CLABSI rate
For all eligible patients:  
(number of CLABSI / number of CVC days) * 1000 



# IVAC

##Probleam 

check number of days left