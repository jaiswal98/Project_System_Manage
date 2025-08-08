from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Task
from .forms import ProjectForm, TaskForm
from datetime import date
from django.db.models import Count, Q, F
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group

@login_required
def dashboard(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    return render(request, 'manager/dashboard.html', {'tasks': tasks})

@login_required
def mark_task_complete(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)

    if request.method == 'POST':
        task.status = 'Completed'
        task.save()

        # Check if all tasks of the project are now completed
        project = task.project
        if all(t.status == 'Completed' for t in project.tasks.all()):
            # You can set a flag or just let the UI detect it using is_completed()
            pass

    return redirect('dashboard')

@csrf_exempt
def ajax_add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            return JsonResponse({'success': True, 'task_id': task.id, 'title': task.title})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
        
@csrf_exempt
def ajax_add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            return JsonResponse({'success': True, 'project_id': project.id, 'project_name': project.name})
        return JsonResponse({'success': False, 'errors': form.errors})
    

@csrf_exempt
def ajax_edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    else:
        data = {
            'name': project.name,
            'description': project.description,
            'start_date': project.start_date.strftime('%Y-%m-%d'),
            'end_date': project.end_date.strftime('%Y-%m-%d'),
        }
        return JsonResponse(data)

@login_required
def project_list(request):
    if request.user.groups.filter(name='Employee').exists():
        return redirect('dashboard')  # only see own tasks
    elif request.user.groups.filter(name='Manager').exists():
        projects = Project.objects.all()  # limited edit
    else:
        projects = Project.objects.all()  # Admin access
        
    filter_status = request.GET.get('status')
    search_query = request.GET.get('search', '')

    # Annotate total and completed tasks
    projects = Project.objects.annotate(
        total_tasks=Count('tasks'),
        completed_tasks=Count('tasks', filter=Q(tasks__status='Completed'))
    )

    if filter_status == 'completed':
        projects = projects.filter(total_tasks=F('completed_tasks'), total_tasks__gt=0)
    elif filter_status == 'ongoing':
        projects = projects.exclude(total_tasks=F('completed_tasks'))

    if search_query:
        projects = projects.filter(name__icontains=search_query)

    return render(request, 'manager/project_list.html', {
        'projects': projects,
        'filter_status': filter_status,
        'search_query': search_query,
        'form': ProjectForm()
    })

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'manager/project_detail.html', {'project': project})

def add_project(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('project_list')
    return render(request, 'manager/project_form.html', {'form': form})

@login_required
def task_list(request):
    filter_status = request.GET.get('status')
    tasks = Task.objects.select_related('project')
    if filter_status:
        tasks = tasks.filter(status=filter_status)

    form = TaskForm()

    return render(request, 'manager/task_list.html', {
        'tasks': tasks,
        'filter_status': filter_status,
        'form': form,
        'projects': Project.objects.all(),
        'users': User.objects.all(),
    })

def add_task(request):
    form = TaskForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('task_list')
    return render(request, 'manager/task_form.html', {'form': form})

def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'manager/edit_project.html', {'form': form, 'project': project})


def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        return redirect('project_list')
    return render(request, 'manager/delete_project.html', {'project': project})

# Register view
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            default_group = Group.objects.get(name='Employee')  # or Manager/Admin
            user.groups.add(default_group)
    else:
        form = UserCreationForm()
    return render(request, 'manager/register.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'manager/login.html', {'error': 'Invalid credentials'})
    return render(request, 'manager/login.html')

# Logout view
def logout_view(request):
    logout(request)
    return redirect('login')


def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.status = 'Completed'
    task.save()
    return redirect('dashboard')