from django.contrib import admin
from django.urls import path, include

# Defines the urls
urlpatterns = [
    path('admin/', admin.site.urls),
    path("backend2/", include("backend2app.urls")),
]
