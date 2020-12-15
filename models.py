import os
import re

from django.db import models
from geonode.people.models import Profile

from .constants import GeometryTypeChoices

CSV_FILE_PERMISSIONS = (
    ('view_csv', 'View CSV'),
    ('download_csv', 'Download CSV'),
    ('delete_csv', 'Delete CSV'),
    ('publish_csv', 'Publish CSV'),
)


def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.csv']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.only {} allowed'
                              .format(','.join(valid_extensions)))


def valid_table__name(name):
    from django.core.exceptions import ValidationError
    pattern = r"^[a-z0-9_]{1,63}$"
    if not re.search(pattern, name):
        raise ValidationError(
            'Invalid table / column name: {}, Must be alphanumeric, Max length: 63 Bytes'
            .format(name),
             )


def valid_column_name(name):
    from django.core.exceptions import ValidationError
    pattern = r"^[A-Za-z0-9_]{1,63}$"
    if not re.search(pattern, name):
        raise ValidationError(
            'Invalid column name: {}, Must be alphanumeric, Max length: 63 Bytes'
            .format(name),
             )


class CSVUpload(models.Model):
    user = models.ForeignKey(Profile, blank=False, null=True)
    csv_file_name = models.CharField(max_length=63, blank=False)
    csv_file = models.FileField(
        validators=[validate_file_extension],
        null=False,
        blank=False,
        max_length=500)
    uploaded_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    lon_field_name = models.CharField(max_length=55, blank=False, validators=[valid_column_name])
    lat_field_name = models.CharField(max_length=55, blank=False, validators=[valid_column_name])
    wkt_field_name = models.CharField(max_length=55, blank=False, null=True, validators=[valid_column_name])
    geometry_type = models.CharField(
        max_length=55,
        blank=False,
        choices=GeometryTypeChoices.get_choices(),
        null=True,
    )
    the_geom_field_name = models.CharField(max_length=55, blank=False, null=True,)
    srs = models.CharField(max_length=30, blank=False, default='WGS84')
    features_count = models.IntegerField(blank=False, default=0)
    # text field as JSON to store dynamic field names for a CSV
    fields_names = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.csv_name

    def __unicode__(self):
        return self.csv_name

    class Meta:
        ordering = ['-uploaded_at']
        permissions = CSV_FILE_PERMISSIONS

    @property
    def csv_name(self):
        return os.path.basename(self.csv_file.name)
