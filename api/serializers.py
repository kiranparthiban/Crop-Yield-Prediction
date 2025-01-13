from rest_framework import serializers
from .models import MarineSpecies

class MarineSpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarineSpecies
        fields = '__all__'
