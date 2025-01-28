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

class Printer(models.Model):
    name = models.CharField(max_length=255)
    ip = models.GenericIPAddressField()
    serial_number = models.CharField(max_length=255)
    access_code = models.CharField(max_length=255)
    nozzle_type = models.CharField(max_length=255)
    nozzle_diameter = models.FloatField(default=0.0)
    state = models.CharField(max_length=255)
    current_state = models.CharField(max_length=255)


    def __str__(self):
        return self.name

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

    def image_tag(self):
        iname = self.image.name
        return mark_safe('<img src="media/%s" width="150" height="150" />' % (self.image.name))

    image_tag.short_description = 'Image'

    def __str__(self):
        return str(f"{self.revision} - {self.filename}")

class ProductionQueue(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    print_file = models.ForeignKey(GCodeFile, null=False, blank=False,on_delete=models.CASCADE)
    sent_to_printer = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    priority = models.PositiveIntegerField(null=False, blank=False,default=0) #default low
    duration = models.FloatField(null=False, blank=False)


    def __str__(self):
        return str(f"{self.priority} - {self.print_file.filename}")

    def save(self, *args, **kwargs):
        self.duration = self.print_file.print_time
        super(ProductionQueue, self).save(*args, **kwargs)


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
                g.print_time = float(plate['prediction']) / 60.0
                g.md5 = md5
                g.save()

        except Exception as e:
            print(f"{e}")
            pass
        #super(ThreeMF, self).save(*args, **kwargs)

