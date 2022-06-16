from wtforms import StringField, IntegerField, SubmitField, FloatField, SelectField
from wtforms import validators
from flask_wtf import FlaskForm


class SearchRangeForm(FlaskForm):
    mi = IntegerField('min', [validators.InputRequired()])
    ma = IntegerField('max', [validators.InputRequired()])
    metric = SelectField('select one', choices=[('months', 'Months'), ('days', 'Days')])
    offset = IntegerField('offset', [validators.InputRequired()])
    submit = SubmitField('Submit_1', name='submit')

class SearchNearestForm(FlaskForm):
    lat = FloatField('Latitude', [validators.InputRequired()])
    lon = FloatField('Longitude', [validators.InputRequired()])
    radius = FloatField('Range (in KM)', [validators.InputRequired()])
    submit = SubmitField('Submit_2', name='submit')
