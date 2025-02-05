from . import app, socketio
from .rtl_power_util import Wideband, data_queue
from .rtl_tcp_server import Server, Forward
from flask import render_template, request, jsonify, send_from_directory

import threading
import subprocess
import time


current_wideband = None
current_server = None

w_socket = None

@app.route('/')
@app.route('/index')
def index():
	return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@app.route('/rtl_data')
def rtl_data():

	return render_template('rtl_data.html')


@app.route("/start_scan", methods=["POST"])
def start_scan():

	global current_wideband

	data = request.json
	settings = data.get("rtlSettings")
	
	# Stop any running wideband instance
	if current_wideband:

		current_wideband.kill_all()
		current_wideband.stop_data_stream()
		current_wideband = None
		print("[!] Killed Wideband")

	if settings['ongoingScan'] is False:

		# socketio.start_background_task(send_wideband_data)

		current_wideband = Wideband(settings)
		current_wideband.async_stream_data()
		
	return jsonify({"status": "success"})


@app.route("/rtl_tcp_start", methods=["POST"])
def rtl_tcp_start():

	global current_server

	rtl_tcp_data = request.json
	tcp_settings = rtl_tcp_data.get("tcpSettings")

	if current_server:
		current_server.kill_all()
		current_server = None
		print("[*] Killed tcp server")

	if tcp_settings['activeTCPServer'] is False:
		current_server = Server(tcp_settings['rtlClientIP'], tcp_settings['rtlClientPort'])
		current_server.async_server_start()

		return jsonify({"status": "success"})

	else:
		return jsonify({"status": "tcp server not started!"})


@app.route("/rtl_tcp_frequency", methods=["POST"])
def rtl_tcp_frequency():

	if current_server:
		frequency_data = request.json
		set_frequency = frequency_data.get('currentTCPFreq')

		print(frequency_data)

		current_server.send_command(set_frequency)

		return jsonify({"status": "sucess"})

	else:
		return jsonify({"status": "no current server!"})
