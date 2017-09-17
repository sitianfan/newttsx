#! /usr/bin/env python3
# -*- coding:utf-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register/$', views.register),
    url(r'^register_handle/$', views.register_handle),
    url(r'^active(\d+)/$', views.active),
    url(r'^register_exist/$', views.register_exist),
    url(r'^login/$', views.login),
    url(r'^register_email/$', views.register_email),
    url(r'^login_handle/$', views.login_handle),
    url(r'^info/$', views.info),
    url(r'^order/$', views.order),
    url(r'^site/$', views.site),
    url(r'^logout/$', views.logout),
    url(r'^yzm/$', views.verify_code),
]

