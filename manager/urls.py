from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('project/add/', views.add_project, name='add_project'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('tasks/', views.task_list, name='task_list'),
    path('task/add/', views.add_task, name='add_task'),
    path('task/ajax/add/', views.ajax_add_task, name='ajax_add_task'),
    path('project/ajax/add/', views.ajax_add_project, name='ajax_add_project'),
    path('project/edit/<int:pk>/', views.edit_project, name='edit_project'),
    path('project/delete/<int:pk>/', views.delete_project, name='delete_project'),
    path('project/ajax/edit/<int:pk>/', views.ajax_edit_project, name='ajax_edit_project'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('task/complete/<int:task_id>/', views.mark_task_complete, name='mark_task_complete'),
    path('task/<int:task_id>/complete/', views.complete_task, name='complete_task')
]
