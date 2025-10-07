from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views 

router = DefaultRouter()
router.register(r'oper-acc-records', views.OperAccountingViewSet)
router.register(r'planning-records', views.PlanningViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('oper-accounting/', views.OperAccountingPageView.as_view(), name='oper_acc'),
    path('edit-oper-accounting/<int:pk>/', views.EditOperAccountingPageView.as_view(), name='edit_oper_acc'),
    path('planning/', views.PlanningPageView.as_view(), name='planning'),
    path('edit-planning/<int:pk>/', views.EditPlanningPageView.as_view(), name='edit_planning'),
    # path('directory/', views.AnalyticsDirPageView.as_view(), name='analytics_dir'),
]