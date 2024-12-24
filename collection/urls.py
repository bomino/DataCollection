

# collection/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_data, name='upload_data'),
    path('uploads/', views.upload_list, name='upload_list'),
    path('download-template/<str:template_type>/', views.download_template, name='download_template'),
    path('delete-upload/<int:pk>/', views.delete_upload, name='delete_upload'),
]