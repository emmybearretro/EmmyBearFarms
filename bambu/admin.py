from django.contrib import admin
from django.utils.safestring import mark_safe

from bambu.models import ThreeMF, GCodeFile, Printer, ProductionQueue, PrinterState, Folder, \
    PredefinedCommand, PrinterCommand, PrintPlate


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


# Registering PredefinedCommand
@admin.register(PredefinedCommand)
class PredefinedCommandAdmin(admin.ModelAdmin):
    search_fields = ['name', 'command']  # Allows searching by name and command
    list_display = ('name', 'command', 'description', 'can_run_when_blocked')# Registering Folder

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name']

@admin.register(GCodeFile)
class GCodeAdmin(admin.ModelAdmin):
    # This displays the image in the list view
    list_display = ['image_tag','filename','print_time','nozzle','weight','md5','timestamp']
    list_display_links = ['image_tag','filename']
    list_filter = ['filename']
    fields = ['image_tag','print_time','folders','filename','nozzle','weight','md5','timestamp']
    readonly_fields = ['image_tag','timestamp','filename','md5','print_time']

    def image_tag(self, obj):
        if obj.image:
            return mark_safe('<img src="%s" width="100" height="100" />' % obj.image.url)
        else:
            return 'No Image'
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True

    pass


@admin.register(PrinterCommand)
class PrinterCommandAdmin(admin.ModelAdmin):
    list_display = ('printer', 'predefined_command', 'position', 'completed', 'completed_at')
    list_filter = ('printer', 'completed')
    search_fields = ['printer__name', 'predefined_command__name']
    readonly_fields = ['completed','completed_at', 'archived', 'archived_at']


    def queue_number(self, obj):
        # Assuming 'position' represents the queue order
        return obj.position + 1  # Adding 1 to make it human-readable (1-based index)

    queue_number.short_description = 'Queue Number'
    queue_number.admin_order_field = 'position'


    # def has_delete_permission(self, request, obj=None):
    #     return False  # Disables delete permission for this model in the admin

    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     if 'delete_selected' in actions:
    #         del actions['delete_selected']
    #     return actions


@admin.register(PrintPlate)
class PrintPlateAdmin(admin.ModelAdmin):
    pass