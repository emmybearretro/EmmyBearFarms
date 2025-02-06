import hashlib
from fileinput import filename
from io import BytesIO
from django.core.files import File
from django.db import models
from zipfile import ZipFile
import xmltodict
from django.db.models import FileField
from django.db.models.fields.files import FieldFile
from django.utils.safestring import mark_safe
from django.db.models import Max

from bambulabs_api.states_info import PrintStatus

#some helper stuff

# Create your models here.

def metatoplate(metadata):
    pconfig = {}
    for key in metadata:
        print(key)
        k = key['@key']
        v = key['@value']
        pconfig[k] = v
    return pconfig

class PrinterState(models.Model):
    ams_rfid_status = models.IntegerField(default=0)
    ams_status = models.IntegerField(default=0)
    bed_temperature = models.FloatField(default=0.0)
    big_fan1_speed = models.CharField(max_length=10, default="0")
    big_fan2_speed = models.CharField(max_length=10, default="0")
    calibration_version = models.IntegerField(default=0)
    chamber_temperature = models.FloatField(default=0.0)
    cooling_fan_speed = models.CharField(max_length=10, default="0")
    current_layer_number = models.IntegerField(default=0)
    current_stage = models.IntegerField(default=0)
    #current_state = models.CharField(max_length=50, default="DEFAULT")
    fan_gear_status = models.IntegerField(default=0)
    filament_backup = models.JSONField(default=list)  # This stores JSON data
    file_name = models.CharField(max_length=255, blank=True)
    force_upgrade_status = models.BooleanField(default=False)
    gcode_file = models.CharField(max_length=255, blank=True)
    gcode_file_prepare_percentage = models.IntegerField(default=0)
    gcode_state = models.CharField(max_length=20, default="default")
    hardware_switch_state = models.IntegerField(default=0)
    heatbreak_fan_speed = models.CharField(max_length=10, default="0")
    home_flag = models.IntegerField(default=0)
    lifecycle = models.CharField(max_length=20, default="default")
    light_state = models.CharField(max_length=10, default="on")
    nozzle_diameter = models.FloatField(default=0.0)
    nozzle_temperature = models.FloatField(default=0.0)
    nozzle_type = models.CharField(max_length=20, default="default")
    percentage = models.IntegerField(default=0)
    print_error = models.IntegerField(default=0)
    print_line_number = models.CharField(max_length=20, default="0")
    print_speed = models.IntegerField(default=0)
    print_speed_level = models.IntegerField(default=0)
    print_stage = models.CharField(max_length=50, default="DEFAULT")
    print_sub_stage = models.IntegerField(default=0)
    print_type = models.CharField(max_length=20, default="default")
    printer_state = models.CharField(max_length=20, default="DEFAULT")
    production_state = models.CharField(max_length=20, default="default")
    profile_id = models.CharField(max_length=20, default="0")
    project_id = models.CharField(max_length=20, default="0")
    queue_estimated_time = models.IntegerField(default=0)
    queue_number = models.IntegerField(default=0)
    queue_status = models.IntegerField(default=0)
    queue_total = models.IntegerField(default=0)
    ready = models.BooleanField(default=False)
    remaining_print_time = models.IntegerField(default=0)
    sdcard_status = models.BooleanField(default=False)
    skipped_objects = models.JSONField(default=list)  # This stores JSON data
    subtask_id = models.CharField(max_length=20, default="0")
    subtask_name = models.CharField(max_length=255, default="")
    task_id = models.CharField(max_length=20, default="0")
    time_remaining = models.IntegerField(default=0)
    total_layer_number = models.IntegerField(default=0)
    wifi_signal = models.CharField(max_length=20, default="")

    @property
    def current_state(self):
        # Assuming 'current_stage' somehow correlates with 'current_state'
        # Here's a basic mapping. You'll need to adjust this based on your actual logic.
        for status in PrintStatus:
            if status.value == self.current_stage:
                return status.name
        return PrintStatus.UNKNOWN

    def __str__(self):
        return f"{self.current_state}"

    def save(self, *args, **kwargs):
        if self.current_state == "PrintStatus.PRINTING" or self.gcode_state == "RUNNING":
            self.printer.blocked = True
        super().save(*args, **kwargs)

class GcodeState(models.TextChoices):
    IDLE = 'IDLE', 'Idle'
    PREPARE = 'PREPARE', 'Preparing'
    RUNNING = 'RUNNING', 'Running'
    PAUSE = 'PAUSE', 'Paused'
    FINISH = 'FINISH', 'Finished'
    FAILED = 'FAILED', 'Failed'
    UNKNOWN = 'UNKNOWN', 'Unknown'


class Printer(models.Model):
    name = models.CharField(max_length=255)
    access_code = models.CharField(max_length=20)
    ip_address = models.GenericIPAddressField()
    serial_number = models.CharField(max_length=20)
    state = models.OneToOneField(PrinterState, on_delete=models.CASCADE, related_name='printer',null=True,blank=True)
    blocked = models.BooleanField(default=False,blank=True)
    connected = models.BooleanField(default=False,blank=True)

    @property
    def has_error(self):
        pass

    def __str__(self):
        return f"Printer: {self.serial_number}"

    # If you want to ensure the state is always updated when updating the printer:
    def save(self, *args, **kwargs):
        # If this is a new instance, create a new state
        if not self.pk:
            new_state = PrinterState.objects.create()
            self.state = new_state
        # If this is an existing instance, ensure state exists or create one if it doesn't
        elif not self.state:
            self.state = PrinterState.objects.create()

        super().save(*args, **kwargs)


class GCodeFile(models.Model):
    revision = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    gcode = models.FileField(upload_to='gcode', null=False, blank=False)
    md5 = models.CharField(max_length=64, null=True, blank=True)
    filename = models.CharField(max_length=4096, null=True, blank=True)
    image = models.ImageField(upload_to='images', null=False, blank=False)
    nozzle = models.CharField(max_length=64, null=False, blank=False)
    weight = models.CharField(max_length=64, null=False, blank=False)
    print_time = models.FloatField(null=False, blank=False)

    @property
    def is_latest(self):
        latest = GCodeFile.objects.filter(filename=self.filename).aggregate(models.Max('revision'))['revision__max']
        return self.revision == latest


    def image_tag(self):
        iname = self.image.name
        return mark_safe('<img src="media/%s" width="150" height="150" />' % (self.image.name))

    image_tag.short_description = 'Image'

    def __str__(self):
        return str(
            "BOOP" +
            f" - {self.filename}")

PLATE_CHOICES = [
    ("textured_plate", "Textured plate"),
    ("cool_plate", "Cool Plate / PLA Plate"),
    ("hot_plate", "Smooth PEI Plate / High Temp Plate"),
    ("eng_plate", "Engineering Plate"),
]


class ProductionQueue(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    print_file = models.ForeignKey(GCodeFile, null=False, blank=False,on_delete=models.CASCADE)
    sent_to_printer = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    priority = models.PositiveIntegerField(null=False, blank=False,default=0) #default low
    duration = models.FloatField(null=False, blank=False,default=0.0)
    printer = models.ForeignKey(Printer, null=True, blank=True, on_delete=models.CASCADE)
    bed_leveling = models.BooleanField(default=True, null=False, blank=False)
    use_ams = models.BooleanField(default=False, null=False, blank=False)
    plate_type = models.CharField(
        max_length=20,  # Adjust based on the longest option
        choices=PLATE_CHOICES,
        default="textured_plate",  # Set a default if needed
    )
    def __str__(self):
        return str(f"{self.priority} - {self.print_file.filename}")

    def save(self, *args, **kwargs):
        self.duration = self.print_file.print_time
        super(ProductionQueue, self).save(*args, **kwargs)

    @property
    def print_time(self):
        seconds = self.duration
        days = int(seconds // (24 * 3600))
        seconds = seconds % (24 * 3600)
        hours = int(seconds // 3600)
        seconds = seconds % 3600
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{days}d {hours}h {minutes}m{seconds}s"

    @property
    def duration_formatted(self):
        seconds = self.duration
        days = int(seconds // (24 * 3600))
        seconds = seconds % (24 * 3600)
        hours = int(seconds // 3600)
        seconds = seconds % 3600
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return {
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds
        }


class PrinterQueue(models.Model):
    # Link to the printer
    printer = models.ForeignKey(
        Printer,
        on_delete=models.CASCADE,
        related_name='queues'
    )

    # Link to the production queue item
    production_queue_item = models.ForeignKey(
        ProductionQueue,
        on_delete=models.CASCADE,
        related_name='printer_queues'
    )

    # Queue position, to determine order in which items are processed
    position = models.PositiveIntegerField(default=0)

    # Timestamp when this item was added to the printer's queue
    added_to_queue = models.DateTimeField(auto_now_add=True)

    # Status of this item in the queue (e.g., 'queued', 'printing', 'completed', 'cancelled')
    status = models.CharField(
        max_length=20,
        choices=[
            ('queued', 'Queued'),
            ('printing', 'Printing'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='queued'
    )

    # If you want to add more specific data relevant to each printer's queue:
    # estimated_start_time = models.DateTimeField(null=True, blank=True)
    # estimated_completion_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Queue item for {self.printer.name}: {self.production_queue_item.print_file.filename} - Position {self.position}"

    class Meta:
        ordering = ['printer', 'position']  # Order by printer and then by position in the queue
        unique_together = (
        'printer', 'production_queue_item')  # Ensure no duplicate entries for same printer and queue item

    @property
    def duration(self):
        return self.production_queue_item.duration_formatted

    @property
    def priority(self):
        return self.production_queue_item.priority

    def update_status(self, new_status):
        if new_status in dict(self._meta.get_field('status').choices).keys():
            self.status = new_status
            self.save()
        else:
            raise ValueError(f"Invalid status: {new_status}")


class ThreeMF(models.Model):
    file = models.FileField(upload_to='threemf')
    #p = models.ForeignKey(PrintableFile, related_name='threemf',on_delete=models.CASCADE)


    def save(self, *args, **kwargs):
        i = 1
        file_content = self.file.read()
        try:
            plates = []
            zip_file = ZipFile(BytesIO(file_content))
            config_text = zip_file.read("Metadata/slice_info.config").decode("utf-8")
            config = xmltodict.parse(config_text)
            if(isinstance( config['config']['plate'], list)):
                print("it was a list")
                for plate in config['config']['plate']:
                    pconfig = metatoplate(plate['metadata'])
                    plates.append(pconfig)
            else:
                pconfig = metatoplate(config['config']['plate']['metadata'])
                plates.append(pconfig)
            i = 1
            for plate in plates:
                i = 1
                gcode = zip_file.read(f"Metadata/plate_{plate['index']}.gcode")
                md5 = hashlib.md5(gcode).hexdigest().upper()
                md5_file = zip_file.read(f"Metadata/plate_{plate['index']}.gcode.md5").decode("utf-8")
                png = zip_file.read(f"Metadata/plate_{plate['index']}.png")
                if (md5 != md5_file):
                    print("MD5 mismatch")
                g = GCodeFile()
                g.filename = f"{self.file.name}_plate{plate['index']}.gcode"
                try:
                    g.revision = GCodeFile.objects.filter(filename=g.filename).latest('revision').revision + 1
                except GCodeFile.DoesNotExist:
                    g.revision = 1
                g.gcode.save(md5, File(BytesIO(gcode)), save=False)
                g.image.save(f"{md5}.png", File(BytesIO(png)), save=False)
                g.nozzle = plate['nozzle_diameters']
                g.weight = plate['weight']
                g.print_time = float(plate['prediction'])
                g.md5 = md5
                g.save()

        except Exception as e:
            print(f"{e}")
            pass
        #super(ThreeMF, self).save(*args, **kwargs)

