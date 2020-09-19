# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import threading

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import NoReverseMatch, reverse
from validate_email import validate_email
from django.contrib.auth.models import User
from rest_framework import status
# Create your views here.
from django.views.generic.base import View
from django.contrib.sites.shortcuts import get_current_site

from cjapp import settings
from .utils import generate_token
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate, login, logout


# class EmailThread(threading.Thread):
#
#     def __init__(self, email_message):
#         self.email_message = email_message
#         threading.Thread.__init__(self)
#
#     def run(self):
#         self.email_message.send()


class RegistrationView(View):

    def get(self, request):
        return render(request, 'auth/register.html')

    def post(self, request):

        context = {
            'data': request.POST,
            'has_error': False
        }

        # data = request.POST
        email = request.POST.get('email', None)
        full_name = request.POST.get('name', None)
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        password2 = request.POST.get('password2', None)

        if not validate_email(email):
            messages.add_message(request, messages.ERROR, 'please provide valid email')
            context['has_error'] = True

        if len(password) < 6:
            messages.add_message(request, messages.ERROR, 'password should be atleast 6 characters long')
            context['has_error'] = True

        if password != password2:
            messages.add_message(request, messages.ERROR, 'password does not match!')
            context['has_error'] = True

        if User.objects.filter(email=email).exists():
            messages.add_message(request, messages.ERROR, 'Email is taken')
            context['has_error'] = True

        if User.objects.filter(username=username).exists():
            messages.add_message(request, messages.ERROR, 'Username is taken')
            context['has_error'] = True

        if context['has_error']:
            return render(request, 'auth/register.html', context=context, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)  # hashing takes place
        user.first_name = full_name.split(" ")[0]
        user.last_name = full_name.split(" ")[-1]
        user.is_active = False
        user.save()

        current_site = get_current_site(request)  # to get current url
        email_subject = 'Activate your account'
        message = render_to_string('auth/activate.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user)
        })

        email_message = EmailMessage(
            email_subject,
            message,
            settings.EMAIL_HOST_USER,
            [email]
        )

        # EmailThread(email_message).start()
        email_message.send()

        messages.add_message(request, messages.SUCCESS, 'Account Created Successfully! ')
        return redirect('login')


class LoginView(View):

    def get(self, request):
        return render(request, 'auth/login.html')

    def post(self, request):
        context = {
            'data': request.POST,
            'has_error': False
        }

        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        if username == '':
            messages.add_message(request, messages.ERROR, 'Username is required')
            context['has_error'] = True

        if password == '':
            messages.add_message(request, messages.ERROR, 'Password is required')
            context['has_error'] = True

        user = authenticate(request, username=username, password=password)
        if not user and not context['has_error']:
            messages.add_message(request, messages.ERROR, 'Password is required')
            context['has_error'] = True
        if context['has_error']:
            return render(request, 'auth/login.html', status=status.HTTP_400_BAD_REQUEST, context=context)

        login(request, user)
        return redirect('home')

        # return render(request, 'auth/login.html')


class ActivateAccountView(View):

    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception as identfier:
            user = None

        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.add_message(request, messages.SUCCESS, 'Account activated successfully! ')
            return redirect('login')

        return render(request, 'auth/activate_failed.html', status=status.HTTP_401_UNAUTHORIZED)


class HomeView(View):

    def get(self, request):
        return render(request, 'home.html')


class LogoutView(View):

    def post(self, request):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Logout Successfully! ')
        return redirect('login')
