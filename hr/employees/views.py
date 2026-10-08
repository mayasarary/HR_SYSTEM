from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django import forms
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q, Count
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from .models import Department, Employee
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView


class LogoutView(LoginRequiredMixin, DjangoLogoutView):
    http_method_names = ['get', 'post', 'options']
    next_page = 'login'

    def get(self, request, *args, **kwargs):
        from django.shortcuts import render
        return render(request, 'registration/logout.html')

class BaseTestView(TemplateView):
    template_name = 'base.html'

class LoginView(DjangoLoginView):
    template_name = 'registration/login.html'
    next_page = 'base_test'

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session.set_expiry(
            None if self.request.POST.get('remember_me') == '1' else 0
        )
        return response

class EmployeeForm(forms.ModelForm):
    email = forms.EmailField()
    basic_salary = forms.IntegerField(min_value=0)

    def get_field_groups(self):
        groups = [
            (_('Personal details'), ['full_name', 'gender', 'date_of_birth']),
            (_('Contact information'), ['email', 'phone_number', 'address']),
            (_('Employment and contract'), ['department', 'position', 'hire_date', 'employment_status',
                                         'contract_type', 'contract_start_date', 'contract_end_date']),
            (_('Salary and work hours'), ['basic_salary', 'currency_code', 'working_start', 'working_end']),
            (_('Login account'), ['user']),
        ]
        return [(title, [self[name] for name in names]) for title, names in groups]

    class Meta:
        model = Employee
        fields = ['full_name', 'department', 'position', 'gender', 'phone_number', 'email', 'address',
                  'date_of_birth', 'hire_date', 'employment_status',
                  'contract_type', 'contract_start_date', 'contract_end_date',
                  'basic_salary', 'currency_code', 'working_start', 'working_end', 'user']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            **{name: forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'})
               for name in ['date_of_birth', 'hire_date', 'contract_start_date', 'contract_end_date']},
            **{name: forms.TimeInput(format='%H:%M', attrs={'type': 'time'})
               for name in ['working_start', 'working_end']},
        }
        labels = {'user': _('Linked login account'), 'employment_status': _('Active employee'),
                  'working_start': _('Work start time'), 'working_end': _('Work end time')}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].required = True
        self.fields['position'].required = True
        contract_type = (self.data.get(self.add_prefix('contract_type'))
                         if self.is_bound
                         else self.initial.get('contract_type', self.instance.contract_type))
        end_date = self.fields['contract_end_date']
        end_date.required = contract_type in (
            Employee.ContractTypeChoices.PART_TIME,
            Employee.ContractTypeChoices.CONTRACTOR,
            Employee.ContractTypeChoices.INTERN,
        )
        if self.is_bound and contract_type == Employee.ContractTypeChoices.FULL_TIME:
            end_date.disabled = True
            self.initial['contract_end_date'] = None
        accounts = Q(employees__isnull=True)
        if self.instance.user_id:
            accounts |= Q(pk=self.instance.user_id)
        self.fields['user'].queryset = get_user_model().objects.filter(accounts).order_by('username')
        for name, field in self.fields.items():
            field.label = _(field.label or name.replace('_', ' ').capitalize())
            if isinstance(field, forms.ChoiceField) and not isinstance(field, forms.ModelChoiceField):
                field.choices = [(value, _(label)) for value, label in field.choices]
            field.widget.attrs['class'] = ('form-check-input' if isinstance(field.widget, forms.CheckboxInput)
                                          else 'form-select' if isinstance(field.widget, forms.Select)
                                          else 'form-control')
            if name in ['working_start', 'working_end']:
                field.input_formats = ['%H:%M', '%H:%M:%S']

    def clean(self):
        data = super().clean()
        if data.get('contract_type') == Employee.ContractTypeChoices.FULL_TIME:
            data['contract_end_date'] = None
        for start, end, message in [
            ('contract_start_date', 'contract_end_date', _('Contract end must be on or after contract start.')),
            ('date_of_birth', 'hire_date', _('Hire date must be after date of birth.')),
        ]:
            if data.get(start) and data.get(end):
                invalid = data[end] <= data[start] if start == 'date_of_birth' else data[end] < data[start]
                if invalid:
                    self.add_error(end, message)
        from django.utils import timezone
        if data.get('date_of_birth') and data['date_of_birth'] > timezone.localdate():
            self.add_error('date_of_birth', _('Date of birth cannot be in the future.'))
        return data


class EmployeeListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    extra_context = {'page_title': _('Employee List')}
    model = Employee
    permission_required = 'employees.view_employee'
    template_name = 'employee/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 5

    def get_queryset(self):
        queryset = Employee.objects.select_related('user', 'department')
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(Q(full_name__icontains=query) | Q(email__icontains=query) |
                                       Q(phone_number__icontains=query))
        status = self.request.GET.get('status', '')
        if status in ('active', 'inactive'):
            queryset = queryset.filter(employment_status=status == 'active')
        contract = self.request.GET.get('contract', '')
        if contract in Employee.ContractTypeChoices.values:
            queryset = queryset.filter(contract_type=contract)
        sort = self.request.GET.get('sort', 'pk')
        if sort not in ('pk', 'full_name', '-full_name', 'hire_date', '-hire_date'):
            sort = 'pk'
        return queryset.order_by('pk') if sort == 'pk' else queryset.order_by(sort, 'pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract_choices'] = Employee.ContractTypeChoices.choices
        params = self.request.GET.copy()
        params.pop('page', None)
        context['filter_query'] = params.urlencode()
        return context


class EmployeeCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    extra_context = {'page_title': 'Add Employee'}
    model = Employee
    form_class = EmployeeForm
    permission_required = 'employees.add_employee'
    template_name = 'employee/employee_form.html'
    success_url = reverse_lazy('employee_add')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_groups'] = context['form'].get_field_groups()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Employee %(name)s was added successfully.') % {'name': self.object.full_name})
        return response


class EmployeeDetailsView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    extra_context = {'page_title': 'Employee Details'}
    model = Employee
    permission_required = 'employees.view_employee'
    template_name = 'employee/employee_details.html'
    context_object_name = 'employee'

    def get_queryset(self):
        return Employee.objects.select_related('user', 'department')


class EmployeeProfileView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    extra_context = {'page_title': 'Employee Profile'}
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee/profile.html'
    context_object_name = 'employee'
    http_method_names = ['get', 'post', 'head', 'options']

    def get_permission_required(self):
        permissions = ['employees.view_employee']
        if self.request.method == 'POST':
            permissions.append('employees.change_employee')
        return permissions

    def get_queryset(self):
        return Employee.objects.select_related('user', 'department')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = self.request.user.has_perm('employees.change_employee')
        context['field_groups'] = context['form'].get_field_groups()
        return context

    def get_success_url(self):
        return reverse('employee_profile', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Employee profile updated successfully.'))
        return response

class DepartmentView(LoginRequiredMixin, TemplateView):
    template_name = 'department/department.html'
    extra_context = {'page_title': 'Departments'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        return context


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
        labels = {'name': 'Department name'}
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control', 'autofocus': True})}

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if Department.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError(_('A department with this name already exists.'))
        return name


class DepartmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    permission_required = 'employees.add_department'
    template_name = 'department/department_form.html'
    extra_context = {'page_title': 'Add Department'}
    success_url = reverse_lazy('department_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Department added successfully.'))
        return response


class DepartmentEmployeesView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Employee
    permission_required = 'employees.view_employee'
    template_name = 'department/department_employees.html'
    context_object_name = 'employees'
    paginate_by = 5

    def get_queryset(self):
        from django.shortcuts import get_object_or_404
        self.department = get_object_or_404(Department, code=self.kwargs['department'])
        return Employee.objects.filter(department=self.department).order_by('pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['department_name'] = self.department.name
        context['page_title'] = context['department_name']
        return context


class DashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    extra_context = {'page_title': 'Dashboard'}
    template_name = 'dashboard/dashboard.html'
    permission_required = 'employees.view_employee'

    def get_context_data(self, **kwargs):
        from datetime import timedelta
        from django.utils import timezone
        from .models import AttendanceRecords
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        employees = Employee.objects.all()
        totals = employees.aggregate(
            total=Count('pk'), active=Count('pk', filter=Q(employment_status=True)),
            new_hires=Count('pk', filter=Q(hire_date__gte=today.replace(day=1), hire_date__lte=today)),
        )
        upcoming = employees.filter(contract_type__in=['PT', 'CON', 'INT'],
                                    contract_end_date__range=(today, today + timedelta(days=30)))
        context.update(today=today, totals=totals, expiring_count=upcoming.count(),
                       expiring_contracts=upcoming.order_by('contract_end_date', 'pk')[:5],
                       recent_employees=employees.filter(hire_date__lte=today).order_by('-hire_date', '-pk')[:5],
                       active_percentage=round(totals['active'] * 100 / totals['total']) if totals['total'] else 0)
        breakdown = dict(employees.values_list('contract_type').annotate(total=Count('pk')))
        context['contract_chart'] = {'labels': [str(_(label)) for code, label in Employee.ContractTypeChoices.choices],
                                     'values': [breakdown.get(code, 0) for code in Employee.ContractTypeChoices.values]}
        months = []
        for offset in range(5, -1, -1):
            index = today.year * 12 + today.month - 1 - offset
            months.append(today.replace(year=index // 12, month=index % 12 + 1, day=1))
        from django.utils.formats import date_format
        context['hiring_chart'] = {'labels': [date_format(month, 'M Y') for month in months],
                                   'values': [employees.filter(hire_date__year=month.year,
                                              hire_date__month=month.month, hire_date__lte=today).count() for month in months]}
        if self.request.user.has_perm('employees.view_attendancerecords'):
            attendance = AttendanceRecords.objects.filter(attendance_date__date=today)
            context['attendance_today'] = [
                (label, attendance.filter(status=code).values('employee_id').distinct().count())
                for code, label in AttendanceRecords.AttendanceStatus.choices
            ]
        return context
