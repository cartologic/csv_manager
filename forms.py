from django import forms
import re
from .models import CSVUpload


class CSVUploadForm(forms.ModelForm):
    class Meta:
        model = CSVUpload
        fields = ['csv_file', ]


class CSVPublishForm(forms.ModelForm):
    table_name = forms.CharField(max_length=63)
    class Meta:
        model = CSVUpload
        fields = ['id', 'lat_field_name', 'lon_field_name', 'srs',]

    def clean_table_name(self):
        pattern = r"^[a-z0-9_]{1,63}$"
        table_name = self.cleaned_data['table_name']
        if not re.search(pattern, table_name):
            raise forms.ValidationError(('Invalid table name: %(value)s, Must be alphanumeric, Max length: 63 Bytes'), params={'value': table_name},)
        return table_name