from django.db import models
from django.contrib import admin
from .models import YourModel

class YourModelAdmin(admin.ModelAdmin):
    list_display = ('field1', 'field2', 'field3')  # Columns in list view
    list_filter = ('field1', 'field4')            # Filter sidebar
    search_fields = ('field2', 'field3')          # Search box
    ordering = ('field1',)                        # Default ordering


    actions = ['mark_as_verified']

    def mark_as_verified(self, request, queryset):
        queryset.update(verified=True)
        self.message_user(request, f"{queryset.count()} items marked as verified.")

    mark_as_verified.short_description = "Mark selected as verified"
admin.site.register(YourModel, YourModelAdmin)
