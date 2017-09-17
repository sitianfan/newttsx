#! /usr/bin/env python3
# -*- coding:utf-8 -*-
from django.shortcuts import redirect
from django.http import HttpResponseRedirect

#如果未登录则转到登录页面
def login(func):
    # def login_fun(request, *args, **kwargs):
        # if request.session.has_key('user_id'):#py2的代码
        # if 'user_id' in request.session:
        #     return func(request, *args, **kwargs)
        # else:
        #     red = HttpResponseRedirect('/user/login/')
        #     red.set_cookie('url', request.get_full_path())
        #     return red
    def login_fun(request, *args, **kwargs):
        if 'user_id' in request.session:
            return func(request, *args, **kwargs)
        else:
            return redirect('/user/login/')
    return login_fun

