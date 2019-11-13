import re

from django import forms

from .models import CSVUpload, valid_table__name


class CSVUploadForm(forms.ModelForm):
    class Meta:
        model = CSVUpload
        fields = ['csv_file', ]


class XYPublishForm(forms.ModelForm):
    # Added extra field to accept table name
    table_name = forms.CharField(max_length=63, validators=[valid_table__name])

    class Meta:
        model = CSVUpload
        fields = ['id', 'lat_field_name', 'lon_field_name', 'srs', 'geometry_type']


class WKTPublishForm(forms.ModelForm):
    table_name = forms.CharField(max_length=63, validators=[valid_table_column_name])

    class Meta:
        model = CSVUpload
        fields = ['id', 'srs', 'wkt_field_name', 'geometry_type']
