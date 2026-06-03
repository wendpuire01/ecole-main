from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings_view, name='settings'),

    # Notifications
    path('api/notifications/', views.notifications_api, name='notifications_api'),
    path('api/notifications/<int:pk>/read/', views.notification_mark_read, name='notification_mark_read'),
    path('api/notifications/read-all/', views.notifications_mark_all_read, name='notifications_mark_all_read'),
]