'''
Name: Jaykumar Naik
ID: 1001865454
Assignment: 3 (quiz 3)
Web url: https://jkn-adb-a2.azurewebsites.net/quiz3
'''
import os, sys, timeit, random, json, urllib, re, string, time
from socket import socket
from collections import Counter
from flask import Flask, render_template, url_for, flash, redirect, request, make_response
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_bootstrap import Bootstrap
from wtforms import StringField, SubmitField
from flask_caching import Cache
from werkzeug import secure_filename

from dotenv import load_dotenv
import redis
import nltk
from azure.storage.blob import BlobServiceClient
from flask_socketio import SocketIO
from utils import append_room_id, list_rooms, r_set, r_get

from db import DB
from storage import CloudStorage, NLP
from forms import SearchRangeForm, SearchNearestForm, SearchNearestWithMagRange, ClusterForm, \
		BoundForm, NetMagRangeForm, DateForm, UpdateNetForm, VotesYearRangeForm, YearRangeForm, YearRangeNForm, \
			FruitsForm, FruitsBarForm, FruitsScatterForm, TextFileUpload, TextReplaceForm, CountStopwordsForm, \
				NameForm, QuestionForm, AnswerForm, GradeForm, HintForm, EndGameForm, CourseRegisterForm, CoursesForm, SetAgeForm

app = Flask(__name__)
bootstrap = Bootstrap(app)
load_dotenv('.env')
# socketio = SocketIO(app, cors_allowed_origins=["https://3000-jayjonas199-adbassignme-4lbv9t5nkbi.ws-us51.gitpod.io", "http://localhost:3000", "http://127.0.0.1:3000", "http://127.0.0.1:5000"])

r = redis.StrictRedis(host=os.environ.get('CACHE_REDIS_HOST'), password=os.environ.get('CACHE_REDIS_PASS'), ssl=True, db=0, decode_responses=True, port=6380)
nltk.download('punkt')

# Configurations
app.config['SECRET_KEY'] = 'blah blah blah blah'

# class NameForm(FlaskForm):
# 	name = StringField('Name')
# 	submit = SubmitField('Submit')

# ROUTES!
@app.route('/', methods=['GET','POST'])
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
	forms = [SearchRangeForm(), SearchNearestForm(), SearchNearestWithMagRange()]
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
	# Check for the nearest magnitude form and query the database accordingly
	elif request.method == 'POST' and request.form['submit'] == 'Submit_3' and forms[2].validate_on_submit():
		form = forms[2]
		lat = form.lat.data
		lon = form.lon.data
		mi = form.mi.data
		ma = form.ma.data

		db = DB()
		data['columns'], data['rows'] = db.query_nearest_mag(lat, lon, mi, ma)

	return render_template('eq.html',data=data, forms=forms, count=len(data.get('rows', [])))

@app.route('/quiz2', methods=['GET', 'POST'])
def quiz2():
	forms = [BoundForm(), NetMagRangeForm(), DateForm(), UpdateNetForm()]
	data = {}
	if request.method == 'POST' and request.form['submit'] == 'Submit_1' and forms[0].validate_on_submit():
		form = forms[0]
		lat_from = form.lat_from.data
		lat_to = form.lat_to.data
		lon_from = form.lon_from.data
		lon_to = form.lon_to.data

		db = DB()
		data['columns'], data['rows'] = db.query_bound(lat_from, lat_to, lon_from, lon_to)
	elif request.method == 'POST' and request.form['submit'] == 'Submit_2' and forms[1].validate_on_submit():
		form = forms[1]
		mi = form.mi.data
		ma = form.ma.data
		net = form.net.data

		db = DB()
		data['columns'], data['rows'] = db.query_net(net, mi, ma)		
	elif request.method == 'POST' and request.form['submit'] == 'Submit_3' and forms[2].validate_on_submit():
		form = forms[2]
		d = form.d.data

		db = DB()
		data['columns'], data['rows'] = db.query_date(d)
	
	elif request.method == 'POST' and request.form['submit'] == 'Submit_4' and forms[2].validate_on_submit():
		form = forms[3]
		net1 = form.net1.data
		net2 = form.net2.data

		db = DB(auto_close=False)
		data['columns'], data['rows'] = db.query_modify_net(net1, net2)
		db.close()
	
	return render_template('eq.html',data=data, forms=forms, count=len(data.get('rows', [])))

@app.route('/cluster', methods=['GET', 'POST'])
def cluster():
	data = {}
	form = ClusterForm()
	if form.validate_on_submit():
		db = DB()
		lat_from = form.lat_from.data
		lat_to = form.lat_to.data
		lon_from = form.lon_from.data
		lon_to = form.lon_to.data
		interval = form.interval.data
		
		data['columns'], data['rows'] = db.query_cluster(lat_from, lat_to, lon_from, lon_to, interval)
	
	return render_template('eq.html', data=data, forms=[form], count=len(data.get('rows', [])))

@app.route('/a3_a', methods=['POST', 'GET'])
def assignment3_a():
	db = DB(auto_close=False)
	time = 0
	for i in range(1000):
		mag = random.randint(0,9)
		# if r.exists(str(mag)):
			# result = r.get(str(mag))
		# else:
		start = timeit.default_timer()
		_, result = db.query_range(mi=mag, ma=None)
		time += round(timeit.default_timer() - start, 2)
		r.set(str(mag), '')
	db.close()
	return render_template('query_time.html', message=f'Executed 1000 queries in {time} seconds')

@app.route('/a3_b', methods=['POST', 'GET'])
def assignment3_b():
	db = DB(auto_close=False)
	time = 0
	for i in range(1000):
		mag = random.randint(0, 9)
		if r.exists(str(mag)):
			start = timeit.default_timer()
			result = r.get(str(mag))
			time += round(timeit.default_timer() - start, 2)
		else:
			start = timeit.default_timer()
			_, result = db.query_range(mi=mag, ma=None)
			time += round(timeit.default_timer() - start, 2)
			r.set(str(mag), '')
	db.close()
	return render_template('query_time.html', message=f'Executed 1000 queries in {time} seconds')

@app.route('/quiz3', methods=['GET', 'POST'])
def quiz3():
	db = DB(auto_close=False)
	data = dict()
	time, times = 0, 1
	forms = [VotesYearRangeForm(), YearRangeForm(), YearRangeNForm()]
	if request.method == 'POST' and request.form['submit'] == 'Submit_1' and forms[0].validate_on_submit():
		form = forms[0]
		y_min = form.year_min.data
		y_max = form.year_max.data
		v_min = form.votes_min.data
		v_max = form.votes_max.data
		times = form.times.data
		use_cache = form.use_cache.data
		if r.exists(f'1_{y_min}_{y_max}-{v_min}_{v_max}') and use_cache:
			data['columns'] = ['year', 'state', 'votes', 'party']
			for _ in range(times):
				start = timeit.default_timer()
				data['rows'] = json.loads(r.get(f'1_{y_min}_{y_max}-{v_min}_{v_max}'))
				time += round(timeit.default_timer() - start, 4)
		else:
			for _ in range(times):
				start = timeit.default_timer()
				data['columns'], data['rows'], data['rows2'] = db.query_votes(y_min, y_max, v_min, v_max)
				time += round(timeit.default_timer() - start, 4)
			r.set(f'1_{y_min}_{y_max}-{v_min}_{v_max}', json.dumps(data['rows']))
			db.close()

	elif request.method == 'POST' and request.form['submit'] == 'Submit_2' and forms[1].validate_on_submit():
		form = forms[1]
		y_min = form.year_min.data
		y_max = form.year_max.data
		times = form.times.data
		use_cache = form.use_cache.data
		if r.exists(f'2_{y_min}_{y_max}') and use_cache:
			data['columns'] = ['state', 'votes', 'party']
			for _ in range(times):
				start = timeit.default_timer()
				data['rows'] = json.loads(r.get(f'2_{y_min}_{y_max}'))
				time += round(timeit.default_timer() - start, 4)
		else:
			for _ in range(times):
				start = timeit.default_timer()
				data['columns'], data['rows'], data['rows2'] = db.query_votes(y_min, y_max)
				time += round(timeit.default_timer() - start, 4)
			r.set(f'2_{y_min}_{y_max}', json.dumps(data['rows']))
		db.close()
	
	elif request.method == 'POST' and request.form['submit'] == 'Submit_3' and forms[2].validate_on_submit():
		form = forms[2]
		y_min = form.year_min.data
		y_max = form.year_max.data
		times = form.times.data
		sample = form.sample.data
		use_cache = form.use_cache.data
		new_rows = []
		if r.exists(f'3_{y_min}_{y_max}_{sample}') and use_cache:
			for _ in range(times):
				start = timeit.default_timer()
				data['rows'] = json.loads(r.get(f'3_{y_min}_{y_max}_{sample}'))
				time += round(timeit.default_timer() - start, 4)
				for i in sorted(random.sample(range(len(data['rows'])), sample)):
					new_rows.append(data['rows'][i])
				data['rows'] = new_rows
		else:
			for _ in range(times):
				start = timeit.default_timer()
				data['columns'], data['rows'], data['rows2'] = db.query_votes(y_min, y_max)
				time += round(timeit.default_timer() - start, 4)
				for i in sorted(random.sample(range(len(data['rows'])), sample)):
					new_rows.append(data['rows'][i])
			r.set(f'3_{y_min}_{y_max}_{sample}', json.dumps(data['rows']))
			data['rows'] = new_rows
		db.close()

	return render_template('votes.html', data=data, forms=forms, count=len(data.get('rows', [])), message=f'Executed {times} times in {time}s')

@app.route('/graph', methods=['GET', 'POST'])
def assignment4():
	db = DB()
	data = db.short_query('''select case 
    when mag between 0 and 1 then '<1' 
    when mag between 1 and 2 then '1-2'
    when mag between 2 and 3 then '2-3'
    when mag between 3 and 4 then '3-4'
    when mag between 4 and 5 then '4-5'
	else 'else' end as 'magcat' from test0 where 'magcat' != 'else';''')
	data = Counter([x[0] for x in data])
	labels = [x[0] for x in data.items()][:-1]
	data   = [x[1] for x in data.items()][:-1]
	return render_template('graph.html', labels=labels, data=data)

@app.route('/graph_scatter', methods=['GET', 'POST'])
def assignment4_scatter():
	db = DB()
	data = db.short_query('''select mag, depth from test0 where DATEPART(year, time) = %d;''', 2022)
	data = [{'x': x[0], 'y': x[1]} for x in data]
	print(data)
	return render_template('graph_2.html', data=data)

@app.route('/fruits', methods=['GET', 'POST'])
def quiz4_1():
	forms = [FruitsForm(), FruitsBarForm(), FruitsScatterForm()]
	data = {'columns': [], 'rows': [], 'label': { 'x': 'Col 1', 'y': 'Col 3'}}
	db = DB()
	bar_type = ''
	colors = []
	extraLabels = False
	if request.method == 'POST' and request.form['submit'] == 'Submit_1' and forms[0].validate_on_submit():
		form = forms[0]
		n = form.n.data
		fruits = form.fruits.data.split(',')
		_, data['rows'] = db.query_n_fruits(fruits)
		data['columns'] = fruits
		data['rows'] = [x[0] for x in data['rows']]
		bar_type = 'pie'
		colors = ['rgb(255, 99, 132)', 'rgb(54, 162, 235)', 'rgb(255, 205, 86)']
	elif request.method == 'POST' and request.form['submit'] == 'Submit_2' and forms[1].validate_on_submit():
		form = forms[1]
		n = form.n.data
		_, data['rows'] = db.query_bar_fruits(n)
		data['columns'] = [x[0] for x in data['rows']]
		data['rows'] = [x[1] for x in data['rows']]
		print(data)
		bar_type = 'bar'
		colors = ['rgb(0,128,0)']
	elif request.method == 'POST' and request.form['submit'] == 'Submit_3' and forms[2].validate_on_submit():
		form = forms[2]
		low = form.low.data
		high = form.high.data
		_, data['rows'] = db.query_range_fruit(low, high)
		data['rows'] = [{'x': x[0], 'y': x[1]} for x in data['rows']]
		data['label'] = { 'x': 'Col 1', 'y': 'Col 3'}
		data['columns'] = ['col 1', 'col 3']
		bar_type = 'scatter'
		extraLabels = True
		colors = ['rgb(0,128,0)']

	return render_template('fruits.html', extraLabels=extraLabels, colors=colors, bar_type=bar_type, forms=forms, data=data)

@app.route('/assignment5', methods=['GET', 'POST'])
def assignment5():
	forms = [TextFileUpload()]
	if request.method == 'POST' and request.form['submit'] == 'Submit_1' and forms[0].validate_on_submit():
		cs = CloudStorage()
		form = forms[0]
		f = form.f.data

		for i in cs.list_b():
			cs.upload(f, f.filename)		
			with urllib.request.urlopen(CloudStorage.container + i['name']) as data:
				nlp = NLP()
				text = nlp.process(data)
				print(text)

	return render_template('text.html', forms=forms)

@app.route('/quiz5', methods=['GET', 'POST'])
def quizt5():
	data_1 = {}
	data_2 = {}
	forms = [TextFileUpload(), TextReplaceForm(), CountStopwordsForm()]
	if request.method == 'POST' and request.form['submit'] == 'Submit_1' and forms[0].validate_on_submit():
		cs = CloudStorage()
		form = forms[0]
		f = form.f.data
		n = form.n.data
		cs.upload(f, f.filename)

		for i in cs.list_b():	
			with urllib.request.urlopen(CloudStorage.container + i['name']) as text_file:
				nlp = NLP()
				text = nlp.process_quiz5(text_file)
				all_count = len(text.split())
				data_1['rows'] = []
				data_2['rows'] = []

				data_1['columns'] = ['words', 'count', '%']
				d = Counter(text.split())
				counts = []
				for k, v in d.items():
					counts.append((k, v))
				counts = sorted(counts, key=lambda x: x[1], reverse=True)
				for i in range(n):
					data_1['rows'].append([counts[i][0], counts[i][1], (counts[i][1] / all_count) * 100])
				
				data_2['columns'] = ['bigrams', 'count']
				d_2 = Counter([text[idx : idx + 2] for idx in range(len(text) - 1)])
				counts_2 = []
				for k, v in d_2.items():
					if ' ' not in k and len(k.strip()) == 2:
						counts_2.append((k, v))
				counts_2 = sorted(counts_2, key=lambda x: x[1], reverse=True)
				for i in range(n):
					data_2['rows'].append([counts_2[i][0], counts_2[i][1]])

	elif request.method == 'POST' and request.form['submit'] == 'Submit_2' and forms[1].validate_on_submit():
		cs = CloudStorage()
		form = forms[1]
		f = form.f.data
		find = form.find.data
		replace = form.replace.data
		cs.upload(f, f.filename)

		for i in cs.list_b():	
			with urllib.request.urlopen(CloudStorage.container + i['name']) as text_file:
				nlp = NLP()	
				i = 0
				data_1['columns'] = ['line']
				data_1['rows'] = []
				for text in nlp.process_quiz5_12(text_file):
					if text.strip():
						# print(re.sub(find, replace, text))
						data_1['rows'].append([re.sub(find, replace, text)])
						i += 1
					if i >= 5:
						break
	elif request.method == 'POST' and request.form['submit'] == 'Submit_3' and forms[2].validate_on_submit():
		cs = CloudStorage()
		form = forms[2]
		nlp = NLP()
		sw = nlp.stopwords()
		data_1['rows'] = []

		for i in cs.list_b():	
			with urllib.request.urlopen(CloudStorage.container + i['name']) as text_file:
				data_1['columns'] = ['Stop words', 'count']
				text = nlp.process_quiz5(text_file, stopwords=False)
				d = Counter(text.split())
				counts = []
				for k, v in d.items():
					counts.append((k, v))
				counts = sorted(counts, key=lambda x: x[1], reverse=True)
				for k,v in counts:
					if k in sw:
						data_1['rows'].append([k, v])

	
	return render_template('quiz5.html', forms=forms, data_1=data_1, data_2=data_2)

@app.route('/a7_teacher', methods=['GET', 'POST'])
def a7_teacher():
	forms = [NameForm(), QuestionForm(), GradeForm()]
	form = None
	data = { 'status': 'init' ,'active_index': 0, 't_name': '', 's_name': '', 
			'score': [], 'question': [], 'time_started': None, 'time_ended': None}
	if request.cookies.get('id') and r.exists(request.cookies.get('id')):
		data = json.loads(r.get(request.cookies.get('id')))
		append_room_id(r, request.cookies.get('id'))
		data = r_get(r, request.cookies.get('id'))
		if data['status'] in ['a', 'init']:
			form = forms[1]
		elif data['status'] in ['b', 'c']:
			form = forms[2]
	else:
		form = forms[0]
	
	if request.method == 'POST' and request.form['submit'] == 'Submit_1' and forms[0].validate_on_submit():
		form = forms[0]
		name = form.name.data
		data.update({'t_name': name, 'status': 'init'})
		r.set(request.cookies.get('id'), json.dumps(data))
		form = forms[1]
	elif request.method == 'POST' and request.form['submit'] == 'Submit_2' and forms[1].validate_on_submit():
		form = forms[1]
		question = form.question.data
		data.update({'question': data['question'] + [{ 'q': question, 'a': ''}], 'status': 'b'})
		r.set(request.cookies.get('id'), json.dumps(data))
		socketio.emit('student', data) # send student the new question
		socketio.emit('admin', data)
		form = forms[2]
	elif request.method == 'POST' and request.form['submit'] == 'Submit_3' and forms[2].validate_on_submit():
		form = forms[2]
		grade = form.grade.data
		data.update({'score': data['score'] + [grade], 'status': 'a'})
		r.set(request.cookies.get('id'), json.dumps(data))
		socketio.emit('student', data) # send student the new waiting for question
		socketio.emit('admin', data)
		form = forms[1]
	elif request.method == 'POST' and request.form['submit'] == 'end' and EndGameForm().validate_on_submit():
		id = request.args.get('id')
		data = r_get(r, id)
		data.update({'status': 'end', 'time_ended': int(time.time())})
	elif request.method == 'POST' and request.form['submit'] == 'end' and EndGameForm().validate_on_submit():
		id = request.cookies.get('id')
		data = r_get(r, id)
		data.update({'status': 'end', 'time_ended': int(time.time())})

	return render_template('assignment_7_teacher.html', form=form, data=data, end_form=EndGameForm())

@app.route('/a7_student', methods=['GET', 'POST'])
def a7_student():
	forms = [NameForm(), AnswerForm()]
	form = None
	rooms = None
	# data = json.loads(r.get(request.cookies.get('id')))
	if request.args.get('id') and request.method == 'GET':
		if r.exists(request.args.get('id')):
			data = r_get(r, request.args.get('id'))
			if data['status'] == ['init', 'half_init']:
				form = forms[0]
			else:
				form = forms[1]

	elif request.method == 'POST' and request.form['submit'] == 'Submit_1' and forms[0].validate_on_submit() and request.args.get('id'):
		form = forms[0]
		name = form.name.data
		id = request.args.get('id')
		data = r_get(r, id)
		data.update({'s_name': name, 'time_started': int(time.time()), 'status': 'a'})
		r_set(r, id, data)
		socketio.emit('teacher', data)
		socketio.emit('admin', data)
		form = forms[1]
	elif request.method == 'POST' and request.form['submit'] == 'Submit_2' and forms[1].validate_on_submit():
		form = forms[1]
		answer = form.answer.data
		id = request.args.get('id')
		data = r_get(r, id)
		data['question'][-1]['a'] = answer
		data.update({'status': 'c'})
		r_set(r, id, data)
		socketio.emit('teacher', data)
		socketio.emit('admin', data)
		form = forms[0]
	elif request.method == 'POST' and request.form['submit'] == 'end' and EndGameForm().validate_on_submit():
		id = request.args.get('id')
		data = r_get(r, id)
		data.update({'status': 'end', 'time_ended': int(time.time())})
	elif request.method == 'POST' and request.form['submit'] == 'end' and EndGameForm().validate_on_submit():
		id = request.args.get('id')
		data = r_get(r, id)
		data.update({'status': 'end', 'time_ended': int(time.time())})
	else:
		rooms = list_rooms(r)
	return render_template('assignment_7_student.html', rooms=rooms, form=form, end_form=EndGameForm())

@app.route('/a7_admin', methods=['GET', 'POST'])
def a7_admin():
	forms = [HintForm()]
	form = None
	rooms = None

	if request.method == 'GET':
		rooms = list_rooms(r)
	elif request.method == 'POST' and request.form['submit'] == 'end' and forms[0].validate_on_submit():
		form = forms[0]
		hint = form.hint.data
		socketio.emit('student', {'hint': hint})
	
	if request.args.get('id'):
		rooms = None
		form = forms[0]

	return render_template('assignment_7_admin.html', rooms=rooms, form=form, end_form=EndGameForm())

# if os.environ.get('TYPE') == 'STUDENT':
@app.route('/quiz6_student', methods=['GET', 'POST'])
def quiz6_student():
	db = DB(auto_close=False)
	data = {}
	forms = [CourseRegisterForm()]
	message = ""
	if request.method == 'POST' and request.form['submit'] == 'Submit_1' and forms[0].validate_on_submit():
		form = forms[0]
		student_id = form.id.data
		course_id = form.course_id.data
		section_id = form.section_id.data
		data['columns'], data['rows'], message = db.query_register(student_id, course_id, section_id, r)
		print(data, message)
	
	return render_template('quiz6_student.html', forms=forms, data=data, message=message)

# if os.environ.get('TYPE') == 'ADMIN':
@app.route('/quiz6_admin', methods=['GET', 'POST'])
def quiz6_admin():
	db = DB(auto_close=False)
	data = {}
	forms = [SetAgeForm(), CoursesForm()]
	message = ''
	if request.method == 'POST' and request.form['submit'] == 'Submit_1' and forms[0].validate_on_submit():
		form = forms[0]
		age = form.age.data
		r.set('age', int(age))
		message = f"SUCCESS: {age} is the new age limit"
	elif request.method == 'POST' and request.form['submit'] == 'Submit_2' and forms[1].validate_on_submit():
		form = forms[1]
		course_id = form.course_id.data
		section_id = form.section_id.data
		data['columns'], data['rows'] = db.query_registeration(course_id, section_id)

	return render_template('quiz6_student.html', forms=forms, data=data, message=message)


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


@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)

@socketio.on('teacher_emit_updates') # init
def teacher_emit_updates(data):
	if r.exists(data['room_id']):
		room_obj = r.get(data['room_id'])
		socketio.emit('teacher', json.loads(room_obj))
	else:
		init_obj = json.dumps({ 'status': 'half_init' ,'active_index': 0, 't_name': '', 's_name': '',
		'score': [], 'question': [], 'time_started': None, 'time_ended': None})
		r.set(data['room_id'], init_obj)
		socketio.emit('teacher', json.loads(r.get(data['room_id'])))


@socketio.on('req_data')
def request_data(data):
	print(data)
	if r.exists(data['room_id']):
		socketio.emit(data['requestor'], r_get(r, data['room_id']))


if os.environ.get('ENV') == 'local':
	r.set('age', 0)
	port = int(os.getenv('PORT', '3000'))
	# socketio.run(app, host='0.0.0.0', port=port, debug=True)
	# app.run(host='0.0.0.0', port=port, debug=True)
