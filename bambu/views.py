import json

from django.shortcuts import render, get_object_or_404, redirect
import redis
from rest_framework.reverse import reverse_lazy

from bambu.forms import FilteredProductionQueueForm
from bambu.models import ProductionQueue, Printer, GCodeFile
from django.views.generic import ListView, DetailView, UpdateView



# Create your views here.
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

def send_print_job(request,pk):
    job = get_object_or_404(ProductionQueue, pk=pk)
    print(job.print_file)
    print_info = {
        "serial_number": job.printer.serial_number,
        "filepath": job.print_file.gcode.path,
        "filename": job.print_file.filename
    }
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.lpush("print", json.dumps(print_info))
    r.close()
    return redirect('index')

class PrinterListView(ListView):
    model = Printer


class PrinterDetailView(DetailView):
    model = Printer


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
    success_url = reverse_lazy('production_queue')
    form_class = FilteredProductionQueueForm  # Use your custom form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()  # Pass the instance to the form
        return kwargs

class ProductionQueuePrintListView(ListView):
    model = ProductionQueue
    template_name = 'bambu/productionqueue_print.html'
    def get_queryset(self):
        qs = ProductionQueue.objects.order_by('-priority')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Return the modified context
        return context

