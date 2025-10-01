from django.shortcuts import render
from rest_framework import viewsets
from django.views.generic import TemplateView

from .serializers import (
    ProjectSerializer, ParticipantSerializer
)
from .models import (
    Project, Participant
)

# HTML Views
class AnalyticsDirPageView(TemplateView):
    template_name = 'analytics_dir/analytics_dir.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем все данные из базы и передаем в шаблон
        context['projects'] = Project.objects.all()
        context['participants'] = Participant.objects.all()

        return context


# API 
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer