"""crypto_trader URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from management_app import views

urlpatterns = [
    path('collector/', views.collector, name='collector'),
    path('crypto_trader_bot/', views.crypto_trader_bot, name='crypto_trader_bot'),
    path('orders_history/', views.orders_history, name='orders_history'),
    path('trade/', views.trade, name='trade'),
    path('pairs/', views.pairs, name='pairs'),
    path('candles/', views.candles, name='candles'),
    path('balance/', views.balance, name='balance'),
]


