"""
URL configuration for hr project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from employees import views


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('base/', views.DashboardView.as_view(), name='base_test'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('base/departments/', views.DepartmentView.as_view(), name='department_list'),
    path('base/departments/add/', views.DepartmentCreateView.as_view(), name='department_add'),
    path('base/departments/<str:department>/', views.DepartmentEmployeesView.as_view(), name='department_employees'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('base/employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('base/employees/add/', views.EmployeeCreateView.as_view(), name='employee_add'),
    path('base/employees/<int:pk>/profile/', views.EmployeeProfileView.as_view(), name='employee_profile'),
    path('base/employees/<int:pk>/details/', views.EmployeeDetailsView.as_view(), name='employee_details'),
    path('base/employees/<int:pk>/', views.EmployeeProfileView.as_view(), name='employee_detail'),
]
