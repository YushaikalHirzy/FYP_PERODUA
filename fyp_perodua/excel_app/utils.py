import pandas as pd

def clean_vendor_data(grade_queryset, spend_queryset):
    grade_data = pd.DataFrame(list(grade_queryset))
    spend_data = pd.DataFrame(list(spend_queryset))

    # Map grades
    grade_mapping = {"G": 3, "Y": 2, "R": 1, "Not specified": 0}
    for column in ['overall_2022', 'overall_2021', 'overall_2020']:
        grade_data[column] = grade_data[column].map(grade_mapping).fillna(0)
    
    # Convert spend to numeric
    spend_data['overall_5_years'] = pd.to_numeric(spend_data['overall_5_years'], errors='coerce').fillna(0)

    return grade_data, spend_data
