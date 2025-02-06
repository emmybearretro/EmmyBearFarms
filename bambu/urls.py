from django.urls import path

from . import views
from . import forms

urlpatterns = [
    path('',views.index,name='index'),
    path('printers/',views.PrinterListView.as_view(),name='printer_list'), #show all printers
    path('printers/<str:serial_number>',views.PrinterDetailView.as_view(),name='printer_detail'),

    path('queue/', views.ProductionQueueListView.as_view(), name='queued-no-printers'),
    path('printqueue/all/', views.ProductionQueuePrintListView.as_view(), name='print-queue'),
    #path('printqueue/print/<int:pk>', views.send_print_job, name='send_to_production'),
    path('printqueue/<str:serial_number>/', views.PrinterProductionQueuePrintListView.as_view(), name='print-queue-printer'),

    path('queue/update/<int:pk>',views.ProductionQueuepdateView.as_view(),name='production_queue_update'),
    #path('about',views.about,name='about'),

    #path('files/',views.FileListView.as_view(),name='file_list_view'),
    path('files/',views.upload_three_mf, name='upload_three_mf'),
    path('queue/add/<int:file_id>/', views.add_to_production_queue, name='add_to_queue'),

]