from django.shortcuts import render
from rest_framework import viewsets

from .serializers import (
    ProjectSerializer, ParticipantSerializer
)
from .models import (
    Project, Participant
)

# API 
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer