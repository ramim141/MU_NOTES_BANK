from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('note/create/', views.create_note, name='create_note'),
    path('note/<int:note_id>/edit/', views.edit_note, name='edit_note'),
    path('note/<int:note_id>/delete/', views.delete_note, name='delete_note'),
    path('note/<int:note_id>/', views.view_note, name='view_note'),
    path('register/', views.register, name='register'),
    path('profile/', views.user_profile, name='user_profile'),
    path('note/<int:note_id>/like/', views.like_note, name='like_note'),
    path('search/', views.search_notes, name='search_notes'),
    path('note/<int:note_id>/share/', views.share_note, name='share_note'),
    path('notifications/', views.notifications, name='notifications'),
    path('notification/<int:notification_id>/mark-as-read/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('note/<int:note_id>/export/', views.export_note, name='export_note'),
    path('profile/', views.user_profile, name='user_profile'),
]

