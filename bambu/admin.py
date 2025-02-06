from django.contrib import admin
from django.utils.safestring import mark_safe

from bambu.models import ThreeMF, GCodeFile, Printer, ProductionQueue, PrinterState, PrinterQueue


# Register your models here.
@admin.register(ThreeMF)
class ThreeMFAdmin(admin.ModelAdmin):
    pass

@admin.register(Printer)
class PrinterAdmin(admin.ModelAdmin):
    pass

@admin.register(PrinterState)
class PrinterStateAdmin(admin.ModelAdmin):
    pass

@admin.register(ProductionQueue)
class ProductionQueueAdmin(admin.ModelAdmin):
    list_display = ('priority','print_file','timestamp')
    ordering = ('-priority','timestamp',)
    readonly_fields = ['print_time', 'timestamp', 'sent_to_printer', 'duration']
    pass

@admin.register(PrinterQueue)
class PrinterQueueAdmin(admin.ModelAdmin):
    pass

@admin.register(GCodeFile)
class GCodeAdmin(admin.ModelAdmin):
    # This displays the image in the list view
    list_display = ['image_tag','filename','revision','print_time','nozzle','weight','md5','timestamp']
    list_display_links = ['image_tag','filename']
    list_filter = ['filename','revision']
    fields = ['image_tag','print_time','filename','nozzle','weight','revision','md5','timestamp']
    readonly_fields = ['image_tag','timestamp','filename','revision','md5','print_time']

    def image_tag(self, obj):
        if obj.image:
            return mark_safe('<img src="%s" width="100" height="100" />' % obj.image.url)
        else:
            return 'No Image'
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True

    pass