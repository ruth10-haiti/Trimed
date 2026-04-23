from rest_framework import serializers
from .models import TypeSalle, SalleMedicale, ReservationSalle

class TypeSalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeSalle
        fields = '__all__'

class SalleMedicaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalleMedicale
        fields = '__all__'
        read_only_fields = ('created_at',)

class ReservationSalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationSalle
        fields = '__all__'