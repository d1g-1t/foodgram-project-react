from django.urls import include, path
from django.contrib import admin


"""
Маршруты:
/admin/ - Маршрут для административной панели;
/api/ - Маршрут для API.
"""
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
]
