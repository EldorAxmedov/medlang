from django.urls import path
from . import views
from tests import views as test_views
from chat import views as chat_views

urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # --- Student Interface ---
    path('tests/', test_views.student_test_list, name='student_test_list'),
    path('tests/<uuid:pk>/take/', test_views.test_take, name='test_take'),
    path('chats/', chat_views.chat_list, name='chat_list_view'),
    path('chats/<uuid:room_id>/', chat_views.chat_room, name='chat_room_view'),
    path('chats/start/<uuid:user_id>/', chat_views.start_p2p_chat, name='start_p2p_chat_view'),
    
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
    path('dashboard/chats/add/', views.chats_edit, name='chat_add'),
    path('dashboard/chats/<uuid:pk>/edit/', views.chats_edit, name='chat_edit'),
    path('dashboard/chats/<uuid:pk>/delete/', views.chats_delete, name='chat_delete'),
    
    # User Management
    path('dashboard/users/', views.users_list, name='manage_users'),
    path('dashboard/users/add/', views.user_edit, name='user_add'),
    path('dashboard/users/<uuid:pk>/edit/', views.user_edit, name='user_edit'),
    path('dashboard/users/<uuid:pk>/delete/', views.user_delete, name='user_delete'),
]
