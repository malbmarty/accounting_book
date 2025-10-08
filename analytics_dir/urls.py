from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views 

router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet)
router.register(r'participants', views.ParticipantViewSet)
router.register(r'payment-systems', views.PaymentSystemViewSet)
router.register(r'counterparties', views.CounterpartyViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'frequencies', views.FrequencyViewSet)
router.register(r'flow-types', views.FlowTypeViewSet)
router.register(r'variabilities', views.VariabilityViewSet)
router.register(r'items', views.ItemViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('directory/', views.AnalyticsDirPageView.as_view(), name='analytics_dir'),
]