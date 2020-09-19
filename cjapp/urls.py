"""cjapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from restapi import views
from restapi.views import *


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'register/', views.RegistrationView.as_view(), name='register'),
    url(r'login/', views.LoginView.as_view(), name='login'),
    url(r'logout/', views.LogoutView.as_view(), name='logout'),
    # url(r'activate/<uidb64>/<token>', views.ActivateAccountView.as_view(), name='activate'), won't work since token size exceeds
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.ActivateAccountView.as_view(), name='activate'),
    url(r'', login_required(views.HomeView.as_view()), name='home'),
]
