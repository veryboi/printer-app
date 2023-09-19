from flask import Flask, request, Response, send_file, jsonify
import time
from datetime import datetime, timedelta
import hashlib
import requests
import os
import math
import shutil
from werkzeug.utils import secure_filename
from fabric import Connection


# start w func definitions
# private

class Nozzle:
    def __init__(self, printer, nozzle):
        self.refresh(self, printer, nozzle)

    def refresh(self, printer, nozzle):
        response = ask(
            printer, f"/printer/nozzle{1 if nozzle == 0 else 2}", {"token": printer.token}).json()
        self.flow_current, self.flow_target, self.temp_current, self.temp_target = response["data"].values(
        )


class Printer:
    password = ""
    ip_address = ""

    nozzle = 0  # left - 0, right - 1

    def __init__(self, ip, password):
        self.password = str(password)
        self.ip_address = ip
        self.token_gen()
        try:
            self.left = Nozzle(self, 0)
        except:
            pass
        try:
            self.right = Nozzle(self, 1)
        except:
            pass
        self.printer_system_info()
        self.camera()
        self.printer_basic()
        self.printer_status()

    def printer_system_info(self):
        response = ask(self, "/printer/system", {"token": self.token})
        self.serial_number, self.api_version, self.battery, self.brightness, self.date_time, self.firmware_version, self.language, self.machine_id, self.machine_ip, self.machine_name, self.model, self.nozzies_num, self.storage_available, self.update, self.version = response["data"].values(
        )
        return response

    def camera(self):
        response = ask(self, "/printer/camera", {"token": self.token})
        camera_connected = response["data"]["is_camera_connected"]
        if camera_connected:
            self.camera_username = response["data"]["user_name"]
            self.camera_password = response["data"]["password"]
            self.camera_uri = self.ip_address + \
                response["data"]["camerserver_URI"]
        else:
            self.camera_username, self.camera_uri, self.camera_password = None
        return response

    def printer_basic(self):
        response = ask(self, "/printer/basic", {"token": self.token})
        self.fan_current, self.fan_target, self.feed_current, self.feed_target, self.bed_temp_current, self.bed_temp_target = response["data"].values(
        )
        return response

    def printer_status(self):
        response = ask(self, "/printer/runningstatus", {"token": self.token})
        self.running_status = response["data"]["running_status"]
        return response

    def token_gen(self):
        timestamp = int(time.time())
        hash = hashlib.sha1(
            f"password={self.password}&timestamp={timestamp}".encode()).hexdigest()
        hash = hashlib.md5(hash.encode()).hexdigest()

        URL = f"http://{self.ip_address}:10800/v1/login"
        req = requests.get(
            url=URL, params={"sign": hash, "timestamp": timestamp})

        token_get = req.json()
        if token_get["status"] == 1:
            self.token = token_get["data"]["token"]
            self.token_date = datetime.now()
            return True
        else:
            print(
                "error generating new token: " + f'Error {token_get["error"]["code"]}, {token_get["error"]["msg"]}')
            return False
            # raise Exception(
            #     f'Error {token_get["error"]["code"]}, {token_get["error"]["msg"]}')

    def set_left_nozzle_temp(self, temp):
        return order(self, "/printer/nozzle1/temp/set", {"token": self.token}, {"temperature": temp})

    def set_right_nozzle_temp(self, temp):
        return order(self, "/printer/nozzle2/temp/set", {"token": self.token}, {"temperature": temp})

    def set_left_nozzle_flow(self, flow):
        return order(self, "/printer/nozzle1/flowrate/set", {"token": self.token}, {"flowrate": flow})

    def set_right_nozzle_flow(self, flow):
        return order(self, "/printer/nozzle2/flowrate/set", {"token": self.token}, {"flowrate": flow})

    def set_bed_temp(self, temp):
        return order(self, "/printer/heatbedtemp/set", {"token": self.token}, {"temperature": temp})

    def set_feed_rate(self, rate):
        return order(self, "/printer/feedrate/set", {"token": self.token}, {"feedrate": rate})

    def set_fan_speed(self, speed):
        return order(self, "/printer/fanspeed/set", {"token": self.token}, {"fanspeed": speed})

    # def axis_control(self, is_relative: int, feed=None, x=None, y=None, z=None, nozzle=None, e=None):
    #     changes = locals()
    #     changes.pop("self")
    #     changes2 = {key: val for key, val in changes.items() if val != None}
    #     return order(self, "/printer/axiscontrol/set", {"token": self.token}, changes2)

    def current_job(self):
        response = ask(self, "/job/currentjob", {"token": self.token}).json()
        self.file_name, self.print_progress, self.printed_layer, self.printed_time, self.job_id, self.total_layer, self.total_time, self.job_status = response[
            "data"]
        return response

    def current_job_pause(self):
        return order(self, "/job/currentjob/set", {"token": self.token}, {"operate": "pause"})

    def current_job_resume(self):
        return order(self, "/job/currentjob/set", {"token": self.token}, {"operate": "resume"})

    def current_job_stop(self):
        return order(self, "/job/currentjob/set", {"token": self.token}, {"operate": "stop"})

    def new_job(self, file_path):
        return order(self, "/job/newjob/set", {"token": self.token}, {"file_path": file_path})

    def recover_last_job(self):
        return order(self, "/job/recover/set", {"token": self.token})


def ssh(printer_ip: str):
    for printer_obj in printers:
        if printer_obj.ip_address == printer_ip:

            c = Connection(printer_ip, user="root",
                           connect_kwargs={"password": printer_obj.password})
            return c
    return False


def ssh_upload(connection: Connection, file_path: str):
    connection.put(file_path, preserve_mode=False)
    connection.close()


# boolean return, so program will not stop running
def del_all(printer: Printer, connection: Connection):
    if printer.get_current_job()["job_status"] != "paused" and printer.get_current_job()["job_status"] != "running":
        connection.run("rm *.gcode *.data")
        connection.close()
        return True
    else:
        return False
        # raise Exception("Unable to delete, the printer is running")


def get_printer_by_ip(ip_addy: str) -> Printer:
    for printer_obj in printers:
        if printer_obj.ip_address == ip_addy:
            return printer_obj
    return False


def ask(printer: Printer, path: str, params, depth=0) -> requests.Response:
    if printer.token_date <= TOKEN_REFRESH_DELTA:
        printer.token_gen()

    URL = f"http://{printer.ip_address}:10800/v1{path}"
    req = requests.get(url=URL, params=params)
    if req.status_code == 401 and depth == 0:
        printer.token_gen()
        return ask(printer, path, params, 1)
    else:
        return req


def order(printer: Printer, path: str, params, json=None, files=None, depth=0) -> requests.Response:
    if printer.token_date <= TOKEN_REFRESH_DELTA:
        printer.token_gen()

    URL = f"http://{printer.ip_address}:10800/v1{path}"
    req = requests.post(url=URL, params=params, json=json, files=files)
    if req.status_code == 401 and depth == 0:
        printer.token_gen()
        return order(printer, path, params, json, files, 1)
    else:
        return req


# globals
printers = []  # could use pickle or json for data persistence

# file uploads

# configure this to the temp folder to handle file uploads
UPLOAD_FOLDER = "/Users/very/Documents/GitHub/printer-app/flask-server/uploads"

# token refresh time

TOKEN_REFRESH_DELTA = timedelta(hours=24)

# flask

api = Flask(__name__)


# API routes


# adds printer to server printer list
# param: {ip_address: string, password: string}

@api.route('/add_printer')
def add_printer():
    try:
        new_printer = Printer(request.args.get(
            "ip_address"), request.args.get("password"))
    except Exception as e:
        return Response("Error: " + str(e), 400)

    printers.append(new_printer)
    return Response("Printer created", 201)


# returns list of printers to display for main page
# param: none

@api.route('/all_printers')
def all_printers():
    response_list = []
    for printer_obj in printers:
        printer_obj.printer_status()  # keep status up to date
        response_list.append(
            {
                "name": printer_obj.machine_name,
                "ip_address": printer_obj.machine_ip,
                "status": printer_obj.running_status,
            }
        )
    return jsonify(results=response_list)


# returns information for a printer
# param: {ip_address: string}

@api.route('/get_printer')
def get_printer():
    pr_ip = request.args.get("ip_address")
    printer_obj = get_printer_by_ip(pr_ip)
    if printer_obj == False:
        return Response("Error: could not find selected printer", 400)
    response_body = {
        # misc info page
        "serial_number": printer_obj.serial_number,
        "api_version": printer_obj.api_version,
        "battery": printer_obj.battery,
        "brightness": printer_obj.brightness,
        "date_time": printer_obj.date_time,
        "firmware_version": printer_obj.firmware_version,
        "language": printer_obj.language,
        "machine_id": printer_obj.machine_id,
        "machine_ip": printer_obj.machine_ip,
        "machine_name": printer_obj.machine_name,
        "model": printer_obj.model,
        "nozzies_num": printer_obj.nozzies_num,
        "storage_available": printer_obj.storage_available,
        "update": printer_obj.update,
        "version": printer_obj.version,
        # main page
        "camera_uri": printer_obj.camera_uri,
        "camera_username": printer_obj.camera_username,
        "camera_password": printer_obj.camera_password,
        "fan_current": printer_obj.fan_current,
        "fan_target": printer_obj.fan_target,
        "feed_current": printer_obj.feed_current,
        "feed_target": printer_obj.feed_target,
        "bed_temp_current": printer_obj.bed_temp_current,
        "bed_temp_target": printer_obj.bed_temp_target,
        "running_status": printer_obj.running_status,
        "file_name": printer_obj.file_name,
        "print_progress": printer_obj.print_progress,
        "printed_layer": printer_obj.printed_layer,
        "total_layers": printer_obj.total_layers,
        "printed_time": printer_obj.printed_time,
        "total_time": printer_obj.total_time,
        "job_id": printer_obj.job_id,
        "job_status": printer_obj.job_status
    }
    return response_body


# uploads a file to a printer AND starts it
# param: { "ip_address": string }, file

@api.route('/upload')
def upload():
    # check if printer is running first
    try:
        printer_obj = get_printer_by_ip(request.args.get("ip_address"))
    except Exception as e:
        return Response("Error while getting printer: " + str(e), 400)

    if printer_obj.get_current_job()["job_status"] == "paused" or printer_obj.get_current_job()["job_status"] == "running":
        return Response("Printer is still running or paused, cannot upload and begin new job.", 400)

    try:  # clone file to server
        target = os.path.join(UPLOAD_FOLDER, 'upload' +
                              str(math.random(10000, 99999)))  # prevent dest collisions
        if not os.path.isdir(target):
            os.mkdir(target)

        file = request.files['file']
        print("uploading file " + file.filename)
        filename = secure_filename(file.filename)
        destination = "/".join([target, filename])
        file.save(destination)
    except Exception as e:
        return Response("Error while uploading file to server: " + str(e), 400)

    # ssh to printer
    try:
        printer_connection = ssh(request.args.get("ip_address"))
        if printer_connection == False:
            return Response("Error: Could not find printer with given ip.", 400)
    except Exception as e:
        return Response("Error while connecting to printer: " + str(e), 400)

    # empty printer directory, clone file to printer
    try:
        printer_connection.run("rm *.gcode *.data")
        ssh_upload(printer_connection, destination)
    except Exception as e:
        return Response("Error while uploading file from server to printer: " + str(e), 400)

    # delete temp folder
    shutil.rmtree(target)

    # begin task
    try:
        printer_obj.new_job(filename)
    except Exception as e:
        return Response("Error while initiating new job, " + str(e), 400)

    return Response("Success", 201)


# pauses current job of printer
# param: {ip_address: string}

@api.route('/pause_job')
def pause_job():
    try:
        printer_obj = get_printer_by_ip(request.args.get("ip_address"))
        if printer_obj == False:
            return Response("Could not find printer with given IP.", 400)

        resp = printer_obj.current_job_pause()

        return resp
    except Exception as e:
        return Response("Error: " + str(e), 400)


# resume current job of printer
# param: {ip_address: string}

@api.route('/resume_job')
def resume_job():
    try:
        printer_obj = get_printer_by_ip(request.args.get("ip_address"))
        if printer_obj == False:
            return Response("Could not find printer with given IP.", 400)

        resp = printer_obj.current_job_resume()

        return resp
    except Exception as e:
        return Response("Error: " + str(e), 400)


# stop current job of printer
# param: {ip_address: string}
@api.route('/stop_job')
def stop_job():
    try:
        printer_obj = get_printer_by_ip(request.args.get("ip_address"))
        if printer_obj == False:
            return Response("Could not find printer with given IP.", 400)

        resp = printer_obj.current_job_stop()

        return resp
    except Exception as e:
        return Response("Error: " + str(e), 400)


# sets nozzle temp
# param: {ip_address: string, nozzle_type: int: 0 (left), 1 (right), temperature: int}

@api.route('/set_nozzle_temp')
def set_nozzle_temp():
    try:
        printer_obj = get_printer_by_ip(request.args.get("ip_address"))
        if printer_obj == False:
            return Response("Could not find printer with given IP.", 400)
        if request.args.get("nozzle_type") == 0:
            return printer_obj.set_left_nozzle_temp(int(request.args.get("temperature")))
        else:
            return printer_obj.set_right_nozzle_temp(int(request.args.get("temperature")))
    except Exception as e:
        return Response("Error: " + str(e), 400)


# sets bed temp
# param: {ip_address: string, temperature: int}

@api.route('/set_bed_temp')
def set_bed_temp():
    try:
        printer_obj = get_printer_by_ip(request.args.get("ip_address"))
        if printer_obj == False:
            return Response("Could not find printer with given IP.", 400)
        return printer_obj.set_bed_temp(int(request.args.get("temperature")))
    except Exception as e:
        return Response("Error: " + str(e), 400)


# sets nozzle flow
# param: {ip_address: string, nozzle_type: int: 0 (left), 1 (right), flow: int}

@api.route('/set_nozzle_flow')
def set_nozzle_flow():
    try:
        printer_obj = get_printer_by_ip(request.args.get("ip_address"))
        if printer_obj == False:
            return Response("Could not find printer with given IP.", 400)
        if request.args.get("nozzle_type") == 0:
            return printer_obj.set_left_nozzle_flow(int(request.args.get("flow")))
        else:
            return printer_obj.set_right_nozzle_flow(int(request.args.get("flow")))
    except Exception as e:
        return Response("Error: " + str(e), 400)


# sets feed rate
# param: {ip_address: string, rate: int}

@api.route('/set_feed_rate')
def set_feed_rate():
    try:
        printer_obj = get_printer_by_ip(request.args.get("ip_address"))
        if printer_obj == False:
            return Response("Could not find printer with given IP.", 400)
        return printer_obj.set_feed_rate(int(request.args.get("rate")))
    except Exception as e:
        return Response("Error: " + str(e), 400)


# sets fan speed
# param: {ip_address: string, speed: int}

@api.route('/set_fan_speed')
def set_fan_speed():
    try:
        printer_obj = get_printer_by_ip(request.args.get("ip_address"))
        if printer_obj == False:
            return Response("Could not find printer with given IP.", 400)
        return printer_obj.set_fan_speed(int(request.args.get("speed")))
    except Exception as e:
        return Response("Error: " + str(e), 400)


if __name__ == "__main__":
    api.run()
