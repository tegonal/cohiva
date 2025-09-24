from django.shortcuts import render

from geno.forms import process_registration_forms


def registration(request, registration_id=None):
    template_data = {}
    template_data["forms"] = process_registration_forms(request, selector=registration_id)
    return render(request, "website/registration_form.html", template_data)


def get_calendar_events(calendar_id, start, end):
    return []
