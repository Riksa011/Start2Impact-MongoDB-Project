from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # admin url
    path('admin/', admin.site.urls),
    # exchange app url
    path('', include('apps.exchange.urls')),
]
