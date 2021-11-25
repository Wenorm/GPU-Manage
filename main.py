import json
import time

from pynvml import *
from flask import Flask, request, url_for, redirect, render_template
from datetime import timedelta
import os
import psutil
import copy
import socket
import requests

app = Flask(__name__, template_folder='templates')

all_info = {}

@app.after_request
def add_header(r):
    """
        Add headers to both force latest IE rendering engine or Chrome Frame,
        and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route('/get_nvidia_info', methods=['post'])
def get_nvidia_info():
    nvmlInit()
    deviceCount = nvmlDeviceGetCount()
    UNIT = 1024 * 1024
    gpus_info = []
    for i in range(deviceCount):
        dic = {}
        handle = nvmlDeviceGetHandleByIndex(i)
        info = nvmlDeviceGetMemoryInfo(handle)
        utilization = nvmlDeviceGetUtilizationRates(handle)
        proInfos = nvmlDeviceGetComputeRunningProcesses(handle)  # gpu上正在运行的所有进程信息
        dic['Id'] = i
        dic['Name'] = str(nvmlDeviceGetName(handle))
        dic['Temperature'] = nvmlDeviceGetTemperature(handle, 0)
        dic['GpuUtilization'] = utilization.gpu
        dic['MemoryUsed'] = info.used // UNIT
        dic['MemoryFree'] = info.free // UNIT
        dic['MemoryTotal'] = info.total // UNIT
        dic['User:Pid:Mem'] = []
        for proinfo in proInfos:
            pid = proinfo.pid
            user = psutil.Process(pid).username()
            memory = proinfo.usedGpuMemory//UNIT
            dic['User:Pid:Mem'].append("{}:{}:{}".format(user, pid, memory))
        dic['User:Pid:Mem'] = '\n'.join(dic['User:Pid:Mem'])

        gpus_info.append(copy.deepcopy(dic))
    nvmlShutdown()
    return json.dumps(gpus_info)

@app.route('/', methods=['get', 'post'])
def home():
    return render_template('index.html')

def update_nvidia_info():
    global all_info
    with open('iplist.txt', mode='r', encoding='utf-8')as f:
        ips = f.readlines()
    while True:
        headers = {'content-type': 'application/json'}
        for ip in ips:
            ip = ip.strip()
            try:
                res = requests.post(url='http://'+ip+':8000/get_nvidia_info', headers=headers)
                if res.status_code != 200:
                    continue
                all_info[ip] = res.text
            except:
                pass
        time.sleep(1)

@app.route('/watch_nvidia_info', methods=['get'])
def watch_nvidia_info():
    global all_info
    return all_info

if __name__ == '__main__':
    t1 = threading.Thread(target=update_nvidia_info)
    t1.start()
    app.run(host='0.0.0.0', port=8000)