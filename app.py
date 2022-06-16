'''
Name: Jaykumar Naik
ID: 1001865454
Assignment: 2
Web url: 
'''
import os
import shutil
import sys
from flask import Flask,render_template, url_for, flash, redirect, request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_bootstrap import Bootstrap
from wtforms import StringField, IntegerField, SubmitField, SelectField
# from wtforms.validators import DataRequired

from db import DB
from forms import SearchRangeForm, SearchNearestForm

app = Flask(__name__)
bootstrap = Bootstrap(app)
db = DB()

# Configurations
app.config['SECRET_KEY'] = 'blah blah blah blah'

class NameForm(FlaskForm):
	name = StringField('Name')
	submit = SubmitField('Submit')

# ROUTES!
@app.route('/',methods=['GET','POST'])
def index():
	form = NameForm()
	if form.validate_on_submit():
		name = form.name.data
		return render_template('index.html',form=form,name=name)
	return render_template('index.html',form=form,name=None)


@app.route('/eq', methods=['GET', 'POST'])
def eq():
	# Earthquake route to present form and search for warthquakes 
	# accordingly on the data hosted on sql cloud
	forms = [SearchRangeForm(), SearchNearestForm()]
	data = {}

	# Check for the range search form and query accorind to the data
	if request.method == 'POST' and request.form['submit'] == 'Submit_1' and forms[0].validate_on_submit():
		form = forms[0]
		mi = form.mi.data
		ma = form.ma.data
		metric = form.metric.data
		offset = form.offset.data

		db = DB()
		data['columns'], data['rows'] = db.query_range(mi, ma, metric, offset)
	# Check for the radius form and query accordingly
	elif request.method == 'POST' and request.form['submit'] == 'Submit_2' and forms[1].validate_on_submit():
		form = forms[1]
		lat = form.lat.data
		lon = form.lon.data
		radius = form.radius.data

		db = DB()
		data['columns'], data['rows'] = db.query_radius(lat, lon, radius)

	return render_template('eq.html',data=data, forms=forms, count=len(data.get('rows', [])))

@app.route('/cluster', methods=['GET', 'POST'])
def cluster():
	db = DB()
	data = dict()
	data['columns'], data['rows'] = db.query_cluster()
	# print(data['rows'])
	return render_template('eq.html', data=data)

###
@app.route('/help')
def help():
	text_list = []
	# Python Version
	text_list.append({
		'label':'Python Version',
		'value':str(sys.version)})
	# os.path.abspath(os.path.dirname(__file__))
	text_list.append({
		'label':'os.path.abspath(os.path.dirname(__file__))',
		'value':str(os.path.abspath(os.path.dirname(__file__)))
		})
	# OS Current Working Directory
	text_list.append({
		'label':'OS CWD',
		'value':str(os.getcwd())})
	# OS CWD Contents
	label = 'OS CWD Contents'
	value = ''
	text_list.append({
		'label':label,
		'value':value})
	return render_template('help.html',text_list=text_list,title='help')

@app.errorhandler(404)
@app.route("/error404")
def page_not_found(error):
	return render_template('404.html',title='404')

@app.errorhandler(500)
@app.route("/error500")
def requests_error(error):
	return render_template('500.html',title='500')

if os.environ.get('ENV') == 'local':
	port = int(os.getenv('PORT', '3000'))
	app.run(host='0.0.0.0', port=port, debug=True)
