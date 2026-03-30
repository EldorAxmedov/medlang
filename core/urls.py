from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Vocabulary Management
    path('dashboard/vocabulary/', views.vocabulary_list, name='manage_vocabulary'),
    path('dashboard/vocabulary/add/', views.vocabulary_edit, name='vocabulary_add'),
    path('dashboard/vocabulary/<uuid:pk>/edit/', views.vocabulary_edit, name='vocabulary_edit'),
    path('dashboard/vocabulary/<uuid:pk>/delete/', views.vocabulary_delete, name='vocabulary_delete'),
    
    # Test Management
    path('dashboard/tests/', views.tests_list, name='manage_tests'),
    path('dashboard/tests/add/', views.tests_edit, name='test_add'),
    path('dashboard/tests/<uuid:pk>/edit/', views.tests_edit, name='test_edit'),
    path('dashboard/tests/<uuid:pk>/delete/', views.tests_delete, name='test_delete'),
    path('dashboard/tests/<uuid:test_id>/questions/', views.question_list, name='manage_questions'),
    path('dashboard/tests/<uuid:test_id>/questions/add/', views.question_edit, name='question_add'),
    path('dashboard/tests/<uuid:test_id>/questions/<uuid:pk>/edit/', views.question_edit, name='question_edit'),
    path('dashboard/tests/<uuid:test_id>/questions/<uuid:pk>/delete/', views.question_delete, name='question_delete'),
    
    # Simulation Management
    path('dashboard/simulations/', views.simulations_list, name='manage_simulations'),
    path('dashboard/simulations/add/', views.simulations_edit, name='simulation_add'),
    path('dashboard/simulations/<uuid:pk>/edit/', views.simulations_edit, name='simulation_edit'),
    path('dashboard/simulations/<uuid:pk>/delete/', views.simulations_delete, name='simulation_delete'),
    path('dashboard/simulations/<uuid:scenario_id>/sessions/', views.simulation_session_list, name='simulation_sessions'),
    path('dashboard/simulations/session/<uuid:session_id>/', views.simulation_session_detail, name='session_detail_admin'),
    
    # Chat Management
    path('dashboard/chats/', views.chats_list, name='manage_chats'),
    
    # User Management
    path('dashboard/users/', views.users_list, name='manage_users'),
    path('dashboard/users/<uuid:pk>/delete/', views.user_delete, name='user_delete'),
]
