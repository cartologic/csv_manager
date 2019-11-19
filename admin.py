from django.contrib import admin

from .models import CSVUpload


class CSVUploadAdmin(admin.ModelAdmin):
    list_display = ('user', 'csv_file', 'uploaded_at', 'features_count',)
    list_filter = ('uploaded_at',)
    search_fields = ('user__username', 'csv_file_name',)


admin.site.register(CSVUpload, CSVUploadAdmin)
