from django.contrib import admin
from .models import ImportLog, ChangeLog, ChatMessage, Cohort, Funding, Milestone, Partner, Project
for m in (ImportLog, Cohort, Milestone, Partner, Funding, ChangeLog, ChatMessage):
    admin.site.register(m)
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "domain", "cohort", "status", "progress")
    list_filter = ("status", "domain", "cohort")
    search_fields = ("title", "owner")
