#! /usr/bin/env python3
# -*- coding:utf-8 -*-
from django.shortcuts import render
from .models import *
from django.core.paginator import Page,Paginator
from haystack.generic_views import SearchView
# Create your views here.
def index(request):
    """
    分析首页数据结构，分类对象，最新的４个和最火的３个
    :param request:
    :return:
    """
    type_list = TypeInfo.objects.all()
    list = []
    for type in type_list:
        #查询最新和点击量最高的商品
        new = type.goodsinfo_set.all().order_by('-id')[0:4]
        click = type.goodsinfo_set.all().order_by('-gclick')[0:3]
        #构建数据传给模板
        list.append({'type':type, 'new':new, 'click':click})

    context = {'title':'首页', 'iscart':1, 'list':list}
    return render(request, 'tt_goods/index.html', context)

def list(request, tid, pindex, porder):
    #gtype外键了typeinfo(商品分类)id是默认自动创建的,所以有隐含的id
    #查出来了所有的分类信息
    type_title = TypeInfo.objects.get(id=tid).ttitle
    gnew = GoodsInfo.objects.filter(gtype_id=tid).order_by('-id')[0:2]

    order_str = '-id'
    if porder == '2':
        order_str = '-gprice'
    elif porder == '-3':
        order_str = '-gclick'
    elif porder == '4':
        order_str = 'id'
    elif porder == '5':
        order_str = 'gprice'
    elif porder == '6':
        order_str = 'gclick'
    glist = GoodsInfo.objects.filter(gtype_id=tid).order_by(order_str)



    paginator = Paginator(glist, 10)
    pindex1 = int(pindex)
    page = paginator.page(pindex1)
    context = {'title':'商品列表', 'iscart':1, 'page':page,
               'gnew':gnew, 'tid':tid, 'pindex':pindex1,
               'order':porder, 'type_title':type_title}
    return render(request, 'tt_goods/list.html', context)

def detail(request, gid):
    goods = GoodsInfo.objects.get(id=gid)
    goods.gclick += 1
    goods.save()
    #查询最新的２个商品
    gnew = goods.gtype.goodsinfo_set.all().order_by('-id')[0:2]
    context = {'title':'商品详情', 'iscart':1, 'goods':goods, 'gnew':gnew}
    response = render(request, 'tt_goods/detail.html', context)
    #加入最近浏览
    gid = str(goods.id)
    #browsed_late最近浏览
    browsed_late = request.COOKIES.get('browsed_late', '')
    browsed_late_list = [gid]#如果是空的就直接加个gid
    if browsed_late:
        browsed_late_list =  browsed_late.split(',')
        if gid in browsed_late_list:
            browsed_late_list.remove(gid)
        browsed_late_list.insert(0, gid)
        #控制个数保持在５个
        if len(browsed_late_list)>5:
            browsed_late_list.pop()
     #逐个加入
    response.set_cookie('browsed_late', ','.join(browsed_late_list), expires=60*60*24*7)
    return response

class GoodsSearchView(SearchView):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['iscart'] = 1
        context['qwjs'] = 2
        return context