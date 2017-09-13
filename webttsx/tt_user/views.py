# -*- coding:utf-8 -*-
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, redirect
from hashlib import sha1

from . import user_decorator
from .models import *
from django.core.mail import send_mail
from django.conf import settings
from . import task


# Create your views here.
def register(request):
    return render(request, 'tt_user/register.html')

def register_handle(request):
    post = request.POST
    uname = post.get('user_name')
    upwd = post.get('pwd')
    # upwd2 = post.get('cpwd')
    uemail = post.get('email')
    # if upwd != upwd2:
    #     return redirect('/user/register/')
    # upwd = upwd.encode('utf-8')
    s1 = sha1()
    s1.update(upwd.encode('utf-8'))
    upwd_sha1 = s1.hexdigest()

    user = UserInfo()
    user.uname = uname
    user.upwd = upwd_sha1
    user.uemail = uemail
    user.save()

    task.sendemali.delay(user.id, uemail)
    # msg = '<a href="http://127.0.0.1:8000/user/active%s/">点击激活</a>'%(user.id)
    # send_mail('天天生鲜用户激活', '', settings.EMAIL_FROM, [uemail], html_message=msg)

    return HttpResponse('账户注册成功，请到邮箱激活')

#通过邮箱的链接，激活刚注册的账户
def active(request, uid):
    user = UserInfo.objects.get(id=uid)
    user.isActive = True
    user.save()
    return HttpResponse('激活成功，<a href="/user/login/">点击登录</a>')


def register_exist(request):
    uname = request.GET.get('uname')
    uemail = request.GET.get('uemail')
    count = UserInfo.objects.filter(uname=uname).count()
    length = UserInfo.objects.filter(uemail=uemail).count()
    return JsonResponse({'count':count, 'length':length})



def login(request):
    uname = request.COOKIES.get('uname', '')
    context = {'title':'用户登录', 'error_name':0, 'error_pwd':0, 'uname':uname}
    return render(request, 'tt_user/login.html', context)


def login_handle(request):
    #接受请求信息
    post = request.POST
    uname = post.get('username')
    upwd = post.get('pwd')
    jizhu = post.get('jizhu', 0)

    users = UserInfo.objects.filter(uname=uname)
    #判断：如果未查找则用户名错，如果查到则判断密码是否正确
    if len(users) == 1:
        s1 = sha1()
        s1.update(upwd.encode('utf-8'))
        if s1.hexdigest() == users[0].upwd:
            red = HttpResponseRedirect('/user/info/')
            #记住用户名
            if jizhu != 0:
                red.set_cookie('uname', uname)
            else:
                red.set_cookie('uname', max_age=-1)
            request.session['user_id'] = users[0].id
            request.session['user_name'] = uname
            return red
        else:
            context = {'title':'用户登录', 'error_name':0, 'error_pwd':1, 'uname':uname, 'upwd':upwd}
            return render(request, 'tt_user/login.html', context)
    else:
        context = {'title':'用户登录', 'error_name':1, 'error_pwd':0, 'uname':uname, 'upwd':upwd}
        return render(request, 'tt_user/login.html', context)

def logout(request):
    #清除所有session,可以单独清id
    request.session.flush()
    return redirect('/')

@user_decorator.login
def info(request):
    user_email = UserInfo.objects.get(id=request.session['user_id']).uemail
    goods_ids = request.COOKIES.get('goods_ids', ',')
    goods_ids1 = goods_ids.split(',')
    goods_list = []
    # for goods_id in goods_ids1:#导入库后展开
        #与数据库交换5次明确点击顺序　，GoodsInfo.objects.filter(id_in=goods_ids1)不能明确顺序
        # goods_list.append(GoodsInfo.objects.get(id=int(goods_id)))
    context = {'title':'用户中心',
               'user_email':user_email,
               'user_name':request.session['user_name']
               'page_name':1,
               'goods_list':goods_list}
    return render(request, 'tt_user/user_center_info.html', context)

@user_decorator.login
def order(request):
    context = {'title':'用户中心'}
    return render(request, 'tt_user/user_center_order.html', context)

@user_decorator.login
def site(request):
    user = UserInfo.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        post = request._post
        user.ushou = post.get('ushou')
        user.uaddress = post.get('uaddress')
        user.uyoubian = post.get('uyoubian')
        user.uphone = post.get('uphone')
        user.save()
    context = {'title':'用户中心', 'user':user}
    return render(request, 'tt_user/user_center_site.html', context)