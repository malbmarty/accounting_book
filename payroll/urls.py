from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views 

router = DefaultRouter()
router.register(r'positions', views.PositionViewSet)
router.register(r'departments', views.DepartmentViewSet)
router.register(r'statuses', views.StatusViewSet)
router.register(r'employee-types', views.EmployeeTypeViewSet)
router.register(r'payment-types', views.PaymentTypeViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]