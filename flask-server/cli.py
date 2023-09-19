import time
import hashlib
import requests
from fabric import Connection


def ssh(printer, ssh_password):
    c = Connection(printer.ip_address, user="root",
                   connect_kwargs={"password": ssh_password})
    return c


def ssh_upload(connection, file_path):
    connection.put(file_path, preserve_mode=False)
    connection.close()


def del_all(printer, connection):
    if printer.get_current_job()["job_status"] != "paused" or printer.get_current_job()["job_status"] != "running":
        connection.run("rm *.gcode *.data")
        connection.close()
        return 1
    else:
        raise Exception("Unable to delete, the printer is running")


def ask(printer, path, params):
    URL = f"http://{printer.ip_address}:10800/v1{path}"
    req = requests.get(url=URL, params=params)
    if req.status_code == 401:
        printer.token = printer.token_gen()
        URL = f"http://{printer.ip_address}:10800/v1{path}"
        req2 = requests.get(url=URL, params=params)
        if req2.status_code == 401:
            raise Exception("Error 10000, sign error or password error")
        else:
            return req2.json()
    elif not req.ok:
        raise req.raise_for_status()
    else:
        return req.json()


def order(printer, path, params, json=None, files=None):
    URL = f"http://{printer.ip_address}:10800/v1{path}"
    req = requests.post(url=URL, params=params, json=json, files=files)
    if req.status_code == 401:
        printer.token = printer.token_gen()
        URL = f"http://{printer.ip_address}:10800/v1{path}"
        req2 = requests.get(url=URL, params=params)
        if req2.status_code == 401:
            raise Exception("Error 10000, sign error or password error")
        else:
            return req2.json()
    elif not req.ok:
        raise req.raise_for_status()
    else:
        return req.json()


class Nozzle:
    def __init__(self, printer, nozzle):
        self.refresh(self, printer, nozzle)

    def refresh(self, printer, nozzle):
        response = ask(
            printer, f"/printer/nozzle{1 if nozzle == 0 else 2}", {"token": printer.token})
        self.flow_current, self.flow_target, self.temp_current, self.temp_target = response["data"].values(
        )


class Printer:
    password = ""
    ip_address = ""

    nozzle = 0  # left - 0, right - 1

    def __init__(self, ip, password):
        self.password = str(password)
        self.ip_address = ip
        self.token = self.token_gen()
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
        token_get = ask(self, "/login",
                        {"sign": hash, "timestamp": timestamp})
        if token_get["status"] == 1:
            return token_get["data"]["token"]
        else:
            raise Exception(
                f'Error {token_get["error"]["code"]}, {token_get["error"]["msg"]}')

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

    def axis_control(self, is_relative: int, feed=None, x=None, y=None, z=None, nozzle=None, e=None):
        changes = locals()
        changes.pop("self")
        changes2 = {key: val for key, val in changes.items() if val != None}
        return order(self, "/printer/axiscontrol/set", {"token": self.token}, changes2)

    def current_job(self):
        response = ask(self, "/job/currentjob", {"token": self.token})
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
