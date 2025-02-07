# forms.py
from django import forms
from django.utils.safestring import mark_safe

from .models import GCodeFile, ProductionQueue, Printer, Folder, PrintSettings, PLATE_CHOICES

from .models import ThreeMF


class ThreeMFForm(forms.ModelForm):
    class Meta:
        model = ThreeMF
        fields = ['file']

    # Customizing the file field widget for better user experience
    file = forms.FileField(
        widget=forms.FileInput(attrs={ 'accept': '.3mf'})
    )

    def __init__(self, *args, **kwargs):
        super(ThreeMFForm, self).__init__(*args, **kwargs)
        # Adding a custom label or help text if needed
        self.fields['file'].label = "Upload 3MF File"
        self.fields['file'].help_text = "Please select a .3mf file to upload."

class FilteredProductionQueueForm(forms.ModelForm):
    class Meta:
        model = ProductionQueue
        fields = ['printer','priority', 'print_file']  # Include print_file for selection

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')

        # Filter GCodeFile queryset by the filename if an instance exists
        if instance and instance.print_file:
            filename = instance.print_file.filename
            self.fields['print_file'].queryset = GCodeFile.objects.filter(filename=filename).order_by('-timestamp')

        # Filter printers based on nozzle size if a print_file is selected or exists
        if instance and instance.print_file:
            gcode_file = instance.print_file
        elif 'print_file' in self.data:
            try:
                gcode_file = GCodeFile.objects.get(id=self.data['print_file'])
            except (ValueError, GCodeFile.DoesNotExist):
                gcode_file = None
        else:
            gcode_file = None

        if gcode_file:
            # Assuming nozzle size is stored as a string in the GCodeFile model (e.g., '0.4')
            nozzle_size = gcode_file.nozzle
            # Filter printers that match this nozzle size. Here, assuming nozzle is exact match
            self.fields['printer'].queryset = Printer.objects.filter(state__nozzle_diameter=nozzle_size)
        else:
            # If no GCodeFile is specified, you might want to show all printers or none
            self.fields['printer'].queryset = Printer.objects.none()


class ImagePreviewWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        if value and hasattr(value, 'url'):
            return mark_safe(f'<img src="{value.url}" style="max-width: 200px; max-height: 200px;" />')
        return ''
