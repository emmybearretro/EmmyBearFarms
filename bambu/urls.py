from django.urls import path

from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('printers',views.PrinterListView.as_view(),name='printer_list'),
    path('printer/<int:pk>',views.PrinterDetailView.as_view(),name='printer_detail'),
    path('queue',views.ProductionQueueListView.as_view(),name='production_queue'),
    #path('about',views.about,name='about'),
]