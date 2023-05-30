# views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Customer, Order
import random
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from bson.objectid import ObjectId
from .forms import CreateUserForm, NewOrderForm
from django.contrib.auth import authenticate, login, logout


def homePage(request):
    return render(request, 'project/index.html')


def registerPage(request):
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            customer = Customer(user=user)
            customer.bitcoinBalance = random.randint(1, 10)
            customer.save()
            return redirect('loginPage')
    else:
        form = CreateUserForm
        return render(request, 'project/customerAuth/register.html', {'form': form})


def loginPage(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profilePage')
    return render(request, 'project/customerAuth/login.html')


def customLoginRequired(view_func):
    decorated_view_func = login_required(view_func)

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('homePage')
        else:
            return decorated_view_func(request, *args, **kwargs)

    return wrapper


@customLoginRequired
def logoutPage(request):
    logout(request)
    return redirect('loginPage')


@customLoginRequired
def profilePage(request):
    return render(request, 'project/customerAuth/profile.html')


@customLoginRequired
def dashboardPage(request):
    user = request.user
    customer = Customer.objects.get(user=user)
    availableBitcoin = customer.bitcoinBalance - customer.pendingBitcoin
    availableEuro = customer.euroBalance - customer.pendingEuro
    context = {
        "customer": customer,
        "availableBitcoin": availableBitcoin,
        "availableEuro": availableEuro,
    }
    return render(request, 'project/customerAct/dashboard.html', context)


@customLoginRequired
def newOrderPage(request):
    newOrderUser = request.user
    newOrderCustomer = Customer.objects.get(user=newOrderUser)
    openSellOrders = Order.objects.filter(
        Q(status='open') & Q(type='sell') & ~Q(user=newOrderUser)
    )
    openBuyOrders = Order.objects.filter(
        Q(status='open') & Q(type='buy') & ~Q(user=newOrderUser)
    )
    # user interacts with the page
    if request.method == "POST":
        form = NewOrderForm(request.POST)
        # if new order fields are valid
        if form.is_valid():
            newOrder = form.save(commit=False)
            # check that new order amount is greater than zero
            if newOrder.amount > 0:
                # check that new order price per bitcoin is greater than zero
                if newOrder.pricePerBitcoin > 0:
                    newOrder.user = newOrderUser
                    newOrder.totalPrice = newOrder.amount * newOrder.pricePerBitcoin
                    # if it's a BUY order
                    if newOrder.type == 'buy':
                        # check that user has enough €
                        if (newOrderCustomer.euroBalance - newOrderCustomer.pendingEuro) >= newOrder.totalPrice:
                            newOrderCustomer.pendingEuro += newOrder.totalPrice
                            # the BUY order is valid and ready to be created
                            newOrder.setOpenDatetime()
                            newOrder.save()
                            newOrderCustomer.save()
                            # check if the new BUY order can be matched with an open SELL order
                            isOrderMatched = False
                            for openSellOrder in openSellOrders:
                                # open sell order user and customer handle
                                openSellOrderUser = openSellOrder.user
                                openSellOrderCustomer = Customer.objects.get(user=openSellOrderUser)
                                # if the new order isn't already matched
                                if isOrderMatched is False:
                                    # if the pricePerBitcoin of the new order is equal than the pricePerBitcoin of an open order
                                    if newOrder.pricePerBitcoin == openSellOrder.pricePerBitcoin:
                                        # if the new order btc amount is the same as the open order btc amount
                                        if newOrder.amount == openSellOrder.amount:
                                            # the 2 orders can be matched together and both flagged as closed
                                            # orders match
                                            # new order
                                            newOrderCustomer.euroBalance = newOrderCustomer.euroBalance - newOrder.totalPrice
                                            newOrderCustomer.bitcoinBalance = newOrderCustomer.bitcoinBalance + newOrder.amount
                                            newOrderCustomer.pendingEuro = newOrderCustomer.pendingEuro - newOrder.totalPrice
                                            newOrderCustomer.profitLoss = newOrderCustomer.profitLoss - newOrder.totalPrice
                                            newOrder.profitLoss = newOrder.profitLoss - newOrder.totalPrice
                                            newOrder.setClosedDatetime()
                                            # open order
                                            openSellOrderCustomer.bitcoinBalance = openSellOrderCustomer.bitcoinBalance - openSellOrder.amount
                                            openSellOrderCustomer.euroBalance = openSellOrderCustomer.euroBalance + openSellOrder.totalPrice
                                            openSellOrderCustomer.pendingBitcoin = openSellOrderCustomer.pendingBitcoin - openSellOrder.amount
                                            openSellOrderCustomer.profitLoss = openSellOrderCustomer.profitLoss - openSellOrder.totalPrice
                                            openSellOrder.profitLoss = openSellOrder.profitLoss - openSellOrder.totalPrice
                                            openSellOrder.setClosedDatetime()
                                            # orders flag as closed and orders & customers save
                                            newOrder.status = 'closed'
                                            openSellOrder.status = 'closed'
                                            newOrder.save()
                                            newOrderCustomer.save()
                                            openSellOrder.save()
                                            openSellOrderCustomer.save()
                                            isOrderMatched = True
                                        # else if the new order btc amount is less than the open order btc amount
                                        elif newOrder.amount < openSellOrder.amount:
                                            # the new order can be matched with a part of the open order: the new order is fully matched and can be flagged as closed, instead the open order remains open and needs to be updated
                                            # new order close
                                            newOrderCustomer.euroBalance = newOrderCustomer.euroBalance - newOrder.totalPrice
                                            newOrderCustomer.bitcoinBalance = newOrderCustomer.bitcoinBalance + newOrder.amount
                                            newOrderCustomer.pendingEuro = newOrderCustomer.pendingEuro - newOrder.totalPrice
                                            newOrderCustomer.profitLoss = newOrderCustomer.profitLoss - newOrder.totalPrice
                                            newOrder.profitLoss = newOrder.profitLoss - newOrder.totalPrice
                                            newOrder.setClosedDatetime()
                                            newOrder.status = 'closed'
                                            # open order update
                                            openSellOrderCustomer.bitcoinBalance = openSellOrderCustomer.bitcoinBalance - newOrder.amount
                                            openSellOrderCustomer.euroBalance = openSellOrderCustomer.euroBalance + (
                                                    openSellOrder.pricePerBitcoin * newOrder.amount)
                                            openSellOrderCustomer.pendingBitcoin = openSellOrderCustomer.pendingBitcoin - newOrder.amount
                                            openSellOrder.amount = openSellOrder.amount - newOrder.amount
                                            openSellOrder.totalPrice = openSellOrder.amount * openSellOrder.pricePerBitcoin
                                            openSellOrderCustomer.profitLoss = openSellOrderCustomer.profitLoss - openSellOrder.totalPrice
                                            openSellOrder.profitLoss = openSellOrder.profitLoss - openSellOrder.totalPrice
                                            openSellOrder.setPartiallyClosedDatetime()
                                            # new order and related customer save
                                            newOrder.save()
                                            newOrderCustomer.save()
                                            # open order and related customer save
                                            openSellOrder.save()
                                            openSellOrderCustomer.save()
                                            isOrderMatched = True
                                        # else the new order btc amount is greater than the open order btc amount
                                        else:
                                            # a part of the new order can be matched with the open order: the open order is fully matched and can be flagged as closed, instead the new order remains open and needs to be updated
                                            # new order update
                                            newOrderCustomer.euroBalance = newOrderCustomer.euroBalance - openSellOrder.totalPrice
                                            newOrderCustomer.bitcoinBalance = newOrderCustomer.bitcoinBalance + openSellOrder.amount
                                            newOrderCustomer.pendingEuro = newOrderCustomer.pendingEuro - openSellOrder.totalPrice
                                            newOrder.amount = newOrder.amount - openSellOrder.amount
                                            newOrder.totalPrice = newOrder.amount * newOrder.pricePerBitcoin
                                            newOrderCustomer.profitLoss = newOrderCustomer.profitLoss - newOrder.totalPrice
                                            newOrder.profitLoss = newOrder.profitLoss - newOrder.totalPrice
                                            newOrder.setPartiallyClosedDatetime()
                                            # open order close
                                            openSellOrderCustomer.bitcoinBalance = openSellOrderCustomer.bitcoinBalance - openSellOrder.amount
                                            openSellOrderCustomer.euroBalance = openSellOrderCustomer.euroBalance + openSellOrder.totalPrice
                                            openSellOrderCustomer.pendingBitcoin = openSellOrderCustomer.pendingBitcoin - openSellOrder.amount
                                            openSellOrderCustomer.profitLoss = openSellOrderCustomer.profitLoss - openSellOrder.totalPrice
                                            openSellOrder.profitLoss = openSellOrder.profitLoss - openSellOrder.totalPrice
                                            openSellOrder.setClosedDatetime()
                                            openSellOrder.status = 'closed'
                                            # new order and related customer save
                                            newOrder.save()
                                            newOrderCustomer.save()
                                            # open order and related customer save
                                            openSellOrder.save()
                                            openSellOrderCustomer.save()
                                            isOrderMatched = False
                                    # if the pricePerBitcoin of the new order is greater than the pricePerBitcoin of an open order
                                    elif newOrder.pricePerBitcoin > openSellOrder.pricePerBitcoin:
                                        # if the new order btc amount is the same as the open order btc amount
                                        if newOrder.amount == openSellOrder.amount:
                                            # the 2 orders can be matched together and both flagged as closed
                                            # new order match and related customer refund of difference between prices per bitcoin
                                            newOrderCustomer.euroBalance = newOrderCustomer.euroBalance - openSellOrder.totalPrice
                                            newOrderCustomer.bitcoinBalance = newOrderCustomer.bitcoinBalance + newOrder.amount
                                            newOrderCustomer.pendingEuro = newOrderCustomer.pendingEuro - newOrder.totalPrice
                                            newOrder.pricePerBitcoin = openSellOrder.pricePerBitcoin
                                            newOrder.totalPrice = openSellOrder.totalPrice
                                            newOrderCustomer.profitLoss = newOrderCustomer.profitLoss - newOrder.totalPrice
                                            newOrder.profitLoss = newOrder.profitLoss - newOrder.totalPrice
                                            newOrder.setClosedDatetime()
                                            # open order match
                                            openSellOrderCustomer.bitcoinBalance = openSellOrderCustomer.bitcoinBalance - openSellOrder.amount
                                            openSellOrderCustomer.euroBalance = openSellOrderCustomer.euroBalance + openSellOrder.totalPrice
                                            openSellOrderCustomer.pendingBitcoin = openSellOrderCustomer.pendingBitcoin - openSellOrder.amount
                                            openSellOrderCustomer.profitLoss = openSellOrderCustomer.profitLoss - openSellOrder.totalPrice
                                            openSellOrder.profitLoss = openSellOrder.profitLoss - openSellOrder.totalPrice
                                            openSellOrder.setClosedDatetime()
                                            # orders flag as closed and orders & customers save
                                            newOrder.status = 'closed'
                                            openSellOrder.status = 'closed'
                                            newOrder.save()
                                            newOrderCustomer.save()
                                            openSellOrder.save()
                                            openSellOrderCustomer.save()
                                            isOrderMatched = True
                                        # else if the new order btc amount is less than the open order btc amount
                                        elif newOrder.amount < openSellOrder.amount:
                                            # the new order can be matched with a part of the open order: the new order is fully matched and can be flagged as closed, instead the open order remains open and needs to be updated
                                            # new order close and related customer refund of difference between prices per bitcoin
                                            newOrderCustomer.pendingEuro = newOrderCustomer.pendingEuro - newOrder.totalPrice
                                            newOrder.pricePerBitcoin = openSellOrder.pricePerBitcoin
                                            newOrder.totalPrice = newOrder.pricePerBitcoin * newOrder.amount
                                            newOrderCustomer.euroBalance = newOrderCustomer.euroBalance - newOrder.totalPrice
                                            newOrderCustomer.bitcoinBalance = newOrderCustomer.bitcoinBalance + newOrder.amount
                                            newOrderCustomer.profitLoss = newOrderCustomer.profitLoss - newOrder.totalPrice
                                            newOrder.profitLoss = newOrder.profitLoss - newOrder.totalPrice
                                            newOrder.setClosedDatetime()
                                            newOrder.status = 'closed'
                                            # open order update
                                            openSellOrderCustomer.bitcoinBalance = openSellOrderCustomer.bitcoinBalance - newOrder.amount
                                            openSellOrderCustomer.euroBalance = openSellOrderCustomer.euroBalance + newOrder.totalPrice
                                            openSellOrderCustomer.pendingBitcoin = openSellOrderCustomer.pendingBitcoin - newOrder.amount
                                            openSellOrder.amount = openSellOrder.amount - newOrder.amount
                                            openSellOrder.totalPrice = openSellOrder.amount * openSellOrder.pricePerBitcoin
                                            openSellOrderCustomer.profitLoss = openSellOrderCustomer.profitLoss - openSellOrder.totalPrice
                                            openSellOrder.profitLoss = openSellOrder.profitLoss - openSellOrder.totalPrice
                                            openSellOrder.setPartiallyClosedDatetime()
                                            # new order and related customer save
                                            newOrder.save()
                                            newOrderCustomer.save()
                                            # open order and related customer save
                                            openSellOrder.save()
                                            openSellOrderCustomer.save()
                                            isOrderMatched = True
                                        # else the new order btc amount is greater than the open order btc amount
                                        else:
                                            # a part of the new order can be matched with the open order: the open order is fully matched and can be flagged as closed, instead the new order remains open and needs to be updated
                                            # open order close
                                            openSellOrder.totalPrice = openSellOrder.amount * newOrder.pricePerBitcoin
                                            openSellOrderCustomer.bitcoinBalance = openSellOrderCustomer.bitcoinBalance - openSellOrder.amount
                                            openSellOrderCustomer.euroBalance = openSellOrderCustomer.euroBalance + openSellOrder.totalPrice
                                            openSellOrderCustomer.pendingBitcoin = openSellOrderCustomer.pendingBitcoin - openSellOrder.amount
                                            openSellOrderCustomer.profitLoss = openSellOrderCustomer.profitLoss - openSellOrder.totalPrice
                                            openSellOrder.profitLoss = openSellOrder.profitLoss - openSellOrder.totalPrice
                                            openSellOrder.setClosedDatetime()
                                            openSellOrder.status = 'closed'
                                            # new order update
                                            newOrderCustomer.euroBalance = newOrderCustomer.euroBalance - openSellOrder.totalPrice
                                            newOrderCustomer.bitcoinBalance = newOrderCustomer.bitcoinBalance + openSellOrder.amount
                                            newOrderCustomer.pendingEuro = newOrderCustomer.pendingEuro - openSellOrder.totalPrice
                                            newOrder.amount = newOrder.amount - openSellOrder.amount
                                            newOrder.totalPrice = newOrder.amount * newOrder.pricePerBitcoin
                                            newOrderCustomer.profitLoss = newOrderCustomer.profitLoss - newOrder.totalPrice
                                            newOrder.profitLoss = newOrder.profitLoss - newOrder.totalPrice
                                            newOrder.setPartiallyClosedDatetime()
                                            # new order and related customer save
                                            newOrder.save()
                                            newOrderCustomer.save()
                                            # open order and related customer save
                                            openSellOrder.save()
                                            openSellOrderCustomer.save()
                                            isOrderMatched = False
                        else:
                            # error message
                            print('User has not enough funds')
                            return redirect('newOrderPage')
                    # else it's a SELL order
                    else:
                        # check that user has enough BTC
                        if (newOrderCustomer.bitcoinBalance - newOrderCustomer.pendingBitcoin) >= newOrder.amount:
                            newOrderCustomer.pendingBitcoin += newOrder.amount
                            # the SELL order is valid and ready to be created
                            newOrder.setOpenDatetime()
                            newOrder.save()
                            newOrderCustomer.save()
                            # check if the new SELL order can be matched with an open BUY order
                            isOrderMatched = False
                            for openBuyOrder in openBuyOrders:
                                # open buy order user and customer handle
                                openBuyOrderUser = openBuyOrder.user
                                openBuyOrderCustomer = Customer.objects.get(user=openBuyOrderUser)
                                # if the new order isn't already matched
                                if isOrderMatched is False:
                                    # if the pricePerBitcoin of the new order is equal than the pricePerBitcoin of an open order
                                    if newOrder.pricePerBitcoin == openBuyOrder.pricePerBitcoin:
                                        # if the new order btc amount is the same as the open order btc amount
                                        if newOrder.amount == openBuyOrder.amount:
                                            # the 2 orders can be matched together and both flagged as closed
                                            # orders match
                                            # new order
                                            newOrderCustomer.euroBalance = newOrderCustomer.euroBalance + newOrder.totalPrice
                                            newOrderCustomer.bitcoinBalance = newOrderCustomer.bitcoinBalance - newOrder.amount
                                            newOrderCustomer.pendingBitcoin = newOrderCustomer.pendingBitcoin - newOrder.amount
                                            newOrderCustomer.profitLoss = newOrderCustomer.profitLoss + newOrder.totalPrice
                                            newOrder.profitLoss = newOrder.profitLoss + newOrder.totalPrice
                                            newOrder.setClosedDatetime()
                                            # open order
                                            openBuyOrderCustomer.bitcoinBalance = openBuyOrderCustomer.bitcoinBalance + openBuyOrder.amount
                                            openBuyOrderCustomer.euroBalance = openBuyOrderCustomer.euroBalance - openBuyOrder.totalPrice
                                            openBuyOrderCustomer.pendingEuro = openBuyOrderCustomer.pendingEuro - openBuyOrder.totalPrice
                                            openBuyOrderCustomer.profitLoss = openBuyOrderCustomer.profitLoss - openBuyOrder.totalPrice
                                            openBuyOrder.profitLoss = openBuyOrder.profitLoss - openBuyOrder.totalPrice
                                            openBuyOrder.setClosedDatetime()
                                            # orders flag as closed and orders & customers save
                                            newOrder.status = 'closed'
                                            openBuyOrder.status = 'closed'
                                            newOrder.save()
                                            newOrderCustomer.save()
                                            openBuyOrder.save()
                                            openBuyOrderCustomer.save()
                                            isOrderMatched = True
                                        # else if the new order btc amount is less than the open order btc amount
                                        elif newOrder.amount < openBuyOrder.amount:
                                            # the new order can be matched with a part of the open order: the new order is fully matched and can be flagged as closed, instead the open order remains open and needs to be updated
                                            # new order close
                                            newOrderCustomer.euroBalance = newOrderCustomer.euroBalance + newOrder.totalPrice
                                            newOrderCustomer.bitcoinBalance = newOrderCustomer.bitcoinBalance - newOrder.amount
                                            newOrderCustomer.pendingBitcoin = newOrderCustomer.pendingBitcoin - newOrder.amount
                                            newOrderCustomer.profitLoss = newOrderCustomer.profitLoss + newOrder.totalPrice
                                            newOrder.profitLoss = newOrder.profitLoss + newOrder.totalPrice
                                            newOrder.setClosedDatetime()
                                            newOrder.status = 'closed'
                                            # open order update
                                            openBuyOrderCustomer.bitcoinBalance = openBuyOrderCustomer.bitcoinBalance + newOrder.amount
                                            openBuyOrderCustomer.euroBalance = openBuyOrderCustomer.euroBalance - newOrder.totalPrice
                                            openBuyOrderCustomer.pendingEuro = openBuyOrderCustomer.pendingEuro - newOrder.totalPrice
                                            openBuyOrder.amount = openBuyOrder.amount - newOrder.amount
                                            openBuyOrder.totalPrice = openBuyOrder.amount * openBuyOrder.pricePerBitcoin
                                            openBuyOrderCustomer.profitLoss = openBuyOrderCustomer.profitLoss - openBuyOrder.totalPrice
                                            openBuyOrder.profitLoss = openBuyOrder.profitLoss - openBuyOrder.totalPrice
                                            openBuyOrder.setPartiallyClosedDatetime()
                                            # new order and related customer save
                                            newOrder.save()
                                            newOrderCustomer.save()
                                            # open order and related customer save
                                            openBuyOrder.save()
                                            openBuyOrderCustomer.save()
                                            isOrderMatched = True
                                        # else the new order btc amount is greater than the open order btc amount
                                        else:
                                            # a part of the new order can be matched with the open order: the open order is fully matched and can be flagged as closed, instead the new order remains open and needs to be updated
                                            # new order update
                                            newOrderCustomer.euroBalance = newOrderCustomer.euroBalance + openBuyOrder.totalPrice
                                            newOrderCustomer.bitcoinBalance = newOrderCustomer.bitcoinBalance - openBuyOrder.amount
                                            newOrderCustomer.pendingBitcoin = newOrderCustomer.pendingBitcoin - openBuyOrder.amount
                                            newOrder.amount = newOrder.amount - openBuyOrder.amount
                                            newOrder.totalPrice = newOrder.amount * newOrder.pricePerBitcoin
                                            newOrderCustomer.profitLoss = newOrderCustomer.profitLoss + newOrder.totalPrice
                                            newOrder.profitLoss = newOrder.profitLoss + newOrder.totalPrice
                                            newOrder.setPartiallyClosedDatetime()
                                            # open order close
                                            openBuyOrderCustomer.bitcoinBalance = openBuyOrderCustomer.bitcoinBalance + openBuyOrder.amount
                                            openBuyOrderCustomer.euroBalance = openBuyOrderCustomer.euroBalance - openBuyOrder.totalPrice
                                            openBuyOrderCustomer.pendingEuro = openBuyOrderCustomer.pendingEuro - openBuyOrder.totalPrice
                                            openBuyOrderCustomer.profitLoss = openBuyOrderCustomer.profitLoss - openBuyOrder.totalPrice
                                            openBuyOrder.profitLoss = openBuyOrder.profitLoss - openBuyOrder.totalPrice
                                            openBuyOrder.setClosedDatetime()
                                            openBuyOrder.status = 'closed'
                                            # new order and related customer save
                                            newOrder.save()
                                            newOrderCustomer.save()
                                            # open order and related customer save
                                            openBuyOrder.save()
                                            openBuyOrderCustomer.save()
                                            isOrderMatched = False
                                    # if the pricePerBitcoin of the new order is greater than the pricePerBitcoin of an open order
                                    elif newOrder.pricePerBitcoin < openBuyOrder.pricePerBitcoin:
                                        # if the new order btc amount is the same as the open order btc amount
                                        if newOrder.amount == openBuyOrder.amount:
                                            # the 2 orders can be matched together and both flagged as closed
                                            # new order match and related customer refund of difference between prices per bitcoin
                                            newOrderCustomer.euroBalance = newOrderCustomer.euroBalance + newOrder.totalPrice
                                            newOrderCustomer.bitcoinBalance = newOrderCustomer.bitcoinBalance - newOrder.amount
                                            newOrderCustomer.pendingBitcoin = newOrderCustomer.pendingBitcoin - newOrder.amount
                                            newOrderCustomer.profitLoss = newOrderCustomer.profitLoss + newOrder.totalPrice
                                            newOrder.profitLoss = newOrder.profitLoss + newOrder.totalPrice
                                            newOrder.setClosedDatetime()
                                            # open order match
                                            openBuyOrderCustomer.bitcoinBalance = openBuyOrderCustomer.bitcoinBalance + openBuyOrder.amount
                                            openBuyOrderCustomer.euroBalance = openBuyOrderCustomer.euroBalance - newOrder.totalPrice
                                            openBuyOrderCustomer.pendingEuro = openBuyOrderCustomer.pendingEuro - openBuyOrder.totalPrice
                                            openBuyOrder.pricePerBitcoin = newOrder.pricePerBitcoin
                                            openBuyOrder.totalPrice = newOrder.totalPrice
                                            openBuyOrderCustomer.profitLoss = openBuyOrderCustomer.profitLoss - openBuyOrder.totalPrice
                                            openBuyOrder.profitLoss = openBuyOrder.profitLoss - openBuyOrder.totalPrice
                                            openBuyOrder.setClosedDatetime()
                                            # orders flag as closed and orders & customers save
                                            newOrder.status = 'closed'
                                            openBuyOrder.status = 'closed'
                                            newOrder.save()
                                            newOrderCustomer.save()
                                            openBuyOrder.save()
                                            openBuyOrderCustomer.save()
                                            isOrderMatched = True
                                        # else if the new order btc amount is less than the open order btc amount
                                        elif newOrder.amount < openBuyOrder.amount:
                                            # the new order can be matched with a part of the open order: the new order is fully matched and can be flagged as closed, instead the open order remains open and needs to be updated
                                            # new order close and related customer refund of difference between prices per bitcoin
                                            newOrderCustomer.pendingBitcoin = newOrderCustomer.pendingBitcoin - newOrder.amount
                                            newOrderCustomer.bitcoinBalance = newOrderCustomer.bitcoinBalance - newOrder.amount
                                            newOrderCustomer.euroBalance = newOrderCustomer.euroBalance + newOrder.totalPrice
                                            newOrderCustomer.profitLoss = newOrderCustomer.profitLoss + newOrder.totalPrice
                                            newOrder.profitLoss = newOrder.profitLoss + newOrder.totalPrice
                                            newOrder.setClosedDatetime()
                                            newOrder.status = 'closed'
                                            # open order update
                                            openBuyOrderCustomer.bitcoinBalance = openBuyOrderCustomer.bitcoinBalance + newOrder.amount
                                            openBuyOrderCustomer.euroBalance = openBuyOrderCustomer.euroBalance - newOrder.totalPrice
                                            openBuyOrderCustomer.pendingEuro = openBuyOrderCustomer.pendingEuro - (openBuyOrder.pricePerBitcoin * newOrder.amount)
                                            openBuyOrder.amount = openBuyOrder.amount - newOrder.amount
                                            openBuyOrder.totalPrice = openBuyOrder.amount * openBuyOrder.pricePerBitcoin
                                            openBuyOrderCustomer.profitLoss = openBuyOrderCustomer.profitLoss - openBuyOrder.totalPrice
                                            openBuyOrder.profitLoss = openBuyOrder.profitLoss - openBuyOrder.totalPrice
                                            openBuyOrder.setPartiallyClosedDatetime()
                                            # new order and related customer save
                                            newOrder.save()
                                            newOrderCustomer.save()
                                            # open order and related customer save
                                            openBuyOrder.save()
                                            openBuyOrderCustomer.save()
                                            isOrderMatched = True
                                        # else the new order btc amount is greater than the open order btc amount
                                        else:
                                            # a part of the new order can be matched with the open order: the open order is fully matched and can be flagged as closed, instead the new order remains open and needs to be updated
                                            # new order update
                                            newOrderCustomer.euroBalance = newOrderCustomer.euroBalance + (openBuyOrder.amount * newOrder.pricePerBitcoin)
                                            newOrderCustomer.bitcoinBalance = newOrderCustomer.bitcoinBalance - openBuyOrder.amount
                                            newOrderCustomer.pendingBitcoin = newOrderCustomer.pendingBitcoin - openBuyOrder.amount
                                            newOrder.amount = newOrder.amount - openBuyOrder.amount
                                            newOrder.totalPrice = newOrder.amount * newOrder.pricePerBitcoin
                                            newOrderCustomer.profitLoss = newOrderCustomer.profitLoss + newOrder.totalPrice
                                            newOrder.profitLoss = newOrder.profitLoss + newOrder.totalPrice
                                            newOrder.setPartiallyClosedDatetime()
                                            # open order close
                                            openBuyOrderCustomer.bitcoinBalance = openBuyOrderCustomer.bitcoinBalance + openBuyOrder.amount
                                            openBuyOrderCustomer.pendingEuro = openBuyOrderCustomer.pendingEuro - openBuyOrder.totalPrice
                                            openBuyOrder.pricePerBitcoin = newOrder.pricePerBitcoin
                                            openBuyOrder.totalPrice = openBuyOrder.amount * openBuyOrder.pricePerBitcoin
                                            openBuyOrderCustomer.euroBalance = openBuyOrderCustomer.euroBalance - openBuyOrder.totalPrice
                                            openBuyOrderCustomer.profitLoss = openBuyOrderCustomer.profitLoss - openBuyOrder.totalPrice
                                            openBuyOrder.profitLoss = openBuyOrder.profitLoss - openBuyOrder.totalPrice
                                            openBuyOrder.setClosedDatetime()
                                            openBuyOrder.status = 'closed'
                                            # new order and related customer save
                                            newOrder.save()
                                            newOrderCustomer.save()
                                            # open order and related customer save
                                            openBuyOrder.save()
                                            openBuyOrderCustomer.save()
                                            isOrderMatched = False
                        else:
                            # error message
                            print('User has not enough funds')
                            return redirect('newOrderPage')
                else:
                    # error message
                    print('Order price per Bitcoin must be greater than zero')
                    return redirect('newOrderPage')
            else:
                # error message
                print('Order amount must be greater than zero')
                return redirect('newOrderPage')
        return redirect('myOrdersPage')
    # user first visit on the page
    else:
        form = NewOrderForm
        return render(request, 'project/customerAct/new-order.html', {'form': form})


@customLoginRequired
def orderBookPage(request):
    currentUser = request.user
    buyOrderBook = Order.objects.filter(
        Q(status='open') & Q(type='buy') & ~Q(user=currentUser)
    ).order_by('openDatetime')
    sellOrderBook = Order.objects.filter(
        Q(status='open') & Q(type='sell') & ~Q(user=currentUser)
    ).order_by('openDatetime')
    context = {
        "buyOrderBook": buyOrderBook,
        "sellOrderBook": sellOrderBook,
    }
    return render(request, 'project/customerAct/order-book.html', context)


@customLoginRequired
def myOrdersPage(request):
    currentUser = request.user
    openOrders = Order.objects.filter(
        Q(status='open') & Q(user=currentUser)
    )
    closedOrders = Order.objects.filter(
        Q(status='closed') & Q(user=currentUser)
    )
    context = {
        "openOrders": openOrders,
        "closedOrders": closedOrders,
    }
    return render(request, 'project/customerAct/my-orders.html', context)


@customLoginRequired
def myOrdersJson(request):
    currentUser = request.user
    openOrders = Order.objects.filter(
        Q(status='open') & Q(user=currentUser)
    )
    closedOrders = Order.objects.filter(
        Q(status='closed') & Q(user=currentUser)
    )
    ordersJsonReport = [{"Open orders": ""}]
    for order in openOrders:
        ordersJsonReport.append(
            {
                "Type": order.type,
                "Bitcoin amount": order.amount,
                "Price per Bitcoin": order.pricePerBitcoin,
                "Total price": order.totalPrice,
                "Profit & Loss": order.profitLoss,
                "Opened on": order.openDatetime,
                "Partially closed on": order.PartiallyClosedDatetime,
            }
        )
    ordersJsonReport.append({"Closed orders": ""})
    for order in closedOrders:
        ordersJsonReport.append(
            {
                "Type": order.type,
                "Bitcoin amount": order.amount,
                "Price per Bitcoin": order.pricePerBitcoin,
                "Total price": order.totalPrice,
                "Profit & Loss": order.profitLoss,
                "Opened on": order.openDatetime,
                "Partially closed on": order.PartiallyClosedDatetime,
                "Closed on": order.closedDatetime,
            }
        )
    return JsonResponse(ordersJsonReport, safe=False, json_dumps_params={'indent': 3})


@customLoginRequired
def deleteOrderPage(request):
    user = request.user
    customer = Customer.objects.get(user=user)
    orders = Order.objects.filter(user=user, status='open')
    # user interacts with the page
    if request.method == "POST":
        # order handle
        orderId = request.POST.get('order')
        order = Order.objects.get(_id=ObjectId(orderId))
        # customer pending balance update
        if order.type == 'buy':
            orderEuro = order.totalPrice
            customer.pendingEuro = customer.pendingEuro - orderEuro
        else:
            orderBitcoin = order.amount
            customer.pendingBitcoin = customer.pendingBitcoin - orderBitcoin
        customer.save()
        # order deletion
        order.delete()
        return redirect('myOrdersPage')

    # user first visit on the page
    else:
        return render(request, 'project/customerAct/delete-order.html', {"orders": orders})
