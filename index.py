from flask import Flask, render_template, request
from subprocess import Popen, PIPE, STDOUT
from threading import Thread
import re
import os
from moviepy.editor import VideoFileClip

app = Flask(__name__) # 初始化 Flask 類別成為 instance

@app.route('/', methods=['GET']) # 路由和處理函式配對
def index():
	if 'url' in request.args:
		url = request.args.get('url')
		return render_template('index.html', url=url)
	else:
		return render_template('index.html')

@app.route('/get_title', methods=['GET'])
def get_title():
	url = request.args.get('url')
	process = Popen('youtube-dl --get-id --get-title -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4 \"' + url + '\"', stdout=PIPE, stderr=STDOUT, shell=True, universal_newlines=True, encoding="utf-8")
	output = ''
	error = False
	while True:
		line = process.stdout.readline()
		if not line:
			break
		else:
			line = line.strip()
			r1 = re.search(r'ERROR:', line)
			r2 = re.search(r'WARNING:', line)
			if r2 is None:
				output += line + '<br>'
			if r1 is not None:
				error = True
	if error:
		output = 'error.<br>' + output
	return output

def download_thread(title, url):
	process = Popen('youtube-dl -o \"static/' + title + '.mp4\" -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4 ' + url, stdout=PIPE, stderr=STDOUT, shell=True, universal_newlines=True, encoding="utf-8")
	output = ''
	while True:
		line = process.stdout.readline()
		if not line:
			break
		else:
			line = line.strip()
			output += line + '<br>'
			reg = re.search(r'\[download\]\s+(\d+\.?\d*)%\sof', line)
			if reg is not None:
				percent = open('static/message/' + title + '.txt', 'w')
				print(reg.group(1), file=percent, end='')
				percent.close()
	f = open('static/message/' + title + '.txt', 'w')
	if os.path.isfile('static/' + title + '.mp4'):
		print('complete', file=f, end='<br>')
		clip = VideoFileClip('static/' + title + '.mp4')
		print('%d:%.2f' % (clip.duration//60, clip.duration % 60), file=f, end='')
	else:
		print('failed', file=f, end='')
	f.close()

@app.route('/download', methods=['GET'])
def download():
	title = request.args.get('title')
	url = request.args.get('url')
	thread = Thread(target=download_thread, args=(title, url))
	thread.start()
	return ''

def mp3cut_thread(title, start, end):
	process = Popen('ffmpeg -y -i \"static/' + title + '.mp4\" -ss ' + start + ' -to ' + end + ' \"static/' + title + '_mp3cut_' + start + '_' + end + '.mp3\"', stdout=PIPE, stderr=STDOUT, shell=True, universal_newlines=True, encoding="utf-8")
	output = ''
	while True:
		line = process.stdout.readline()
		if not line:
			break
		else:
			line = line.strip()
			output += line + '<br>'
			reg = re.search(r'time=(\d\d):(\d\d):(\d\d\.\d\d)\s', line.strip())
			if reg is not None:
				percent = (float(reg.group(1)) * 3600 + float(reg.group(2))
						   * 60 + float(reg.group(3))) * 100 / (float(end) - float(start))
				f = open('static/message/' + title + '_mp3cut_' + start + '_' + end + '.txt', 'w')
				if (percent >= 100):
					f.write('100')
				else:
					f.write('%.2f' % percent)
				f.close()
	f = open('static/message/' + title + '_mp3cut_' + start + '_' + end + '.txt', 'w')
	f.write('complete')
	f.close()

@app.route('/mp3cut', methods=['GET'])
def mp3cut():
	title = request.args.get('title')
	start = request.args.get('start')
	end = request.args.get('end')
	thread = Thread(target=mp3cut_thread, args=(title, start, end))
	thread.start()
	return ''

def mp4cut_thread(title, start, end):
	process = Popen('ffmpeg -y -i \"static/' + title + '.mp4\" -ss ' + start + ' -to ' + end + ' -acodec copy \"static/' + title + '_mp4cut_' + start + '_' + end + '.mp4\"', stdout=PIPE, stderr=STDOUT, shell=True, universal_newlines=True, encoding="utf-8")
	output = ''
	while True:
		line = process.stdout.readline()
		if not line:
			break
		else:
			line = line.strip()
			output += line + '<br>'
			reg = re.search(r'time=(\d\d):(\d\d):(\d\d\.\d\d)\s', line.strip())
			if reg is not None:
				percent = (float(reg.group(1)) * 3600 + float(reg.group(2))
						   * 60 + float(reg.group(3))) * 100 / (float(end) - float(start))
				f = open('static/message/' + title + '_mp4cut_' + start + '_' + end + '.txt', 'w')
				if (percent >= 100):
					f.write('100')
				else:
					f.write('%.2f' % percent)
				f.close()
	f = open('static/message/' + title + '_mp4cut_' + start + '_' + end + '.txt', 'w')
	f.write('complete')
	f.close()

@app.route('/mp4cut', methods=['GET'])
def mp4cut():
	title = request.args.get('title')
	start = request.args.get('start')
	end = request.args.get('end')
	thread = Thread(target=mp4cut_thread, args=(title, start, end))
	thread.start()
	return ''

if __name__ == '__main__': # 判斷自己執行非被當做引入的模組，因為 __name__ 這變數若被當做模組引入使用就不會是 __main__
	app.debug = True
	app.run()