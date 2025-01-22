import json
from django import template

register = template.Library()

@register.filter
def get_grade(year_grades, year):
    # Ensure year_grades is converted to a queryset
    year_grades = year_grades.all() if hasattr(year_grades, 'all') else year_grades
    return next((g.grade for g in year_grades if g.year == year), '-')

@register.filter
def get_grand_total_for_year(data, year):
    year_field = f"year_{year}"
    return getattr(data, year_field, 0)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')

@register.filter
def filter_by_program(program_values, program):
    return program_values.filter(program=program).first()