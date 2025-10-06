from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views 

router = DefaultRouter()
router.register(r'oper-acc-records', views.OperationalAccountingViewSet)
router.register(r'planning-records', views.PlanningViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    # path('directory/', views.AnalyticsDirPageView.as_view(), name='analytics_dir'),
]