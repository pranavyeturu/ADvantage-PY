from django.urls import path
from . import views

urlpatterns = [
    
    #customer uploading csv api 
    path("upload/", views.upload_customers, name="upload-customers"),
]


