# models.py
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from djongo.models.fields import ObjectIdField


class Customer(models.Model):
    _id = ObjectIdField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    euroBalance = models.FloatField(default=20000)
    bitcoinBalance = models.FloatField(default=0)
    profitLoss = models.FloatField(default=0)
    pendingBitcoin = models.FloatField(default=0)
    pendingEuro = models.FloatField(default=0)
    ipAddresses = models.Field(default=[])

    def __str__(self):
        return f"{self.user}({self._id})"


class Order(models.Model):
    _id = ObjectIdField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=4, choices=[
        ('buy', 'buy'),
        ('sell', 'sell')
    ], default='buy')
    status = models.CharField(max_length=6, choices=[
        ('open', 'open'),
        ('closed', 'closed')
    ], default='open')
    openDatetime = models.DateTimeField(default=None, blank=True)
    closedDatetime = models.DateTimeField(default=None, blank=True)
    PartiallyClosedDatetime = models.DateTimeField(default=None, blank=True)
    amount = models.FloatField(default=0)
    pricePerBitcoin = models.FloatField(default=0)
    totalPrice = models.FloatField(default=0)
    profitLoss = models.FloatField(default=0)

    # function to set the open date
    def setOpenDatetime(self):
        currentTime = datetime.now()
        roundedCurrentTime = currentTime.replace(microsecond=0)
        self.openDatetime = roundedCurrentTime
        self.save()

    # function to set the closed date
    def setClosedDatetime(self):
        currentTime = datetime.now()
        roundedCurrentTime = currentTime.replace(microsecond=0)
        self.closedDatetime = roundedCurrentTime
        self.save()

    # function to set the partially closed date
    def setPartiallyClosedDatetime(self):
        currentTime = datetime.now()
        roundedCurrentTime = currentTime.replace(microsecond=0)
        self.PartiallyClosedDatetime = roundedCurrentTime
        self.save()

    def __str__(self):
        return f"Order({self._id})"
