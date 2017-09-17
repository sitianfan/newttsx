#! /usr/bin/env python3
# -*- coding:utf-8 -*-
"""
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

"""


class GetPathMiddleware():
    def process_view(self, request, view_func, view_ars, view_kwargs):
        #请求的不是这些路径，就记录下路径
        no_path = ['/user/register/',
                    '/user/register_handle/',
                    '/user/register_exist/',
                    '/user/login/',
                   '/user/login_handle/',
                   '/user/logout/',
                   '/user/yzm/'
                                ]
        if request.path not in no_path:
            request.session['url_path'] = request.get_full_path()


