from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('role-selection/', views.role_selection, name='role_selection'),

    # Citizen
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),

    # Authority
    path('authority/register/', views.authority_register, name='authority_register'),
    path('authority/login/', views.authority_login, name='authority_login'),

    # Shared
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
]
