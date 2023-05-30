# forms.py
from django import forms
from .models import Order
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# form for new user registration
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# form for new order creation
class NewOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['type', 'amount', 'pricePerBitcoin']
