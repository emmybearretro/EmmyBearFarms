from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.serializers import PrinterSerializer, PrinterStateSerializer
from bambu.models import Printer, ThreeMF


# Create your views here.
class PrinterListView(APIView):
    def get(self, request, format=None):
        printers = Printer.objects.all()
        serializer = PrinterSerializer(printers, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):

        serializer = PrinterSerializer(data=request.data)
        if serializer.is_valid():
            i = 1
            sn = serializer.validated_data['serial_number']
            try:
                obj = Printer.objects.get(serial_number=sn)
            except Printer.DoesNotExist:
                serializer.save()
                return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PrinterDetailView(APIView):

    def get_object(self, serial_number):
        try:
            return Printer.objects.get(serial_number=serial_number)
        except Printer.DoesNotExist:
            raise Http404

    def patch(self, request, serial_number, format=None):
        item = self.get_object(serial_number)
        if not item:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Only update fields that are sent in the request
        serializer = PrinterSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, serial_number, format=None):
        printer = self.get_object(serial_number)
        serializer = PrinterSerializer(printer)
        return Response(serializer.data)

    def put(self, request, serial_number):
        printer = self.get_object(serial_number)
        serializer = PrinterSerializer(printer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PrinterStatusView(APIView):
    def get_object(self, serial_number):
        try:
            p:Printer = Printer.objects.get(serial_number=serial_number)
            return p.state
        except Printer.DoesNotExist:
            raise Http404

    def get(self, request, serial_number, format=None):
        state = self.get_object(serial_number)
        serializer = PrinterStateSerializer(state)
        return Response(serializer.data)

    def patch(self, request, serial_number, format=None):
        state = self.get_object(serial_number)
        serializer = PrinterStateSerializer(state,data=request.data, partial=True)
        print(type(request.data), request.data)
        if serializer.is_valid():
            i = 1

            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileUploadView(APIView):
    def post(self, request, format=None):
        try:
            if 'file' not in request.FILES:
                return Response({
                    'error': 'No file provided'
                }, status=status.HTTP_400_BAD_REQUEST)

            uploaded_file = request.FILES['file']

            # Validate file extension
            if not uploaded_file.name.lower().endswith('.3mf'):
                return Response({
                    'error': 'Invalid file format. Only .3mf files are accepted'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create ThreeMF instance
            three_mf = ThreeMF()
            three_mf.file.save(uploaded_file.name, uploaded_file)

            # The ThreeMF model's save() method will handle the extraction and
            # creation of GCodeFile instances

            return Response({
                'message': 'File processed successfully',
                'filename': uploaded_file.name
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)