# -*- coding:utf-8 -*-
from datetime import datetime
from decimal import Decimal

from django.db import transaction
from django.shortcuts import render, redirect

from tt_cart.models import *
from tt_user import user_decorator
from tt_user.models import UserInfo
from .models import *





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
    return render(request, 'tt_order/place_order.html', context)


"""
事务：一旦操作失败则全部回退
1.创建订单对象
2.判断商品的库存
3.创建详单对象
4.修改商品库存
5.删除购物车
"""
# @transaction.atomic
# @user_decorator.login
# def order_handle(request):
#     #保存一个点
#     tran_id = transaction.savepoint()
#     #接收购物车编号
#     cart_ids = request.POST.getlist('cart_ids')
#     try:
#         #创建订单对象
#         order = OrderInfo()
#         now = datetime.now()
#         uid = request.session['user_id']
#         order.oid = '%s%d'%(now.strftime('%Y%m%d%H%M%S'), uid)
#         order.user_id = uid
#         order.odate = now
#         order.ototal = Decimal(request.POST.get('total'))
#         order.save()
#
#         cart_ids1 = [int(item) for item in cart_ids.split(',')]
#         for id1 in cart_ids1:
#             detail = OrderDetailInfo()
#             detail.order = order
#             #查询购物车信息
#             cart = CartInfo.objects.get(id=id1)
#             #判断商品库存
#             goods = cart.goods
#             if goods.gkucun >= cart.count:
#                 #减少商品库存
#                 goods.gkucun = cart.goods.gkucun - cart.count
#                 goods.save()
#                 #完善详单信息
#                 detail.goods_id = goods.id
#                 detail.price = goods.gprice
#                 detail.count = cart.count
#                 detail.money = detail.price*detail.count
#                 detail.save()
#                 #删除购物车数据
#                 cart.delete()
#             else:
#                 #库存小于购买数量，事务回滚
#                 transaction.savepoint_rollback(tran_id)
#                 return redirect('/cart/')
#             #完成事务，提交
#         transaction.savepoint_commit(tran_id)
#     except Exception as e:
#         print(e)
#         transaction.savepoint_rollback(tran_id)
#     return redirect('/user/info/')

# def order(request):
#     dict = request.GET
#     cid = dict.getlist('cid')
#     carts = CartInfo.objects.filter(id__in=cid)
#     context = {'carts':carts}
#     return render(request, 'tt_order/place_order.html', context)


@transaction.atomic
@user_decorator.login
def order_handle(request):
    cid = request.POST.getlist('cid')
    #开启事物
    sid = transaction.savepoint()
    #创建订单主表
    order = OrderInfo()
    # uid = request.session['user_id']
    # order.oid = '%s%s'%(datetime.now().strftime('%Y%m%d%H%M%S'), uid)
    # order.user_id = uid
    # order_ototal = Decimal(request.POST.get('total'))
    order.oid = '%s%s'%(datetime.now().strftime('%Y%m%d%H%M%S'), '14')
    order.user_id = 14
    order.ototal = 0
    order.oaddress = ''
    order.save()
    carts = CartInfo.objects.filter(id__in=cid)
    total = 0
    #判断库存
    isOk = True
    for cart in carts:
        #库存足够可以购买
        if cart.goods.gkucun >= cart.count:
            detail = OrderDetailInfo()
            detail.order = order
            detail.goods = cart.goods
            detail.price = cart.goods.gprice
            detail.count = cart.count
            detail.save()
            #计算总价
            total += detail.count*detail.price
            cart.goods.gkucun -= cart.count
            cart.goods.save()
            #删除购物车数据
            cart.delete()
        else:
            isOk = False
            break
    if isOk:
        #订单成功
        order.ototal = total
        order.save()
        transaction.savepoint_commit(sid)
        return redirect('/user/info/')
    else:
        #订单失败
        transaction.savepoint_rollback(sid)
        return redirect('/cart/')