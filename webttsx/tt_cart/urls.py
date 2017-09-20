#! /usr/bin/env python3
# -*- coding:utf-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.cart),
    url(r'^add/$', views.add),
    url(r'^edit/$', views.edit),
    url(r'^remove/$', views.remove),
    url(r'^count/$', views.count),
]

