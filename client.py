import time
from pynvml import *
from flask import Flask, request, url_for, redirect, render_template
import requests
import color
app = Flask(__name__, template_folder='templates')

all_info = {}

# 客户端,只用来发送请求

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
                res = requests.post(url='http://'+ip+':29454/get_nvidia_info', headers=headers)
                if res.status_code != 200:
                    continue
                all_info[ip] = res.text
            except:
                pass
        time.sleep(1)

@app.route('/watch_nvidia_info', methods=['get'])
def watch_nvidia_info():
    return all_info

if __name__ == '__main__':
    t1 = threading.Thread(target=update_nvidia_info)
    t1.start()
    app.run(host='0.0.0.0', port=8000)