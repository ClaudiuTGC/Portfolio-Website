from django.contrib import admin

from .models import Education, Experience, Project, SiteProfile, Skill

admin.site.site_header = "Portfolio administration"


@admin.register(SiteProfile)
class SiteProfileAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return super().has_add_permission(request) and not SiteProfile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("role", "company", "start_date", "end_date")
    search_fields = ("role", "company", "highlights")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "context", "position")
    list_editable = ("position",)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary", "stack")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "position")
    list_filter = ("category",)
    search_fields = ("name", "category")


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("title", "institution", "kind", "date", "status")
    list_filter = ("kind",)
    search_fields = ("title", "institution")
