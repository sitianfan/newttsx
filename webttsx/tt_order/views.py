# -*- coding:utf-8 -*-
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import transaction

from datetime import datetime
from decimal import Decimal
#
from webttsx.tt_user.models import UserInfo
from webttsx.tt_cart.models import *
from webttsx.tt_order import user_decorator
from .models import *

# def order(request):
#     return render(request, 'tt_order/place_order.html')

@user_decorator.login
def order(request):
    #查询用户对象
    user = UserInfo.objects.get(id=request.session['user_id'])
    #根据提交查询购物车信息
    get = request.GET
    cart_ids = get.getlist('cart_id')
    cart_ids1 = [int(item) for item in cart_ids]
    carts = CartInfo.objects.filter(id__in=cart_ids1)
    #构造模板中的数据
    context = {'title':'提交订单',
               'page_name':1,
               'carts':carts,
               'user':user,
               'cart_ids':','.join(cart_ids)}
    return render(request, 'tt_order/place_order.html')
"""
事务：一旦操作失败则全部回退
1.创建订单对象
2.判断商品的库存
3.创建详单对象
4.修改商品库存
5.删除购物车
"""
@transaction.atomic()
@user_decorator.login
def order_handle(request):
    #保存一个点
    tran_id = transaction.savepoint()
    #接收购物车编号
    cart_ids = request.POST.get('cart_ids')
    try:
        #创建订单对象
        order = OrderInfo()
        now = datetime.now()
        uid = request.session['user_id']
        order.oid = '%s%d'%(now.strftime('%Y%m%d%H%M%S'), uid)
        order.user_id = uid
        order.odate = now
        order.ototal = Decimal(request.POST.get('total'))
        order.save()

        cart_ids1 = [int(item) for item in cart_ids.split(',')]
        for id1 in cart_ids1:
            detail = OrderDetailInfo()
            detail.order = order
            #查询购物车信息
            cart = CartInfo.objects.get(id=id1)
            #判断商品库存
            goods = cart.goods
            if goods.gkucun >= cart.count:
                #减少商品库存
                goods.gkucun = cart.goods.gkucun - cart.count
                goods.save()
                #完善详单信息
                detail.goods_id = goods.id
                detail.price = goods.gprice
                detail.count = cart.count
                detail.save()
                #删除购物车数据
                cart.delete()
            else:
                #库存小于购买数量，事务回滚
                transaction.savepoint_rollback(tran_id)
                return redirect('/cart/')
            #完成事务，提交
        transaction.savepoint_commit(tran_id)
    except Exception as e:
        print(e)
        transaction.savepoint_rollback(tran_id)
    return redirect('/tt_user/place_order/')


@user_decorator.login
def pay(request, oid):
    order = OrderInfo.objects.get(oid=oid)
    order.oIsPay = True
    order.save()
    context = {'order':order}
    return render(request, 'tt_order/pay.html', context)