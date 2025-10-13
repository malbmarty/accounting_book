from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views 


urlpatterns = [
    path('payment-calendar/', views.PaymentCalendarPageView.as_view(), name='payment_calendar'),
    path('dept/', views.DeptPageView.as_view(), name='dept'),
    path('balances/', views.BalancesPageView.as_view(), name='balances'),
]