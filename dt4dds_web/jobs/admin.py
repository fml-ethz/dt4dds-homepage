from django.contrib import admin

from .models import Job, BasicSubmission, AdvancedSubmission, ChallengeSubmission


class JobAdmin(admin.ModelAdmin):
    model = Job

    list_display = ('uid', 'state', 'submission_date', 'is_deleted')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.order_by('-submission_date')
        return qs

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()



class AbstractSubmissionAdmin(admin.ModelAdmin):
    actions = ['delete_model']

    list_display = ('name', 'email')

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.job.delete()
            obj.delete()

    def delete_model(self, request, obj):
        obj.job.delete()
        obj.delete()



class BasicSubmissionAdmin(admin.ModelAdmin):
    model = BasicSubmission


class AdvancedSubmissionAdmin(admin.ModelAdmin):
    model = AdvancedSubmission


class ChallengeSubmissionAdmin(admin.ModelAdmin):
    model = ChallengeSubmission


admin.site.register(Job, JobAdmin)
admin.site.register(BasicSubmission, BasicSubmissionAdmin)
admin.site.register(AdvancedSubmission, AdvancedSubmissionAdmin)
admin.site.register(ChallengeSubmission, ChallengeSubmissionAdmin)