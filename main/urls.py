from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings_view, name='settings'),

    # Gestion des utilisateurs
    path('users/', views.users_list, name='users_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/toggle/', views.user_toggle_active, name='user_toggle_active'),
    path('users/<int:pk>/password/', views.user_change_password, name='user_change_password'),

    # Gestion des sessions
    path('sessions/', views.sessions_list, name='sessions_list'),
    path('sessions/<str:session_key>/delete/', views.session_delete, name='session_delete'),

    # Notifications
    path('api/notifications/', views.notifications_api, name='notifications_api'),
    path('api/notifications/<int:pk>/read/', views.notification_mark_read, name='notification_mark_read'),
    path('api/notifications/read-all/', views.notifications_mark_all_read, name='notifications_mark_all_read'),
]