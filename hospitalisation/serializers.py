from rest_framework import serializers
from .models import Chambre, Lit, Admission

class ChambreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chambre
        fields = '__all__'
        read_only_fields = ('created_at',)

class LitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lit
        fields = '__all__'

class AdmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admission
        fields = '__all__'
        read_only_fields = ('date_admission',)