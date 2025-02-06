import json

from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
import redis
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from rest_framework.reverse import reverse_lazy

from bambu import models
from bambu.forms import FilteredProductionQueueForm, ThreeMFForm
from bambu.models import ProductionQueue, Printer, GCodeFile, PLATE_CHOICES
from django.views.generic import ListView, DetailView, UpdateView



# Create your views here.
@require_http_methods(["GET", "POST"])
def upload_three_mf(request):
    if request.method == 'POST':
        form = ThreeMFForm(request.POST, request.FILES)
        if form.is_valid():
            three_mf = form.save(commit=False)  # Don't save to the database yet
            three_mf.save()  # This will call the custom save method of ThreeMF
            return redirect('upload_three_mf')  # Redirect to a success page or view
    else:
        form = ThreeMFForm()

    # Assuming you have a list view or similar for your GCode files
    all_files = GCodeFile.objects.all() # Adjust this query as needed
    # Dictionary to hold the latest revision of each file by filename
    latest_files = {}

    for file in all_files:
        if file.filename not in latest_files or file.revision > latest_files[file.filename].revision:
            latest_files[file.filename] = file
    context = {
        'form': form,
        'gcode_files': latest_files.values(),
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
            bed_leveling=bed_leveling,
            use_ams=use_ams,
            plate_type=plate_type,
        )

        # Redirect back to the list of files or another appropriate page
        return redirect(reverse('upload_three_mf'))  # Assuming 'file_list_view' is your URL name

    context = {
        'gcode_file': gcode_file,
        'printers': printers,
        'plate_choices': PLATE_CHOICES,
    }
    return render(request, 'bambu/add_to_queue.html', context)