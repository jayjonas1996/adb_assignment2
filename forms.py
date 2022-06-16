from wtforms import StringField, IntegerField, SubmitField, FloatField, SelectField
from wtforms import validators
from flask_wtf import FlaskForm


class SearchRangeForm(FlaskForm):
    mi = FloatField('min', [validators.Optional()])
    ma = FloatField('max', [validators.Optional()])
    metric = SelectField('select one', choices=[('days', 'Days'), ('months', 'Months')])
    offset = IntegerField('offset', [validators.Optional()])
    submit = SubmitField('Submit_1', name='submit')

class SearchNearestForm(FlaskForm):
    lat = FloatField('Latitude', [validators.InputRequired()])
    lon = FloatField('Longitude', [validators.InputRequired()])
    radius = FloatField('Range (in KM)', [validators.InputRequired()])
    submit = SubmitField('Submit_2', name='submit')
