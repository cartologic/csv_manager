import os

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


class CSVUpload(models.Model):
    user = models.ForeignKey(Profile, blank=True, null=True)
    csv_file_name = models.CharField(max_length=63, blank=True)
    csv_file = models.FileField(
        validators=[validate_file_extension],
        null=False,
        blank=False,
        max_length=500)
    uploaded_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    lon_field_name = models.CharField(max_length=55, blank=True)
    lat_field_name = models.CharField(max_length=55, blank=True)
    wkt_field_name = models.CharField(max_length=55, blank=True)
    geometry_type = models.CharField(
        max_length=55,
        blank=True,
        choices=GeometryTypeChoices.get_choices(),
        default=GeometryTypeChoices.UNKNOWN.name
    )
    the_geom_field_name = models.CharField(max_length=55, blank=True)
    srs = models.CharField(max_length=30, blank=True, default='WGS84')
    features_count = models.IntegerField(blank=True, default=0)

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
