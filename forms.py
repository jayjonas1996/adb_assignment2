from wtforms import StringField, IntegerField, SubmitField, FloatField, SelectField
from wtforms import validators
from flask_wtf import FlaskForm


class SearchRangeForm(FlaskForm):
    # WT form to search for earthwuakes by magnitude and time
    mi = FloatField('min', [validators.Optional()])
    ma = FloatField('max', [validators.Optional()])
    metric = SelectField('select one', choices=[('days', 'Days'), ('months', 'Months')])
    offset = IntegerField('offset', [validators.Optional()])
    submit = SubmitField('Submit_1', name='submit')

class SearchNearestForm(FlaskForm):
    # WT form for finding earthquakes in a particular radius of a given coordinate
    lat = FloatField('Latitude', [validators.InputRequired()])
    lon = FloatField('Longitude', [validators.InputRequired()])
    radius = FloatField('Range (in KM)', [validators.InputRequired()])
    submit = SubmitField('Submit_2', name='submit')

class SearchNearestWithMagRange(FlaskForm):
    # WT form for finding nearest earthquake from a location in a magnitude range
    mi = FloatField('min', [validators.Optional()])
    ma = FloatField('max', [validators.Optional()])
    lat = FloatField('Latitude', [validators.InputRequired()])
    lon = FloatField('Longitude', [validators.InputRequired()])
    submit = SubmitField('Submit_3', name='submit')

class ClusterForm(FlaskForm):
    # WT form for finding clusters in a bounding box of coordinates with interval for partitioning
    lat_from = FloatField('Latitude from', [validators.InputRequired()])
    lat_to = FloatField('Latitude to', [validators.InputRequired()])
    lon_from = FloatField('Longitude from', [validators.InputRequired()])
    lon_to = FloatField('longitude to', [validators.InputRequired()])
    interval = FloatField('Interval', [validators.InputRequired()])
    submit = SubmitField('Submit', name='submit')
