from django.contrib import admin
from django.urls import path

from develop import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cac/', views.cac),
]
