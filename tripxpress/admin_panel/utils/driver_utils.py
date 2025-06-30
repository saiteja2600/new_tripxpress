# admin_panel/utils/driver_utils.py

import string
import secrets
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from datetime import date
from admin_panel.models import Driver

def generate_random_password(length=12):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_unique_company_email(first_name, last_name):
    base_email = (first_name + last_name).replace(' ', '').lower()
    domain = "tripxpress.com"
    email_candidate = f"{base_email}@{domain}"
    counter = 1

    while Driver.objects.filter(company_email=email_candidate).exists():
        email_candidate = f"{base_email}{counter}@{domain}"
        counter += 1

    return email_candidate

def calculate_age(date_of_birth):
    if not date_of_birth:
        return None
    today = date.today()
    return today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )

def send_driver_credentials_email(first_name, last_name, to_email, company_email, password, joined_at):
    subject = 'Your TripXpress Driver Account Credentials'
    message = f"""
Hi {first_name} {last_name},

Your driver account for TripXpress has been created, Joining Date: {joined_at.strftime('%d-%m-%Y')}.
You can use the following credentials to log in:

Company Email: {company_email}
Password: {password}

Thank you,
The TripXpress Team
"""
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email], fail_silently=False)
