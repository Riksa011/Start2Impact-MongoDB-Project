# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # homepage
    path('', views.homePage, name='homePage'),
    # customer authentication
    path('login/', views.loginPage, name='loginPage'),
    path('logout/', views.logoutPage, name='logoutPage'),
    path('register/', views.registerPage, name='registerPage'),
    # customer actions
    path('profile/', views.profilePage, name='profilePage'),
    path('dashboard/', views.dashboardPage, name='dashboardPage'),
    path('new-order/', views.newOrderPage, name='newOrderPage'),
    path('delete-order/', views.deleteOrderPage, name='deleteOrderPage'),
    path('order-book/', views.orderBookPage, name='orderBookPage'),
    path('my-orders/', views.myOrdersPage, name='myOrdersPage'),
    path('my-orders-json/', views.myOrdersJson, name='myOrdersJson'),
]
