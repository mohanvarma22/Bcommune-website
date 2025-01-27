from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Idea, Job, Project, CustomUser, IndividualProfile, Bid, Internship, FreelanceProject, FreelanceBid, JobApplication, SavedApplication, LikeDislike

# Register all models with ImportExportModelAdmin
models = [Idea, Job, Project, CustomUser, Bid, Internship, FreelanceProject, FreelanceBid, JobApplication, SavedApplication, LikeDislike]

for model in models:
    admin.site.register(model, ImportExportModelAdmin)

# Customize IndividualProfileAdmin with import/export
class IndividualProfileAdmin(ImportExportModelAdmin):
    list_display = ('user', 'location', 'availability_status', 'work_type', 'salary_expected', 'current_position_title')
    list_filter = ('availability_status', 'work_type', 'location', 'salary_expected')

admin.site.register(IndividualProfile, IndividualProfileAdmin)