from rest_framework import serializers
from bambu.models import Printer

class PrinterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Printer
        fields = '__all__'

    def create(self, validated_data):
        return Printer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.serial_number = validated_data.get('serial_number', instance.serial_number)
        instance.access_code = validated_data.get('access_code', instance.access_code)
        instance.ip = validated_data.get('ip', instance.ip)
        instance.nozzle_diameter = validated_data.get('nozzle_diameter', instance.nozzle_diameter)
        instance.nozzle_type = validated_data.get('nozzle_type', instance.nozzle_type)
        instance.save()
        return instance