
from django.db import models

# Create your models here.
class CartInfo(models.Model):
    user=models.ForeignKey('tt_user.UserInfo')
    goods=models.ForeignKey('tt_goods.GoodsInfo')
    count=models.IntegerField()

