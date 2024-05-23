from rest_framework import generics
from core.models import Sector, Skill
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from sector_assessment import serializers


class SectorListView(generics.ListAPIView):
    queryset = Sector.objects.all()
    serializer_class = serializers.SectorListSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class SkillListView(generics.ListAPIView):
    queryset = Skill.objects.all()
    serializer_class = serializers.SkillListSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
