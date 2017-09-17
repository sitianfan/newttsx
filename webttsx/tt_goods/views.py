from django.shortcuts import render

# Create your views here.
def index(request):
    context = {'title':'首页'}
    return render(request, 'tt_goods/index.html', context)