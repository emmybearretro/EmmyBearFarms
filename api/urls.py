from django.urls import path

from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('printers/',views.PrinterListView.as_view(),name='index'),
    path('printer/<str:serial_number>',views.PrinterDetailView.as_view(),name='detail'),
    path('printer/<str:serial_number>/state', views.PrinterStatusView.as_view(), name='status_detail'),

    path('files/upload',views.FileUploadView.as_view(),name='file_upload'),


    #path('printer/<int:id>',views.printer,name='printer'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
