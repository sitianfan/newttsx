# -*- coding:utf-8 -*-
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, redirect
from hashlib import sha1

from . import user_decorator
from .models import *
from . import task
from tt_goods.models import *
from tt_order.models import *
from django.core.paginator import Paginator,Page

# Create your views here.
def register(request):
    context = {'title':'注册'}
    return render(request, 'tt_user/register.html', context)

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
    count = UserInfo.objects.filter(uname=uname).count()
    return JsonResponse({'count':count})

def register_email(request):
    uemail = request.GET.get('uemail')
    count = UserInfo.objects.filter(uemail=uemail).count()
    print(count)
    return JsonResponse({'count':count})

def login(request):
    uname = request.COOKIES.get('uname', '')
    context = {'title':'用户登录', 'uname':uname}
    return render(request, 'tt_user/login.html', context)

# def login_handle(request):
#     #接受请求信息
#     post = request.POST
#     uname = post.get('username')
#     upwd = post.get('pwd')
#     jizhu = post.get('jizhu', 0)
#
#     users = UserInfo.objects.filter(uname=uname)
#     #判断：如果未查找则用户名错，如果查到则判断密码是否正确
#     if len(users) == 1:
#         s1 = sha1()
#         s1.update(upwd.encode('utf-8'))
            #user是一个对象，[0]是他的各种选项如name,email等等
#         if s1.hexdigest() == users[0].upwd:
#             red = HttpResponseRedirect('/user/info/')
#             #记住用户名
#             if jizhu != 0:
#                 red.set_cookie('uname', uname)
#             else:
#                 red.set_cookie('uname', max_age=-1)
#             request.session['user_id'] = users[0].id
#             request.session['user_name'] = uname
#
#             return red
#         else:
#             context = {'title':'用户登录', 'error_name':0, 'error_pwd':1, 'uname':uname, 'upwd':upwd}
#             return render(request, 'tt_user/login.html', context)
#     else:
#         context = {'title':'用户登录', 'error_name':1, 'error_pwd':0, 'uname':uname, 'upwd':upwd}
#         return render(request, 'tt_user/login.html', context)

def login_handle(request):
    if request.method == 'GET':
        return redirect('/user/login/')
    dict = request.POST
    uname = dict.get('username')
    upwd = dict.get('pwd')
    urem = dict.get('remember', '0')
    yzm = dict.get('yzm')
    #判断验证吗是否正确
    context = {'title':'用户登录', 'uname':uname, 'upwd':upwd, 'uname_error':0, 'upwd_error':0, 'yzm_error':0}
    if yzm.lower() != request.session['verifycode'].lower():
        return render(request, 'tt_user/login.html',  context)
    user = UserInfo.objects.filter(uname=uname)
    if user:
        #用户名存在
        upwd_db = user[0].upwd
        s1 = sha1()
        s1.update(upwd.encode('utf-8'))
        upwd_sha1 = s1.hexdigest()
        #对比密码
        if upwd_db == upwd_sha1:#正确,转到info
            if user[0].isActive:
                #记录地址,在请求页面退出，回到请求页面,即将重定向的页面参数化
                #字典的访问直接用[]没法给默认值，用get方法(一开始直接请求就还没有记录，需要默认值)
                #中间件记录的方法
                response = redirect(request.session.get('url_path', '/'))
                # response = redirect('/user/info/')
                if urem=='1':
                    response.set_cookie('user_name', uname, expires=60*60*24*14)
                else:
                    response.set_cookie('user_name', '', expires=-1)
                request.session['user_id'] = user[0].id
                request.session['uname'] = uname
                return response
            else:
                return HttpResponse('账户未激活,请先激活账户')
        else:
            #密码错误
            context['upwd_error']=1
            return render(request, 'tt_user/login.html',  context)

    else:
        #用户名不存在
        context['uname_error'] = 1
        return render(request, 'tt_user/login.html', context)

def logout(request):
    #清除所有session,可以单独清id
    request.session.flush()
    return redirect('/')

@user_decorator.login
def info(request):
    # user_email = UserInfo.objects.get(id=request.session['user_id']).uemail
    # goods_ids = request.COOKIES.get('goods_ids', ',')
    # goods_ids1 = goods_ids.split(',')
    # goods_list = []
    # for goods_id in goods_ids1:#导入库后展开
    #     # 与数据库交换5次明确点击顺序　，GoodsInfo.objects.filter(id_in=goods_ids1)不能明确顺序
    #     goods_list.append(GoodsInfo.objects.get(id=int(goods_id)))
    # context = {'title':'用户中心',
    #            'user_email':user_email,
    #            'user_name':request.session['user_name'],
    #            'page_name':1,
    #            'goods_list':goods_list}
    #读取最近浏览信息
    browsed_late = request.COOKIES.get('browsed_late')
    uname = request.session.get('uname')
    goods_list = []
    if browsed_late:
        browsed_late_list = browsed_late.split(',')
        for gid in browsed_late_list:
            #维护浏览顺序，逐个添加明确点击顺序　
            goods_list.append(GoodsInfo.objects.get(id=gid))
        # goods_list = GoodsInfo.objects.filter(id__in=(browsed_late_list))

    context = {'title':'用户中心', 'goods_list':goods_list, 'uname':uname}
    return render(request, 'tt_user/user_center_info.html', context)

@user_decorator.login
def order(request):
    #少了分页的功能
    pindex = request.GET.get('page', '1')#接受到页面参数,在传回去
    order = OrderInfo.objects.filter(user_id=request.session.get('user_id')).order_by('-odate')
    paginator = Paginator(order, 4)
    page = paginator.page(int(pindex))

    context = {'title':'我的订单', 'page':page}
    return render(request, 'tt_user/user_center_order.html', context)

@user_decorator.login
def site(request):
    user_id = request.session.get('user_id')
    sites = UserAddressInfo.objects.filter(user_id=user_id)

    # if len(sites)>0:#测试,清除全部
    #     UserAddressInfo.objects.all().delete()

    #修改
    site=UserAddressInfo()
    sid = request.GET.get('sid')#get方式请求过来的
    if sid:#知道修改那个对象
        site = UserAddressInfo.objects.get(id=sid)

    context = {'title':'收货地址','sites':sites, 'site':site}
    return render(request, 'tt_user/user_center_site.html', context)

@user_decorator.login
def site_handle(request):
    dict = request.POST

    user_id = request.session.get('user_id')
    #如果是修改的时候，不新增
    sid = dict.get('sid')

    uname = dict.get('uname')
    uaddress = dict.get('uaddress')
    uphone = dict.get('uphone')
    if sid=='0':#修改和新增就是新建对象的区别
        address = UserAddressInfo()
    else:
        address = UserAddressInfo.objects.get(id=sid)
    address.uname = uname
    address.uphone = uphone
    address.uaddress = uaddress
    address.user_id = user_id


    address.save()
    return redirect('/user/site/')

# def site(request):
#     # .order_by('-uname')[0:5]
#     user = UserInfo.objects.get(id=request.session.get('user_id'))
#
#     context={}
#     if request.method == 'POST':
#         post = request.POST
#         addr = UserAddressInfo()
#
#         addr.user=user
#         addr.uname = post.get('uname')
#         addr.uaddress = post.get('uaddress')
#
#
#         addr.uphone = post.get('uphone')
#
#         context['addr']=addr
#         addr.save()
#     context = {'title':'收货地址', 'user':user}
#     return render(request, 'tt_user/user_center_site.html', context)


from PIL import Image, ImageDraw, ImageFont
def verify_code(request):
    import random
    bgcolor = (random.randrange(20, 100), random.randrange(
        20, 100), 255)
    width = 100
    height = 25
    im = Image.new('RGB', (width, height), bgcolor)
    draw = ImageDraw.Draw(im)
    for i in range(0, 100):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw.point(xy, fill=fill)
    str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]
    font = ImageFont.truetype('FreeMono.ttf', 23)
    fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
    draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
    draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
    draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
    draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
    del draw
    request.session['verifycode'] = rand_str
    #内存文件操作py2
    #import cStringIO
    #buf = cStringIo.StringIO()
    from io import BytesIO
    buf = BytesIO()
    im.save(buf, 'png')
    return HttpResponse(buf.getvalue(), 'image/png')


# def verify_show(request):
#     return render(request, 'booktest/verify_show.html')
#
# def verify_yz(request):
#     yzm = request.POST.get('yzm')
#     verifycode = request.session['verifycode']
#     if yzm.lower() == verifycode.lower():
#         return HttpResponse('验证成功')
#     else:
#         return HttpResponse('验证失败')