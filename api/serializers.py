from rest_framework import serializers
from bambu.models import Printer, PrinterState


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
        instance.ip_address = validated_data.get('ip_address', instance.ip_address)
        #instance.nozzle_diameter = validated_data.get('nozzle_diameter', instance.nozzle_diameter)
        #instance.nozzle_type = validated_data.get('nozzle_type', instance.nozzle_type)
        instance.save()
        return instance

class PrinterStateSerializer(serializers.ModelSerializer):
        class Meta:
            model = PrinterState
            fields = '__all__'

        def update(self, instance, validated_data):
            # Update all fields of PrinterState
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance

        def create(self, validated_data):
            # If you need to create a new PrinterState instance
            return PrinterState.objects.create(**validated_data)