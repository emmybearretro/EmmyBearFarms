import json

from django.shortcuts import render
import redis

from bambu.models import ProductionQueue, Printer

from django.views.generic import ListView, DetailView


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


class PrinterListView(ListView):
    model = Printer


class PrinterDetailView(DetailView):
    model = Printer


class ProductionQueueListView(ListView):
    model = ProductionQueue