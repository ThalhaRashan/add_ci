completeness_core_variables_to_exclude = []

completeness_sari_variables_to_exclude = ['sari_pre_discharge_positive_culture1',
                                          'sari_pre_discharge_culture_date1',
                                          'sari_pre_discharge_type_of_culture1',
                                          'sari_pre_discharge_organism1',
                                          'sari_pre_discharge_cfu1',
                                          'sari_admission_assessment_sari_admission_assessment_id',
                                          'sari_admission_assessment_date',
                                          'sari_admission_assessment_time',
                                          'sari_pre_discharge_sari_pre_discharge_id',
                                          'sari_pre_discharge_date',
                                          'sari_pre_discharge_time']

completeness_sari_daily_variables_to_exclude = ['sari_daily_assessment_sari_daily_assessment_id',
                                                'sari_daily_assessment_date',
                                                'sari_daily_assessment_time']

completeness_daily_assessment_variables_to_exclude = ['daily_assessment_positive_culture1',
                                                      'daily_assessment_culture_date1',
                                                      'daily_assessment_type_of_culture1',
                                                      'daily_assessment_organism1',
                                                      'daily_assessment_cfu1',
                                                      'daily_assessment_daily_assessment_id',
                                                      'daily_assessment_date',
                                                      'daily_assessment_time'
                                                      ]

colors = ["#1CE6FF", "#FFFF00", "#FF34FF", "#FF4A46", "#008941", "#006FA6", "#A30059",
          "#FFDBE5", "#7A4900", "#0000A6", "#63FFAC", "#B79762", "#004D43", "#8FB0FF", "#997D87",
          "#5A0007", "#809693", "#FEFFE6", "#1B4400", "#4FC601", "#3B5DFF", "#4A3B53", "#FF2F80",
          "#61615A", "#BA0900", "#6B7900", "#00C2A0", "#FFAA92", "#FF90C9", "#B903AA", "#D16100",
          "#DDEFFF", "#000035", "#7B4F4B", "#A1C299", "#300018", "#0AA6D8", "#013349", "#00846F",
          "#372101", "#FFB500", "#C2FFED", "#A079BF", "#CC0744", "#C0B9B2", "#C2FF99", "#001E09",
          "#00489C", "#6F0062", "#0CBD66", "#EEC3FF", "#456D75", "#B77B68", "#7A87A1", "#788D66",
          "#885578", "#FAD09F", "#FF8A9A", "#D157A0", "#BEC459", "#456648", "#0086ED", "#886F4C",

          "#34362D", "#B4A8BD", "#00A6AA", "#452C2C", "#636375", "#A3C8C9", "#FF913F", "#938A81",
          "#575329", "#00FECF", "#B05B6F", "#8CD0FF", "#3B9700", "#04F757", "#C8A1A1", "#1E6E00",
          "#7900D7", "#A77500", "#6367A9", "#A05837", "#6B002C", "#772600", "#D790FF", "#9B9700",
          "#549E79", "#FFF69F", "#201625", "#72418F", "#BC23FF", "#99ADC0", "#3A2465", "#922329",
          "#5B4534", "#FDE8DC", "#404E55", "#0089A3", "#CB7E98", "#A4E804", "#324E72", "#6A3A4C",
          "#83AB58", "#001C1E", "#D1F7CE", "#004B28", "#C8D0F6", "#A3A489", "#806C66", "#222800",
          "#BF5650", "#E83000", "#66796D", "#DA007C", "#FF1A59", "#8ADBB4", "#1E0200", "#5B4E51",
          "#C895C5", "#320033", "#FF6832", "#66E1D3", "#CFCDAC", "#D0AC94", "#7ED379", "#012C58",

          "#7A7BFF", "#D68E01", "#353339", "#78AFA1", "#FEB2C6", "#75797C", "#837393", "#943A4D",
          "#B5F4FF", "#D2DCD5", "#9556BD", "#6A714A", "#001325", "#02525F", "#0AA3F7", "#E98176",
          "#DBD5DD", "#5EBCD1", "#3D4F44", "#7E6405", "#02684E", "#962B75", "#8D8546", "#9695C5",
          "#E773CE", "#D86A78", "#3E89BE", "#CA834E", "#518A87", "#5B113C", "#55813B", "#E704C4",
          "#00005F", "#A97399", "#4B8160", "#59738A", "#FF5DA7", "#F7C9BF", "#643127", "#513A01",
          "#6B94AA", "#51A058", "#A45B02", "#1D1702", "#E20027", "#E7AB63", "#4C6001", "#9C6966",
          "#64547B", "#97979E", "#006A66", "#391406", "#F4D749", "#0045D2", "#006C31", "#DDB6D0",
          "#7C6571", "#9FB2A4", "#00D891", "#15A08A", "#BC65E9", "#FFFFFE", "#C6DC99", "#203B3C",

          "#671190", "#6B3A64", "#F5E1FF", "#FFA0F2", "#CCAA35", "#374527", "#8BB400", "#797868",
          "#C6005A", "#3B000A", "#C86240", "#29607C", "#402334", "#7D5A44", "#CCB87C", "#B88183",
          "#AA5199", "#B5D6C3", "#A38469", "#9F94F0", "#A74571", "#B894A6", "#71BB8C", "#00B433",
          "#789EC9", "#6D80BA", "#953F00", "#5EFF03", "#E4FFFC", "#1BE177", "#BCB1E5", "#76912F",
          "#003109", "#0060CD", "#D20096", "#895563", "#29201D", "#5B3213", "#A76F42", "#89412E",
          "#1A3A2A", "#494B5A", "#A88C85", "#F4ABAA", "#A3F3AB", "#00C6C8", "#EA8B66", "#958A9F",
          "#BDC9D2", "#9FA064", "#BE4700", "#658188", "#83A485", "#453C23", "#47675D", "#3A3F00",
          "#061203", "#DFFB71", "#868E7E", "#98D058", "#6C8F7D", "#D7BFC2", "#3C3E6E", "#D83D66",

          "#2F5D9B", "#6C5E46", "#D25B88", "#5B656C", "#00B57F", "#545C46", "#866097", "#365D25",
          "#252F99", "#00CCFF", "#674E60", "#FC009C", "#92896B"]

completeness_report_no_data = {
    "number_of_beds": 'No data',
    "number_admission": 'No data',
    "bed_occupancy": 'No data',
    "icu_turn_over": "No data",
    "unplanned_readmission": 'No data',
    "admission_type": {
        "number_planned": 'No data',
        "number_unplanned": 'No data',
        "percentage_planned": 'No data',
        "percentage_unplanned": 'No data'
    },
    "top_ten_diagnosis": "No data",
    "treatment_withdrawn": {
        "count_yes": 'No data',
        "count_no": 'No data',
        "per_yes": 'No data',
        "per_no": 'No data'
    },
    "left_against_medical_advice": {
        "count_yes": 'No data',
        "per_yes": 'No data'
    },
    "cardiac_arrest": {
        "count": 'No data',
        "per": 'No data'
    },
    "age_planned": {
        "std": 'No data',
        "mean": 'No data'
    },
    "age_unplanned": {
        "std": 'No data',
        "mean": 'No data'
    },
    "gender_planned": {
        "male": 'No data',
        "female": 'No data',
        "per_female": 'No data',
        "per_male": 'No data'
    },
    "gender_unplanned": {
        "male": 'No data',
        "female": 'No data',
        "per_female": 'No data',
        "per_male": 'No data'
    },
    "los_prior_to_icu_planned": 'No data',
    "los_prior_to_icu_unplanned": 'No data',
    "mechanically_ventilated_planned": {
        "count": 'No data',
        "per": 'No data'
    },
    "mechanically_ventilated_unplanned": {
        "count": 'No data',
        "per": 'No data'
    },
    "non_invasive_ventilation_planned": {
        "count": 'No data',
        "per": 'No data'
    },
    "renal_replacement_planned": {
        "count": 'No data',
        "per": 'No data'
    },
    "renal_replacement_unplanned": {
        "count": 'No data',
        "per": 'No data'
    },
    "apache_score": {
        "APACHE_planned": 'No data',
        "APACHE_unplanned": 'No data',
        "stand_planned": 'No data',
        "stand_unplanned": 'No data'
    },
    "los_stats_planned": {
        "mean_stay": 'No data',
        "std": 'No data',
        "median": 'No data',
        "iqr": 'No data'
    },
    "los_stats_unplanned": {
        "mean_stay": 'No data',
        "std": 'No data',
        "median": 'No data',
        "iqr": 'No data'
    },
    "tracheostomies_performed_planned": 'No data',
    "tracheostomies_performed_unplanned": 'No data',
    "clabsi_rate": "No data",
    "clauti_rate": "No data",
    "ivac_rate": "No data",
    "venuos_thromboemboliasm": {
        "count": "No data",
        "per": "No data"
    },
    "Mean_duration_of_mechanical_ventilation": 'No data',
    "unnplanned_reintubain": {
        "count": "No data",
        "per": "No data"
    },
    "stress_ulcer": {
        "count": 'No data',
        "per": 'No data'
    },
    "sbt": {
        "count": 'No data',
        "per": 'No data'
    },
    "Mean_duration_on_antibiotics": 'No data',
    "completeness_core_variables": 'No data',
    "completeness": 'No data',
    "QI_assessment": 'No data',
    "completeness_QI_form_completeness": 'No data',
    "registry_completeness_core_variables": 'No data',
    "registry_completeness": 'No data',
    "registry_QI_assessment": 'No data',
    "registry_completeness_QI_form_completeness": 'No data'

}

covid_registry_level_no_data = {
    'covid_cases': 'No data',
    'number_covid_units': 'No data',
    'covid_in_patients': 'No data',
    'bed_occupancy': 'No data',
    'suspected_covid_label': 'No data',
    'confirmed_covid_label': 'No data',
    'male_cases_label': 'No data',
    'mean_age': 'No data',
    'mec_vent_label': 'No data',
    'non_invasive_label': 'No data',
    'rrt_label': 'No data',
    'covid_admission_by_unit': {'covid_json_data': 'No data', 'colours': 'No data'},
    'covid_discharge_count': 'No data',
    'dead_label': 'No data',
    'mec_vent_dead_label': 'No data',
    'los': 'No data'
}

covid_unit_level_no_data = {
    'covid_cases': 'No data',
    'covid_in_patients': 'No data',
    'bed_occupancy': 'No data',
    'suspected_covid_label': 'No data',
    'confirmed_covid_label': 'No data',
    'male_label': 'No data',
    'mean_age': 'No data',
    'mec_vent_label': 'No data',
    'non_invasive_label': 'No data',
    'rrt_label': 'No data',
    'covid_count_by_day': 'No data',
    'covid_discharge_count': 'No data',
    'dead_label': 'No data',
    'mec_vent_dead_label': 'No data',
    'los': 'No data',
    'unit_type': '',
    'unit_type_cap': ''
}

qi_intervention_no_data = {
    'eligible_clabsi_patients': 'No data',
    'per_clabsi_patients': 'No data',
    'clabsi_rate': 'No data',
    'clabsi_per_change': {'turnOver': 'No data', 'icon': '', 'color': 'green'},
    'clabsi_rate_change': {'turnOver': 'No data', 'icon': '', 'color': 'green'},

    'eligible_clauti_patients': 'No data',
    'per_clauti_patients': 'No data',
    'clauti_rate': 'No data',
    'clauti_per_change': {'turnOver': 'No data', 'icon': '', 'color': 'green'},
    'clauti_rate_change': {'turnOver': 'No data', 'icon': '', 'color': 'green'},

    'eligible_ivac_patients': 'No data',
    'per_ivac_patients': 'No data',
    'ivac_rate': 'No data',
    'ivac_per_change': {'turnOver': 'No data', 'icon': '', 'color': 'green'},
    'ivac_rate_change': {'turnOver': 'No data', 'icon': '', 'color': 'green'}
}

vizhospital_no_data = {
    'length_of_stay': 'No data',
    'admission_month': 'No data',
    'admission_type': {'number_planned': 'No data', 'number_unplanned': 'No data',
                       'percentage_planned': 'No data', 'percentage_unplanned': 'No data'},
    'diagnosis_type': {'non': 'No data', 'post': 'No data'},
    'mechanically_ventilated_on_admission': 'No data',
    'cardiovascular_support_on_admission': 'No data',
    'fio2_by_month': 'No data',
    'fio2_per': 'No data',
    'antibiotics_on_admission': 'No data',
    'time_on_antibiotics': 'No data',
    'mean_days_mechanically_ventilated': 'No data',
    'hierarchical_chart_level1': 'No data',
    'hierarchical_chart_level2': 'No data',
    'bed_occupancy': 'No data',
    'pain_score': 'No data',
    'patient_satisfaction': 'No data',
    'mortality_rate': 'No data',
    'trackeostomy': 'No data',
    'eq5d': 'No data',
    'los_planned': 'No data',
    'los_unplanned': 'No data',
    'diagnosis': 'No data',
    'admission_type_per_month': 'No data',
    'mechanically_ventilated': 'No data',
    'icu_turn_over': 'No data',
    'readmissions': 'No data',
    'smr': 'No data',
    'apache_score': {'APACHE_planned': 'No data', 'APACHE_unplanned': 'No data',
                     'stand_planned': 'No data', 'stand_unplanned': 'No data'},
    'pims_score': {'mean_pims_score_planned': 'No data',
                   'std_pims_score_planned': 'No data',
                   'mean_pims_score_unplanned': 'No data',
                   'std_pims_score_unplanned': 'No data'},
    'dd_type': ''}

vizregonal_no_data = {'admission_type': 'No data',
                      'mechanically_ventilated': 'No data',
                      'mechanically_ventilated_per': 'No data',
                      'fio2_by_month': 'No data',
                      'fio2_per': 'No data',
                      'antibiotics': 'No data',
                      'los_planned': 'No data',
                      'los_unplanned': 'No data',
                      'cardiovascular_support': 'No data',
                      'diagnosis': 'No data',
                      'time_on_antibiotics': 'No data',
                      'number_units': 'No data',
                      'number_beds': 'No data',
                      'number_hospitals': 'No data',
                      'total_admission': 'No data'}
