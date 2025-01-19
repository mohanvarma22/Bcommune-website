from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from .models import Idea, Job, Project, CustomUser, IndividualProfile, Bid, Internship,FreelanceProject, FreelanceBid, JobApplication
from users.forms import CompanySignupForm, IndividualSignupForm,IndividualProfileForm, CompanyProfileForm, BidForm,FreelanceProjectForm,FreelanceBidForm
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

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

    # Fetch all ideas
    ideas = Idea.objects.all()

    # Fetch jobs and order by the most recent
    jobs = Job.objects.all().order_by('-posted_date')

    # Fetch top 3 most recent freelance projects
    freelance_projects = FreelanceProject.objects.all().order_by('-created_at')[:3]

    # Render the dashboard
    return render(
        request,
        'individual_dashboard.html',
        {
            'ideas': ideas,
            'jobs': jobs,
            'freelance_projects': freelance_projects,
        }
    )

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

@login_required
@require_http_methods(["POST"])
def delete_job(request, job_id):
    try:
        job = get_object_or_404(Job, id=job_id, company_user=request.user)
        job.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)




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
def place_project_bid(request, project_id):
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
    recent_projects = Project.objects.filter(company=request.user).order_by('-created_at')[:3]
    recent_ideas = Idea.objects.all().order_by('-created_at')[:3]
    recent_internships = Internship.objects.filter(company_user=request.user).order_by('-posted_date')[:3]
    # Add this line to fetch recent freelance projects
    recent_freelance_projects = FreelanceProject.objects.filter(user=request.user).order_by('-created_at')[:3]
    
    return render(request, 'myportfolio.html', {
        'jobs': recent_jobs,
        'projects': recent_projects,
        'ideas': recent_ideas,
        'internships': recent_internships,
        'freelance_projects': recent_freelance_projects  # Add this line
    })


def all_jobs(request):
    if not request.user.is_authenticated:
        return redirect('login')

    jobs = Job.objects.filter(company_user=request.user)
    
    # Get the job_id from URL parameters
    selected_job_id = request.GET.get('job_id')
    
    return render(request, 'all_jobs.html', {
        'jobs': jobs,
        'selected_job_id': selected_job_id
    })

def all_projects(request):
    if not request.user.is_authenticated:
        return redirect('company_login')
    
    projects = Project.objects.filter(company=request.user).order_by('-created_at')
    selected_project_id = request.GET.get('project_id')
    
    return render(request, 'all_projects.html', {
        'projects': projects,
        'selected_project_id': selected_project_id
    })

def all_ideas(request):
    if not request.user.is_authenticated:
        return redirect('company_login')
    
    ideas = Idea.objects.all().order_by('-created_at')
    selected_idea_id = request.GET.get('idea_id')
    
    return render(request, 'all_ideas.html', {
        'ideas': ideas,
        'selected_idea_id': selected_idea_id
    })

def myinternships(request):
    if not request.user.is_authenticated:
        return redirect('company_login')
    company_internships = Internship.objects.filter(company_user=request.user).order_by('-posted_date')
    return render(request,'myinternships.html',{'internships':company_internships})

def post_internship(request):
    if request.method == 'POST':
        try:
            internship = Internship.objects.create(
                title=request.POST.get('job_title'),  # Matches corrected form
                company=request.POST.get('company_name'),
                location=request.POST.get('job_location'),  # Matches corrected form
                description=request.POST.get('job_description'),  # Matches corrected form
                requirements=request.POST.get('job_type'),
                duration=request.POST.get('duration'),
                salary=request.POST.get('salary'),
                company_user=request.user
            )
            return JsonResponse({'status': 'success', 'message': 'Internship posted successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return render(request, 'post_internship.html')


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
@require_http_methods(["POST"])
def delete_internship(request, internship_id):
    try:
        internship = get_object_or_404(Internship, id=internship_id, company_user=request.user)
        internship.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
def edit_internship(request, internship_id):  # Changed parameter name to internship_id
    internship = get_object_or_404(Internship, id=internship_id, company_user=request.user)
    
    if request.method == 'POST':
        try:
            internship.title = request.POST.get('job_title')  # Updated with internship variable
            internship.company = request.POST.get('company_name')
            internship.location = request.POST.get('job_location')
            internship.description = request.POST.get('job_description')
            internship.requirements = request.POST.get('job_type')
            internship.duration = request.POST.get('duration')
            internship.salary = request.POST.get('salary')
            internship.save()
            return JsonResponse({'status': 'success', 'message': 'Internship updated successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return render(request, 'edit_internship.html', {'internship': internship})

def freelance(request):
    if not request.user.is_authenticated:
        return redirect('company_login')
    projects = FreelanceProject.objects.filter(user=request.user)
    return render(request, 'freelance.html', {'projects': projects})

def post_freelance(request):
    if request.method == 'POST':
        form = FreelanceProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project_data = form.cleaned_data
            request.session['project_data'] = project_data  # Save form data in session for preview
            return redirect('preview_freelance_project')
    else:
        form = FreelanceProjectForm()

    return render(request, 'post_freelance.html', {'form': form})

def preview_freelance_project(request):
    project_data = request.session.get('project_data', None)
    if not project_data:
        return redirect('post_project')

    if request.method == 'POST':  # If confirmed, save the project
        form = FreelanceProjectForm(project_data)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user  # Associate project with logged-in user
            project.save()
            del request.session['project_data']  # Clear session
            return redirect('project_success')

    return render(request, 'preview_freelance_project.html', {'project_data': project_data})

def project_success(request):
    return render(request, 'project_success.html')

@login_required
@require_http_methods(["POST"])
def delete_freelance(request, project_id):
    """
    Delete a freelance project by its ID.
    """
    try:
        project = get_object_or_404(FreelanceProject, id=project_id, user=request.user)
        project.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def edit_freelance(request, project_id):
    """
    Edit a freelance project by its ID.
    """
    project = get_object_or_404(FreelanceProject, id=project_id, user=request.user)

    if request.method == 'POST':
        try:
            # Bind the form to the POST data and the existing instance
            form = FreelanceProjectForm(request.POST, request.FILES, instance=project)
            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success', 'message': 'Freelance project updated successfully!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid data submitted.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    # Render the edit form with the existing project data
    form = FreelanceProjectForm(instance=project)
    return render(request, 'edit_freelance.html', {'form': form, 'project': project})

def view_bids(request, project_id):
    # Fetch the project and its associated bids
    project = get_object_or_404(Project, id=project_id)
    bids = project.bids.select_related('bidder').order_by('-created_at')  # Assuming related_name is `bids` in the ForeignKey

    context = {
        "project": project,
        "bids": bids,
    }
    return render(request, "view_bids.html", context)

def all_internships(request):
    internships = Internship.objects.filter(company_user=request.user).order_by('-posted_date')
    
    return render(request, 'all_internships.html', {'internships': internships})

def all_freelance_projects(request):
    freelance_projects = FreelanceProject.objects.all().order_by('-created_at')
    return render(request, 'all_freelance_projects.html', {'freelance_projects': freelance_projects})


def all_freelance_projects_company(request):
    # Ensure the user is authenticated and fetch projects belonging to the logged-in user
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login page if not authenticated

    # Filter projects by the logged-in user (assuming company users are linked via the `user` field)
    freelance_projects = FreelanceProject.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'all_freelance_projects_company.html', {'freelance_projects': freelance_projects})



@login_required
def place_freelance_bid(request, project_id):
    project = get_object_or_404(FreelanceProject, id=project_id)
    
    # Check if user has already placed a bid
    existing_bid = FreelanceBid.objects.filter(project=project, bidder=request.user).first()
    if existing_bid:
        return redirect('view_my_freelance_bid', project_id=project_id)
    
    if request.method == 'POST':
        form = FreelanceBidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.project = project
            bid.bidder = request.user
            bid.save()
            messages.success(request, 'Your bid has been submitted successfully!')
            return redirect('all_freelance_projects')
    else:
        form = FreelanceBidForm(initial={
            'name': request.user.get_full_name(),
            'email': request.user.email
        })
    
    return render(request, 'place_freelance_bid.html', {
        'form': form,
        'project': project
    })

@login_required
def view_my_freelance_bid(request, project_id):
    project = get_object_or_404(FreelanceProject, id=project_id)
    bid = get_object_or_404(FreelanceBid, project=project, bidder=request.user)
    return render(request, 'view_my_freelance_bid.html', {
        'bid': bid,
        'project': project
    })

def view_freelance_bids(request, project_id):
    # Fetch the project and its bids
    project = get_object_or_404(FreelanceProject, id=project_id)
    bids = FreelanceBid.objects.filter(project=project).order_by('-created_at')

    return render(request, 'view_freelance_bids.html', {
        'project': project,
        'bids': bids,
    })

def individual_alljobs(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Fetch all jobs and order by most recent first
    jobs = Job.objects.all().order_by('-posted_date')  # Assuming `posted_date` is the field for job posting date

    # Get the job_id from URL parameters (if any)
    selected_job_id = request.GET.get('job_id')

    return render(request, 'individual_alljobs.html', {
        'jobs': jobs,
        'selected_job_id': selected_job_id
    })

def apply_job(request, job_id):
    # Fetch the job object
    job = get_object_or_404(Job, id=job_id)
    
    if request.method == 'POST':
        # Get additional data if needed from the form
        applicant_name = request.POST.get('name')
        applicant_email = request.POST.get('email')
        cover_letter = request.POST.get('cover_letter')
        
        # Create a job application
        JobApplication.objects.create(
            job=job,
            user=request.user,  # Assuming the user is logged in
            name=applicant_name,
            email=applicant_email,
            cover_letter=cover_letter
        )
        
        # Show a success message
        messages.success(request, 'You have successfully applied for the job!')
        return redirect('individual_alljobs')  # Redirect to the jobs list page
    
    return render(request, 'apply_jobs.html', {'job': job})

def job_success(request):
    return render(request,'job_success.html')