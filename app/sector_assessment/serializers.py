from core.models import Sector, Skill

from rest_framework import serializers


class SectorListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sector
        fields = ['name']


class SkillListSerializer(serializers.ModelSerializer):
    sectors = SectorListSerializer(many=True, read_only=True)

    class Meta:
        model = Skill
        fields = ['name', 'sectors']
