from enum import Enum


class GeometryTypeChoices(Enum):
    UNKNOWN = 'wkbUnknown'
    POINT = 'wkbPoint'
    LINE = 'wkbLineString'
    POLYGON = 'wkbPolygon'
    MULTIPOINT = 'wkbMultiPoint'
    MULTILINE = 'wkbMultiLineString'
    MULTIPOLYGON = 'wkbMultiPolygon'
    POINTXY = 'AS_XY'
    POINTYX = 'AS_YX'
    POINTXYZ = 'AS_XYZ'
    LINESTARTEND = 'start_end'

    @classmethod
    def get_choices(cls):
        return [(tag.name, tag.value) for tag in cls]
