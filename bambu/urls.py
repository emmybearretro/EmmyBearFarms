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
    path('files/', views.upload_three_mf, name='file-list-view'),
   # path('files/<int:pk>/edit/', views.gcodefile_update, name='file-update'),
    path('files/<int:pk>/delete/', views.gcodefile_delete, name='file-delete'),
    path('queue/add/<int:file_id>/', views.add_to_production_queue, name='add_to_queue'),
    path('queue/<str:serial_number>/', views.command_queue_view, name='printer-command-queue'),
    path('printers/<str:serial_number>/send-command/<int:command_id>/', views.send_command_view, name='send_command'),
path('printers/<str:serial_number>/submitjob/<int:queue_id>/', views.add_to_command_queue, name='add_to_command_queue'),
    path('printers/<str:serial_number>/history/', views.printer_history_view, name='printer_history'),
path('clone-queue-item/<int:queue_id>/', views.clone_queue_item, name='clone_queue_item'),


]