from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views 

router = DefaultRouter()
router.register(r'positions', views.PositionViewSet)
router.register(r'departments', views.DepartmentViewSet)
router.register(r'statuses', views.StatusViewSet)
router.register(r'employee-types', views.EmployeeTypeViewSet)
router.register(r'payment-types', views.PaymentTypeViewSet)
router.register(r'employees', views.EmployeeViewSet)
router.register(r'accruals', views.AccrualViewSet)
router.register(r'payouts', views.PayoutViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
    # новый API для сводной таблицы
    path('directory/', views.PayrollDirPageView.as_view(), name='payroll_dir'),
    path('all-employees/', views.EmployeesPageView.as_view(), name='employees'),
    path('all-accruals/', views.AccrualsPageView.as_view(), name='accruals'),
    path('edit-accrual/<int:pk>/', views.EditAccrualPageView.as_view(), name='edit_accrual'),
    path('all-payouts/', views.PayoutsPageView.as_view(), name='payouts'),
    path('edit-payout/<int:pk>/', views.EditPayoutPageView.as_view(), name='edit_payout'),
    path('summary/', views.SummaryPageView.as_view(), name='summary'),
]