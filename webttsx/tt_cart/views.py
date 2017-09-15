from django.shortcuts import render

# Create your views here.

from django.shortcuts import  render,redirect
from django.http import JsonResponse
from tt_user import user_decorator
from .models import *

@user_decorator.login
def cart(request):
    # cart_list = CartInfo.objects.filter(user_id=14)
    # context = {'carts':cart_list}
    # return render(request, 'tt_cart/cart.html', context)
    uid = request.session['user_id']
    carts = CartInfo.objects.filter(user_id=uid)
    context = {'title':'购物车',
               'page_name':1,
               'carts':carts}
    return render(request, 'tt_cart/cart.html', context)




@user_decorator.login
def add(request, gid, count):
    uid = request.session['user_id']
    gid = int(gid)
    count = int(count)
    carts = CartInfo.objects.filter(user_id=uid, goods_id=gid)
    if len(carts) >= 1:
        cart = carts[0]
        cart.count = cart.count + count
    else:
        cart = CartInfo()
        cart.user_id = uid
        cart.goods_id = gid
        cart.count = count
    cart.save()
    #请求add的时候有个区别，一个是ajax,一个是直接跳转
    if request.is_ajax():#ajax返回数据信息
        count = CartInfo.objects.filter(user_id=request.session['user_id'])
        return JsonResponse({'count':count})
    else:#不是ajxa直接跳转cart
        return redirect('/cart/')

@user_decorator.login
def edit(request, cart_id, count):
    try:
        cart = CartInfo.objects.get(pk=int(cart_id))
        count1 = cart.count=int(count)
        cart.save()
        data = {'ok':0}
    except Exception as e:
        data = {'ok':count1}
    return JsonResponse(data)

@user_decorator.login
def delete(request, cart_id):
    try:
        cart = CartInfo.objects.get(pk=int(cart_id))
        cart.delete()
        data = {'ok':1}
    except Exception as e:
        data = {'ok':0}
    return JsonResponse(data)
