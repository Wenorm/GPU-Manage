import json
import time

from pynvml import *
from flask import Flask, request, url_for, redirect, render_template
from datetime import timedelta
import os
import psutil
import copy
app = Flask(__name__)

#服务端，只用来查询
@app.route('/get_nvidia_info', methods=['post'])
def get_nvidia_info():
    nvmlInit()
    deviceCount = nvmlDeviceGetCount()
    UNIT = 1024 * 1024
    gpus_info = []
    global colors
    for i in range(deviceCount):
        dic = {}
        handle = nvmlDeviceGetHandleByIndex(i)
        info = nvmlDeviceGetMemoryInfo(handle)
        utilization = nvmlDeviceGetUtilizationRates(handle)
        dic['Id'] = i
        dic['Name'] = str(nvmlDeviceGetName(handle))

        dic['Temperature'] = nvmlDeviceGetTemperature(handle, 0)
        dic['TemperatureRGB'] = colors[dic['Temperature']//10]

        dic['GpuUtilization'] = utilization.gpu
        dic['GpuUtilizationRGB'] = colors[dic['GpuUtilization']//10]

        dic['MemoryUsed'] = info.used // UNIT
        dic['MemoryFree'] = info.free // UNIT
        dic['MemoryTotal'] = info.total // UNIT

        dic['User:Pid:Mem'] = []
        proInfos = nvmlDeviceGetComputeRunningProcesses(handle)  # gpu上正在运行的所有进程信息
        for proinfo in proInfos:
            pid = proinfo.pid
            user = psutil.Process(pid).username()
            memory = proinfo.usedGpuMemory//UNIT
            dic['User:Pid:Mem'].append("{}:{}:{}".format(user, pid, memory))
        dic['User:Pid:Mem'] = '\n'.join(dic['User:Pid:Mem'])

        gpus_info.append(copy.deepcopy(dic))
    nvmlShutdown()
    return json.dumps(gpus_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=29454)
