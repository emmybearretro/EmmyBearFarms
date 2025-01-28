# forms.py
from django import forms
from .models import GCodeFile, ProductionQueue


class FilteredProductionQueueForm(forms.ModelForm):
    class Meta:
        model = ProductionQueue
        fields = ['printer', 'print_file']  # Include print_file for selection

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            # Filter GCodeFile queryset by the filename of the current print_file
            filename = instance.print_file.filename
            self.fields['print_file'].queryset = GCodeFile.objects.filter(filename=filename).order_by('-revision')

class SendPrintJobForm(forms.ModelForm):
    class Meta:
        model = ProductionQueue
        fields = '__all__'  # Or specify your fields

    def __init__(self, *args, **kwargs):
        super(SendPrintJobForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['disabled'] = True
            field.required = False  # Disable validation since the field is read-only

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            # Filter GCodeFile queryset by the filename of the current print_file
            filename = instance.print_file.filename
            self.fields['print_file'].queryset = GCodeFile.objects.filter(filename=filename).order_by('-revision')