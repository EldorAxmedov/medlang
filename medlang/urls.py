from django.urls import path, include
from django.contrib import admin
from core.views import index, dashboard
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        "project": "MedLang — Medical English Platform",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "register":      request.build_absolute_uri('/api/users/'),
            "login":         request.build_absolute_uri('/api/users/login/'),
            "token_refresh": request.build_absolute_uri('/api/token/refresh/'),
            "users_list":    request.build_absolute_uri('/api/users/'),
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/info/', api_root, name='api-root'),
    path('simulations/', include('simulation.urls')),
    path('', include('core.urls')),
]
