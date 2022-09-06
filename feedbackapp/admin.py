from django.contrib import admin
from feedbackapp.models import Contact, QuestionCategory, Question, Message


class QuestionAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Contact)
admin.site.register(QuestionCategory)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Message)
