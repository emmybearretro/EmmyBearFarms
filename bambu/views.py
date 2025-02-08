import json

from django.db.models import Max
from django.http import Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
import redis
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from rest_framework.reverse import reverse_lazy

from bambu import models
from bambu.forms import FilteredProductionQueueForm, ThreeMFForm
from bambu.models import ProductionQueue, Printer, GCodeFile, PLATE_CHOICES, PrinterCommand, PredefinedCommand
from django.views.generic import ListView, DetailView, UpdateView



# Create your views here.
@require_http_methods(["GET", "POST"])
def upload_three_mf(request):
    if request.method == 'POST':
        form = ThreeMFForm(request.POST, request.FILES)
        if form.is_valid():
            three_mf = form.save(commit=False)  # Don't save to the database yet
            three_mf.save()  # This will call the custom save method of ThreeMF
            return redirect('file-list-view')  # Redirect to a success page or view
    else:
        form = ThreeMFForm()

    # Group by filename and get the latest one per group based on timestamp
    latest_files = GCodeFile.objects.values('filename').annotate(
        latest_timestamp=Max('timestamp')
    ).values('filename', 'latest_timestamp')

    # Now, fetch the actual GCodeFile objects that match these latest timestamps
    latest_gcode_files = GCodeFile.objects.filter(
        timestamp__in=[file['latest_timestamp'] for file in latest_files],
        filename__in=[file['filename'] for file in latest_files]
    )


    context = {
        'form': form,
        'gcode_files': latest_gcode_files,
    }
    return render(request, 'bambu/file_list_view.html', context)
def index(request):
    r = redis.Redis(host='localhost', port=6379, db=0)
    #show current printers and status
    keys = r.keys("*_cfgs")
    # let's try to fetch printer info for printers
    printers = []
    for key in keys:
        p = r.get(key).decode('utf-8')
        printer = json.loads(p)
        printers.append(printer)
        pass

    jobs = ProductionQueue.objects.all().order_by('-priority')

    context = {
        'printers': printers,
        'jobs': jobs,
    }
    r.close()
    return render(request=request, template_name='bambu/index.html',context=context)



    # def start_print(self,filename: str,
    #                     plate_number: int,
    #                     bed_leveling: bool = True,
    #                     flow_calibration: bool = False,
    #                     vibration_calibration: bool = False,
    #                     bed_type:str = "textured_plate",
    #                     use_ams: bool = True,
    #                     ams_mapping: list[int] = [0],
    #                     skip_objects: list[int] | None = None,
    #                     ) -> bool:
def send_print_job(request,pk):
    job = get_object_or_404(ProductionQueue, pk=pk)
    print(job.print_file)
    if not job.printer.blocked:
        print_info = {
            "serial_number": job.printer.serial_number,
            "filepath": job.print_file.gcode.path,
            "filename": job.print_file.filename,
            "plate_number": 1, #we always use 1 because we split all plates into their own files.
            "bed_leveling": job.bed_leveling,
            "bed_type": job.bed_type,
            "use_ams": job.use_ams,
            "ams_mapping": [],
            "skip_objects": []
        }
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.lpush(f"{job.printer.serial_number}", json.dumps(print_info))
        r.close()
        return redirect('index')
    else:
        pass
    return redirect('index')


class PrinterListView(ListView):
    model = Printer


def printer_history_view(request, serial_number):
    printer = get_object_or_404(Printer, serial_number=serial_number)

    # Fetch only items that have been sent to the printer
    history_queue = ProductionQueue.objects.filter(
        printer=printer,
        sent_to_printer=True
    ).order_by('-timestamp')  # Order by most recent first

    context = {
        'printer': printer,
        'history_queue': history_queue,
    }
    return render(request, 'bambu/printer_history.html', context)


def clone_queue_item(request, queue_id):
    queue_item = get_object_or_404(ProductionQueue, id=queue_id)

    # Create a new queue item by copying the original one
    new_queue_item = ProductionQueue.objects.create(
        print_file=queue_item.print_file,
        priority=queue_item.priority,
        duration=queue_item.duration,
        printer=queue_item.printer,
        sent_to_printer=False,  # Reset to not sent
        completed=False,  # Reset to not completed
    )

    # Optionally, copy any other fields you might have in ProductionQueue
    # new_queue_item.field_name = queue_item.field_name
    new_queue_item.save()

    #messages.success(request, f"Queue item '{new_queue_item.print_file.filename}' cloned successfully.")
    return redirect('printer_detail', serial_number=queue_item.printer.serial_number)


@require_http_methods(["POST"])
def printer_action(request, serial_number, action,):
    try:
        printer = get_object_or_404(Printer,serial_number=serial_number)
        data = None
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        predefined_command = None


        if action == 'start':
            # Code to start the printer
            result = {"status": "started"}
        elif action == 'pause':
            # Code to pause the printer
            result = {"status": "paused"}
        # ... handle other actions similarly
        elif action == 'stop_print':
            # Code for emergency stop
           predefined_command =  PredefinedCommand.objects.get(command=action)
        else:
            return JsonResponse({"error": "Invalid action"}, status=400)


        # Calculate the next position for the new command


        # Create the new PrinterCommand
        new_command = PrinterCommand.objects.create(
            printer=printer,
            predefined_command=predefined_command,
            position=0,
            completed=False,
            completed_at=None  # Not completed yet
        )



    except Printer.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Printer not found.'}, status=404)
    except PredefinedCommand.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Command not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


    # Return a JSON response indicating success
    return JsonResponse({
        'success': True,
        'message': 'Command added to queue.',
        'command_id': new_command.id
    }, status=201)



class PrinterDetailView(DetailView):
    model = Printer
    template_name = 'bambu/printer_detail.html'  # Adjust this to your template name
    context_object_name = 'printer'  # Optional, for naming the object in the template

    def get_object(self, queryset=None):
        # Check if queryset is provided, otherwise use the default
        if queryset is None:
            queryset = self.get_queryset()

        # Use the serial_number from the URL to query the Printer model
        queryset = queryset.filter(serial_number=self.kwargs.get('serial_number'))

        try:
            # Get object for display on the template using get() to raise an error if not found
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404("No Printer found with that serial number.")
        return obj

    def get_queryset(self):
        # Optionally, you can limit the queryset here if needed
        return Printer.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filter production queue to exclude items that have been sent to printer
        context['production_queue'] = ProductionQueue.objects.filter(
            printer=self.object,
            completed=False,
            sent_to_printer=False  # Add this filter
        ).order_by('priority', 'timestamp')

        # Command queue remains as is
        context['command_queue'] = PrinterCommand.objects.filter(
            printer=self.object,
            completed=False,
            archived=False
        ).order_by('position')

        return context
class ProductionQueueListView(ListView):
    model = ProductionQueue
    def get_queryset(self):
        qs = ProductionQueue.objects.order_by('-priority')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Return the modified context
        return context

class ProductionQueuepdateView(UpdateView):
    model = ProductionQueue
    success_url = reverse_lazy('print-queue')
    form_class = FilteredProductionQueueForm  # Use your custom form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()  # Pass the instance to the form
        return kwargs

class ProductionQueuePrintListView(ListView):
    model = ProductionQueue
    context_object_name = 'production_queue'
    template_name = 'bambu/productionqueue_print.html'
    def get_queryset(self):
        qs = ProductionQueue.objects.order_by('-priority')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add all printers to the context for selection in the template
        # Return the modified context
        return context

class PrinterProductionQueuePrintListView(ListView):
    model = ProductionQueue
    context_object_name = 'production_queue'
    template_name = 'bambu/productionqueue_print.html'
    def get_queryset(self):
        qs = ProductionQueue.objects.filter(printer__serial_number=self.kwargs.get('serial_number')).order_by('-priority')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["serial_number"] = self.kwargs.get('serial_number')
        # Add all printers to the context for selection in the template
        # Return the modified context
        return context


class FileListView(ListView):
    model = GCodeFile
    context_object_name = 'gcode_files'
    template_name = 'bambu/file_list_view.html'

    def get_queryset(self):
        all_files = GCodeFile.objects.all()

        # Dictionary to hold the latest revision of each file by filename
        latest_files = {}

        for file in all_files:
            if file.filename not in latest_files or file.revision > latest_files[file.filename].revision:
                latest_files[file.filename] = file

        # Return the values of the dictionary which are the latest GCodeFile objects
        return list(latest_files.values())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add all printers to the context for selection in the template
        context['printers'] = Printer.objects.all()
        return context


def add_to_production_queue(request, file_id):

    try:
        gcode_file = GCodeFile.objects.get(id=file_id)
    except GCodeFile.DoesNotExist:
        raise Http404("GCode file does not exist")

    printers = Printer.objects.all().filter(state__nozzle_diameter =  gcode_file.nozzle)  # Fetch all printers for selection
    #if none, we need an error message on screen that says NOPE
    if request.method == 'POST':
        # Create a new ProductionQueue with the data from the form
        printer_id = request.POST.get('printer')
        priority = int(request.POST.get('priority', 0))  # Default to 0 if not specified
        bed_leveling = 'bed_leveling' in request.POST
        use_ams = 'use_ams' in request.POST
        plate_type = request.POST.get('plate_type', 'textured_plate')

        new_queue = ProductionQueue.objects.create(
            print_file=gcode_file,
            sent_to_printer=False,
            completed=False,
            priority=priority,
            duration=gcode_file.print_time,
            printer=Printer.objects.get(id=printer_id) if printer_id else None,

        )

        # Redirect back to the list of files or another appropriate page
        return redirect(reverse('file-list-view'))  # Assuming 'file_list_view' is your URL name

    context = {
        'gcode_file': gcode_file,
        'printers': printers,
        'plate_choices': PLATE_CHOICES,
    }
    return render(request, 'bambu/add_to_queue.html', context)


def command_queue_view(request, serial_number):
    printer = get_object_or_404(Printer, serial_number=serial_number)

    # Fetch all commands for this printer that are not completed and not archived, ordered by position
    commands = PrinterCommand.objects.filter(
        printer=printer,
        completed=False,
        archived=False
    ).order_by('position')

    # Convert the queryset to a list of dictionaries for JSON response
    queue_data = [
        {
            'id': command.id,
            'position': command.position,
            'command': command.predefined_command.name,  # Assuming you want the command name, adjust as needed
        } for command in commands
    ]

    # If you want to render an HTML template:
    return render(request, 'bambu/queue_template.html', {'queue': queue_data, 'printer': printer})

    # For an API response, return JSON:
    #return JsonResponse({'queue': queue_data, 'printer_serial': serial_number})

def gcodefile_delete(request, pk):
    gcode_file = get_object_or_404(GCodeFile, pk=pk)
    if request.method == 'POST':
        gcode_file.delete()
        return redirect('file-list-view')
    return render(request, 'bambu/gcodefile_confirm_delete.html', {'object': gcode_file})


def send_command_view(request,serial_number, command_id):
    printer = get_object_or_404(Printer, serial_number=serial_number)
    command = get_object_or_404(PrinterCommand, id=command_id, printer=printer)

    # Here you would implement the logic to send the command to the printer
    # This could involve using Redis or another system to communicate with the printer

    # After sending, you might want to archive or mark the command as completed
    command.archive()  # Assuming you have such a method

    # Redirect back to the printer detail view
    return redirect('printer_detail', serial_number=printer.serial_number)


def add_to_command_queue(request, serial_number, queue_id):
    printer = get_object_or_404(Printer, serial_number=serial_number)
    queue_item = get_object_or_404(ProductionQueue, id=queue_id, printer=printer)

    if queue_item.completed:
        raise Http404("This queue item cannot be sent to the command queue.")

    # Assuming there's a predefined command for "Print" or similar action
    print_command = get_object_or_404(PredefinedCommand, name="Print")  # Adjust the name as per your setup

    # Create a new command in the command queue based on the production queue item
    last_position = \
    PrinterCommand.objects.filter(printer=printer, completed=False, archived=False).aggregate(models.Max('position'))[
        'position__max'] or 0
    PrinterCommand.objects.create(
        printer=printer,
        predefined_command=print_command,
        position=last_position + 1
    )

    # Optionally, mark the queue item as sent to printer or similar status update
    queue_item.sent_to_printer = True
    queue_item.save()

    # Redirect back to the printer detail view or another appropriate page
    return redirect('printer_detail', serial_number=serial_number)