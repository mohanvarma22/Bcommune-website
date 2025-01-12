from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.conf import settings 
from django.contrib.auth import get_user_model

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('individual', 'Individual'),
        ('company', 'Company'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='company') 
    company_name = models.CharField(max_length=255, null=True, blank=True)
    company_website = models.URLField(max_length=200, null=True, blank=True)
    industry = models.CharField(max_length=100, null=True, blank=True)
    company_size = models.CharField(max_length=20, null=True, blank=True)
    company_type = models.CharField(max_length=255, null=True, blank=True)
    designation = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    bcommune_profile = models.URLField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    about_company = models.TextField(null=True, blank=True)  # About the Company
    founding_year = models.PositiveIntegerField(null=True, blank=True)  # Establishment Year
    headquarters = models.CharField(max_length=255, null=True, blank=True)  # Headquarters Location
    branches = models.TextField(null=True, blank=True) 
    business_registration_number = models.CharField(max_length=100, null=True, blank=True)
    legal_structure = models.CharField(
        max_length=50,
        choices=[
            ('LLP', 'LLP'),
            ('Pvt Ltd', 'Private Limited'),
            ('Partnership', 'Partnership'),
            ('Sole Proprietorship', 'Sole Proprietorship'),
            ('Others', 'Others'),
        ],
        null=True,
        blank=True
    )
    core_services = models.TextField(null=True, blank=True)
    social_media_links = models.JSONField(default=dict, blank=True)  # Example: {"facebook": "", "linkedin": "", "twitter": ""}
    portfolio = models.TextField(null=True, blank=True)
    

    
class Idea(models.Model):
    title = models.CharField(max_length=200)
    patent_number = models.CharField(max_length=100, blank=True, null=True)
    brief_description = models.TextField()
    application_number = models.CharField(max_length=100, blank=True, null=True)
    problem_statement = models.TextField()
    solution = models.TextField()
    visibility = models.CharField(max_length=10, choices=[('public', 'Public'), ('private', 'Private')])
    details = models.TextField(blank=True, null=True)
    fund = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='idea_photos/', blank=True, null=True)
    video = models.FileField(upload_to='idea_videos/', blank=True, null=True)
    team_info = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Job(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    company_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    location = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.CharField(max_length=200)  # or TextField()
    salary = models.CharField(max_length=200, default="Not Specified") 
    posted_date = models.DateTimeField(default=timezone.now)
    # Add other fields as needed

    def __str__(self):
        return f"{self.title} at {self.company}"
    
class Project(models.Model):
    company = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    project_type = models.CharField(max_length=100)
    industry = models.CharField(max_length=100)
    budget = models.DecimalField(max_digits=15, decimal_places=2)
    timeline = models.DateField()
    location = models.CharField(max_length=200, blank=True, null=True)
    expertise_required = models.TextField()
    payment_terms = models.TextField()
    nda_required = models.BooleanField(default=False)
    confidentiality_required = models.BooleanField(default=False)
    ip_rights_required = models.BooleanField(default=False)
    custom_field = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class IndividualProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    tagline = models.CharField(max_length=255, blank=True, null=True)
    availability_status = models.CharField(max_length=50, choices=[
        ('actively_looking', 'Actively Looking'),
        ('not_available', 'Not Available'),
        ('open_to_offers', 'Open to Offers')
    ], default='open_to_offers')
    about_me = models.TextField(blank=True, null=True)
    key_skills = models.JSONField(blank=True, null=True)  # Store as a list of skills
    industries_of_interest = models.JSONField(blank=True, null=True)  # Store as a list
    desired_role = models.CharField(max_length=255, blank=True, null=True)
    desired_location = models.CharField(max_length=255, blank=True, null=True)
    work_type = models.CharField(max_length=50, choices=[
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
        ('on_site', 'On-Site')
    ], default='remote')
    salary_expected = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Work Experience Section
    current_position_title = models.CharField(max_length=255, blank=True, null=True)
    current_company = models.CharField(max_length=255, blank=True, null=True)
    current_duration = models.CharField(max_length=255, blank=True, null=True)
    key_responsibilities = models.TextField(blank=True, null=True)

    # Education Section
    qualification = models.CharField(max_length=255, blank=True, null=True)
    institution = models.CharField(max_length=255, blank=True, null=True)
    year_of_completion = models.IntegerField(blank=True, null=True)
    certifications = models.JSONField(blank=True, null=True)  # Store as a list

    # Portfolio/Projects Section
    projects = models.JSONField(blank=True, null=True)  # Store projects as a list of dicts

    # Achievements Section
    awards = models.JSONField(blank=True, null=True)  # Store awards as a list
    publications = models.JSONField(blank=True, null=True)  # Store publications as a list

    # Interests Section
    hobbies = models.JSONField(blank=True, null=True)  # Store as a list

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
class Bid(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                              limit_choices_to={'user_type': 'company'})  # Only companies can bid
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    proposal = models.TextField()
    estimated_timeline = models.IntegerField(help_text="Estimated days to complete")
    additional_details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['project', 'bidder']
        
    def __str__(self):
        return f"Bid by {self.bidder.company_name} on {self.project}"