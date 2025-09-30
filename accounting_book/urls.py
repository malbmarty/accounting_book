from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('payroll/', include('payroll.urls')),
    path('analytics-dir/', include('analytics_dir.urls'))
]


