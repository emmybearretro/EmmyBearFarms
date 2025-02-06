from django.urls import path

from . import views
from . import forms

urlpatterns = [
    path('',views.index,name='index'),
    path('printers',views.PrinterListView.as_view(),name='printer_list'),
    path('printers/<int:pk>',views.PrinterDetailView.as_view(),name='printer_detail'),

    path('queue',views.ProductionQueueListView.as_view(),name='production_queue'),
    path('printqueue', views.ProductionQueuePrintListView.as_view(), name='production_queue_print'),
    path('printqueue/print/<int:pk>', views.send_print_job, name='send_to_production'),

    path('queue/update/<int:pk>',views.ProductionQueuepdateView.as_view(),name='production_queue_update'),
    #path('about',views.about,name='about'),
]