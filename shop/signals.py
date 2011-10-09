from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404




# methods to update order object after successful / failed payment 
