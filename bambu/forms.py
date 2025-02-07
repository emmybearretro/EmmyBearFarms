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

class GCodeFileWithSettingsForm(forms.ModelForm):
    class Meta:
        model = GCodeFile
        fields = ['displayname', 'filename', 'gcode', 'image', 'nozzle', 'weight', 'print_time', 'folders']

    gcode = forms.FileField(
        widget=forms.HiddenInput(attrs={'readonly': 'readonly'}),
        required=False  # Since it's hidden and disabled, it shouldn't be required
    )
    filename = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        required=False  # Since it's disabled, make it not required
    )
    image = forms.ImageField(
        widget=ImagePreviewWidget,
        required=False  # If editing, we don't want to force re-upload
    )
    nozzle = forms.FloatField(
        widget=forms.NumberInput(attrs={
            'step': '0.1',  # Adjust the step value as needed
            'min': '0.1',   # Set a minimum value if applicable
            'max': '1.0'    # Set a maximum value if applicable
        }),
        required=True  # Assuming nozzle size is always required
    )

    # Include fields for PrintSettings directly in the form
    bed_leveling = forms.BooleanField(required=False, initial=True)
    flow_calibration = forms.BooleanField(required=False, initial=True)
    vibration_calibration = forms.BooleanField(required=False, initial=True)
    plate_type = forms.ChoiceField(choices=PLATE_CHOICES)
    use_ams = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['folders'].queryset = Folder.objects.all()
        instance = kwargs.get('instance')
        if instance and instance.gcode:
            # Add a way to display the current file name since the input is hidden
            self.initial['gcode'] = instance.gcode.name
            self.initial['filename'] = instance.filename
            self.initial['image'] = instance.image
            self.initial['nozzle'] = instance.nozzle

    def save(self, commit=True):
        gcode_file = super().save(commit=False)
        if commit:
            if not gcode_file.print_settings_id:  # If there's no existing PrintSettings
                settings = PrintSettings.objects.create(
                    bed_leveling=self.cleaned_data['bed_leveling'],
                    flow_calibration=self.cleaned_data['flow_calibration'],
                    vibration_calibration=self.cleaned_data['vibration_calibration'],
                    plate_type=self.cleaned_data['plate_type'],
                    use_ams=self.cleaned_data['use_ams']
                )
                gcode_file.print_settings = settings
            else:  # Update existing PrintSettings
                settings = gcode_file.print_settings
                settings.bed_leveling = self.cleaned_data['bed_leveling']
                settings.flow_calibration = self.cleaned_data['flow_calibration']
                settings.vibration_calibration = self.cleaned_data['vibration_calibration']
                settings.plate_type = self.cleaned_data['plate_type']
                settings.use_ams = self.cleaned_data['use_ams']
                settings.save()

            gcode_file.save()
        return gcode_file










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
            self.fields['print_file'].queryset = GCodeFile.objects.filter(filename=filename).order_by('-timestamp')