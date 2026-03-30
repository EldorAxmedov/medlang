from django.urls import path
from . import views

urlpatterns = [
    path('', views.simulation_list, name='simulation_list'),
    path('start/<uuid:scenario_id>/', views.start_simulation, name='start_simulation'),
    path('session/<uuid:session_id>/', views.simulation_detail, name='simulation_detail'),
    path('session/<uuid:session_id>/finish/', views.complete_simulation, name='complete_simulation'),
]
