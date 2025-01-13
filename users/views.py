from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from .models import Idea, Job, Project, CustomUser, IndividualProfile, Bid
from users.forms import CompanySignupForm, IndividualSignupForm,IndividualProfileForm, CompanyProfileForm, BidForm
from django.contrib.auth import logout
from django.http import JsonResponse

def logout_view(request):
    logout(request)
    return redirect('company_login')

def home(request):
    return render(request, 'home.html')

def individual_signup(request):
    if request.method == 'POST':
        form = IndividualSignupForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['password'] != form.cleaned_data['confirm_password']:
                messages.error(request, "Passwords do not match.")
                return redirect('individual_signup')

            if CustomUser.objects.filter(email=form.cleaned_data['email']).exists():
                messages.error(request, "Email already exists.")
                return redirect('individual_signup')

            try:
                user = CustomUser.objects.create_user(
                    username=form.cleaned_data['email'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['name'],
                    user_type='individual'
                )

                # Create associated profile
                IndividualProfile.objects.create(user=user)

                messages.success(request, "Account created successfully!")
                return redirect('individual_login')
            except Exception as e:
                messages.error(request, f"Error creating account: {str(e)}")
                return redirect('individual_signup')
    else:
        form = IndividualSignupForm()
    return render(request, 'individual_signup.html', {'form': form})

def individual_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None and user.user_type == 'individual':
            login(request, user)
            return redirect('individual_dashboard')
        else:
            messages.error(request, "Invalid credentials or wrong user type.")
            return redirect('individual_login')
    
    return render(request, 'individual_login.html')

@login_required
def individual_dashboard(request):
    if request.user.user_type != 'individual':
        return redirect('individual_login')
    ideas = Idea.objects.all()  # Get all ideas submitted
    jobs = Job.objects.all().order_by('-posted_date')
    return render(request, 'individual_dashboard.html', {'ideas': ideas, 'jobs':jobs})

def company_signup(request):
    if request.method == 'POST':
        form = CompanySignupForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, "Company account created successfully!")
                return redirect('company_login')
            except Exception as e:
                messages.error(request, f"Error creating account: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CompanySignupForm()
    return render(request, 'company_signup.html', {'form': form})

def company_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None and user.user_type == 'company':
            login(request, user)
            return redirect('company_dashboard')
        else:
            messages.error(request, "Invalid credentials or wrong user type.")
    return render(request, 'company_login.html')


# View for Company Dashboard (requires login)
@login_required
def company_dashboard(request):
    if request.user.user_type != 'company':
        return redirect('company_login')
    
    ideas = Idea.objects.all().order_by('-created_at')[:3]
    recent_projects = Project.objects.exclude(company=request.user).order_by('-created_at')[:3]
    my_projects = Project.objects.filter(company=request.user).order_by('-created_at')[:3]
    
    context = {
        'ideas': ideas,
        'recent_projects': recent_projects,
        'my_projects': my_projects,
        'company_name': request.user.company_name,
    }
    return render(request, 'company_dashboard.html', context)
def ideaform(request):
    return render(request, 'ideaform.html')

def submit_idea(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        patent_number = request.POST.get('patent_number')
        brief_description = request.POST.get('brief_description')
        application_number = request.POST.get('application_number')
        problem_statement = request.POST.get('problem_statement')
        solution = request.POST.get('solution')
        visibility = request.POST.get('visibility')
        details = request.POST.get('details')
        fund = request.POST.get('fund')
        category = request.POST.get('category')
        photo = request.FILES.get('photo')
        video = request.FILES.get('video')
        team_info = request.POST.get('team_info')

        # Save to database
        idea = Idea(
            title=title,
            patent_number=patent_number,
            brief_description=brief_description,
            application_number=application_number,
            problem_statement=problem_statement,
            solution=solution,
            visibility=visibility,
            details=details,
            fund=fund,
            category=category,
            photo=photo,
            video=video,
            team_info=team_info
        )
        idea.save()

        return JsonResponse({'message': 'Idea submitted successfully!'})

    return JsonResponse({'error': 'Invalid request method!'}, status=400)


def ideas_and_invest(request):
    return render(request, 'ideasandinvest.html')


def myjobs(request):
    if not request.user.is_authenticated:
        return redirect('company_login')
    
    # Get jobs for the current company user
    company_jobs = Job.objects.filter(company_user=request.user).order_by('-posted_date')
    return render(request, 'myjobs.html', {'jobs': company_jobs})

def post_job(request):
    if request.method == 'POST':
        try:
            job = Job.objects.create(
                title=request.POST.get('job_title'),
                company=request.POST.get('company_name'),
                location=request.POST.get('job_location'),
                description=request.POST.get('job_description'),
                requirements=request.POST.get('job_type'),
                salary=request.POST.get('salary'),
                company_user=request.user  # Add this line
            )
            return JsonResponse({'status': 'success', 'message': 'Job posted successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return render(request, 'create_job.html')

@login_required
def myprojects(request):
    # Check if the user is a company user
    other_company_projects = Project.objects.exclude(company=request.user).order_by('-created_at')
    
    # Get projects posted by the current company (for portfolio section)
    my_projects = Project.objects.filter(company=request.user).prefetch_related('bids').order_by('-created_at')
    
    context = {
        'projects': other_company_projects,
        'my_projects': my_projects
    }
    return render(request, 'myprojects.html', context)
@login_required
def post_project(request):
    if request.method == 'POST':
        # Create new project from form data
        project = Project(
            company=request.user,
            title=request.POST['title'],
            description=request.POST['description'],
            project_type=request.POST['type'],
            industry=request.POST['industry'],
            budget=request.POST['budget'],
            timeline=request.POST['timeline'],
            location=request.POST['location'],
            expertise_required=request.POST['expertise'],
            payment_terms=request.POST['payment-terms'],
        )
        project.save()
        messages.success(request, 'Project posted successfully!')
        return redirect('myprojects')
    
    return render(request, 'myprojectform.html')
    
    
def myprojectform(request):
    return render(request, 'myprojectform.html') 

@login_required
def delete_project(request, project_id):
    try:
        project = Project.objects.get(id=project_id, company=request.user)
        project.delete()
        messages.success(request, 'Project deleted successfully!')
    except Project.DoesNotExist:
        messages.error(request, 'Project not found or you do not have permission to delete it.')
    return redirect('myprojects')

@login_required
def edit_project(request, project_id):
    try:
        project = get_object_or_404(Project, id=project_id, company=request.user)
        
        if request.method == 'POST':
            project.title = request.POST['title']
            project.description = request.POST['description']
            project.project_type = request.POST['type']
            project.industry = request.POST['industry']
            project.budget = request.POST['budget']
            project.timeline = request.POST['timeline']  # This will now be in YYYY-MM-DD format
            project.location = request.POST['location']
            project.expertise_required = request.POST['expertise']
            project.payment_terms = request.POST['payment-terms']
            
            # Handle boolean fields
            project.nda_required = 'nda_required' in request.POST
            project.confidentiality_required = 'confidentiality_required' in request.POST
            project.ip_rights_required = 'ip_rights_required' in request.POST
            
            # Handle optional field
            project.custom_field = request.POST.get('custom_field', '')
            
            project.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('myprojects')
            
        return render(request, 'edit_project.html', {'project': project})
    except Exception as e:
        messages.error(request, f'Error editing project: {str(e)}')
        return redirect('myprojects')
    

def explore_all_ideas(request):
    ideas = Idea.objects.filter(visibility='public').order_by('-created_at')
    return render(request, 'explore_all_ideas.html', {'ideas': ideas})

def idea_detail(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    return render(request, 'idea_detail.html', {'idea': idea})


def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, company_user=request.user)
    
    if request.method == 'POST':
        try:
            job.title = request.POST.get('job_title')
            job.company = request.POST.get('company_name')
            job.location = request.POST.get('job_location')
            job.description = request.POST.get('job_description')
            job.requirements = request.POST.get('job_type')
            job.salary = request.POST.get('salary')
            job.save()
            return JsonResponse({'status': 'success', 'message': 'Job updated successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return render(request, 'edit_job.html', {'job': job})

def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, company_user=request.user)
    if request.method == 'POST':
        job.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)




@login_required
def explore_projects(request):
    # Fetch projects excluding those belonging to the logged-in company
    other_company_projects = Project.objects.exclude(company=request.user).order_by('-created_at')
    
    # Handle AJAX request for project details
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        project_id = request.GET.get('project_id')
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
                data = {
                    'title': project.title,
                    'description': project.description,
                    'project_type': project.project_type,
                    'industry': project.industry,
                    'budget': float(project.budget),
                    'timeline': project.timeline.strftime('%Y-%m-%d'),
                    'location': project.location or 'Not specified',
                    'expertise_required': project.expertise_required,
                    'payment_terms': project.payment_terms,
                    'nda_required': project.nda_required,
                    'confidentiality_required': project.confidentiality_required,
                    'ip_rights_required': project.ip_rights_required,
                    'custom_field': getattr(project, 'custom_field', None),  # Safely handle custom_field
                    'created_at': project.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                return JsonResponse(data)
            except Project.DoesNotExist:
                return JsonResponse({'error': 'Project not found'}, status=404)
        else:
            return JsonResponse({'error': 'Invalid project ID'}, status=400)

    # Get selected project ID from URL parameter
    selected_project_id = request.GET.get('selected_project')

    # Determine the project to display first
    first_project = None
    if selected_project_id:
        try:
            first_project = Project.objects.get(id=selected_project_id)
        except Project.DoesNotExist:
            first_project = other_company_projects.first()
    else:
        first_project = other_company_projects.first()
    
    # Context for rendering the template
    context = {
        'projects': other_company_projects,
        'first_project': first_project,
        'selected_project_id': selected_project_id,
    }
    return render(request, 'explore_projects.html', context)

@login_required
def edit_individual_profile(request):
    try:
        profile = IndividualProfile.objects.get(user=request.user)
    except IndividualProfile.DoesNotExist:
        profile = IndividualProfile(user=request.user)

    if request.method == 'POST':
        form = IndividualProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('individual_profile')  # Replace with the desired redirect URL
    else:
        form = IndividualProfileForm(instance=profile)

    return render(request, 'edit_individual_profile.html', {'form': form})

@login_required
def individual_profile(request):
    profile = get_object_or_404(IndividualProfile, user=request.user)
    return render(request, 'individual_profile.html', {'profile': profile})


@login_required
def company_profile(request):
    user = request.user
    if user.user_type != 'company':  # Check the user_type field
        return redirect('home')  # Redirect if the user is not a company.

    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('company_profile')
    else:
        form = CompanyProfileForm(instance=user)

    return render(request, 'company_profile.html', {'form': form, 'user': user})

@login_required
def faq(request):
    return render(request,'faq.html')

@login_required
def place_bid(request, project_id):
    # Check if user is a company
    if request.user.user_type != 'company':
        messages.error(request, "Only companies can place bids!")
        return redirect('explore_projects')  # Redirect to explore_projects
    
    project = get_object_or_404(Project, id=project_id)
    
    # Prevent project owner from bidding on their own project
    if project.company == request.user:
        messages.error(request, "You cannot bid on your own project!")
        return redirect('explore_projects')  # Redirect to explore_projects
    
    # Check if user already has a bid
    existing_bid = Bid.objects.filter(project=project, bidder=request.user).first()
    
    if request.method == 'POST':
        form = BidForm(request.POST, instance=existing_bid)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.project = project
            bid.bidder = request.user
            bid.save()
            messages.success(request, 'Your bid has been placed successfully!')
            return redirect('explore_projects')  # Redirect to explore_projects
    else:
        form = BidForm(instance=existing_bid)
    
    context = {
        'form': form,
        'project': project,
        'existing_bid': existing_bid
    }
    return render(request, 'bidform.html', context)

def myportfolio(request):
    if not request.user.is_authenticated:
        return redirect('company_login')
    
    # Fetch all jobs for the currently logged-in company user
    recent_jobs = Job.objects.filter(company_user=request.user).order_by('-posted_date')[:3]
    return render(request, 'myportfolio.html', {'jobs': recent_jobs})

def all_jobs(request):
    return render(request, 'all_jobs.html')