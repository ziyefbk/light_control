import network
import socket
import machine
import neopixel
import time

# 1. 启动AP模式
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='ESP32_RGB', password='12345678')

# 2. 初始化三组neopixel灯带（每组12颗）
MAX_LED = 60
n1, n2, n3 = 12, 12, 12
l1, l2, l3 = 255, 255, 255
r1, g1, b1 = 0, 0, 0
r2, g2, b2 = 0, 0, 0
r3, g3, b3 = 0, 0, 0

np1 = neopixel.NeoPixel(machine.Pin(2), MAX_LED)
np2 = neopixel.NeoPixel(machine.Pin(4), MAX_LED)
np3 = neopixel.NeoPixel(machine.Pin(5), MAX_LED)

# 新增：初始化阀门IO口
neg_valve_pin = machine.Pin(12, machine.Pin.OUT)
valve1_pin = machine.Pin(13, machine.Pin.OUT)
valve2_pin = machine.Pin(14, machine.Pin.OUT)

# 初始状态全部关闭
neg_valve_pin.value(0)
valve1_pin.value(0)
valve2_pin.value(0)

def scale(val, lum):
    v = int(val * lum / 255)
    return v if v > 0 else (1 if val > 0 and lum > 0 else 0)

def web_page():
    with open('index.html') as f:
        return f.read()

# 4. 启动Web服务器
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

print('Web服务器已启动，手机连接WiFi后访问 http://192.168.4.1')

while True:
    conn, addr = s.accept()
    request = conn.recv(1024)
    request = request.decode('utf-8')
    try:
        if 'GET /?' in request:
            params = request.split('GET /?')[1].split(' ')[0]
            param_list = params.split('&')
            for p in param_list:
                if p.startswith('n1='): n1 = max(1, min(MAX_LED, int(p[3:])))
                if p.startswith('l1='): l1 = int(p[3:])
                if p.startswith('r1='): r1 = int(p[3:])
                if p.startswith('g1='): g1 = int(p[3:])
                if p.startswith('b1='): b1 = int(p[3:])
                if p.startswith('n2='): n2 = max(1, min(MAX_LED, int(p[3:])))
                if p.startswith('l2='): l2 = int(p[3:])
                if p.startswith('r2='): r2 = int(p[3:])
                if p.startswith('g2='): g2 = int(p[3:])
                if p.startswith('b2='): b2 = int(p[3:])
                if p.startswith('n3='): n3 = max(1, min(MAX_LED, int(p[3:])))
                if p.startswith('l3='): l3 = int(p[3:])
                if p.startswith('r3='): r3 = int(p[3:])
                if p.startswith('g3='): g3 = int(p[3:])
                if p.startswith('b3='): b3 = int(p[3:])
        # 新增：负压阀控制
        elif 'GET /neg-valve?' in request:
            # 例如 /neg-valve?open=1
            params = request.split('GET /neg-valve?')[1].split(' ')[0]
            open_val = 0
            if 'open=1' in params:
                open_val = 1
            neg_valve_pin.value(open_val)
            response = 'OK'
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/plain\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()
            continue
        # 新增：三通阀1控制
        elif 'GET /valve1?' in request:
            # 例如 /valve1?ch=A 或 /valve1?ch=B
            params = request.split('GET /valve1?')[1].split(' ')[0]
            ch = 'A' if 'ch=A' in params else 'B'
            valve1_pin.value(0 if ch=='A' else 1)
            response = 'OK'
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/plain\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()
            continue
        # 新增：三通阀2控制
        elif 'GET /valve2?' in request:
            params = request.split('GET /valve2?')[1].split(' ')[0]
            ch = 'A' if 'ch=A' in params else 'B'
            valve2_pin.value(0 if ch=='A' else 1)
            response = 'OK'
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/plain\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()
            continue
        # 先全部清零，再设置前n颗
        for i in range(MAX_LED):
            np1[i] = (0, 0, 0)
            np2[i] = (0, 0, 0)
            np3[i] = (0, 0, 0)
        for i in range(n1):
            np1[i] = (scale(r1, l1), scale(g1, l1), scale(b1, l1))
        for i in range(n2):
            np2[i] = (scale(r2, l2), scale(g2, l2), scale(b2, l2))
        for i in range(n3):
            np3[i] = (scale(r3, l3), scale(g3, l3), scale(b3, l3))
        np1.write()
        np2.write()
        np3.write()
    except Exception as e:
        print('参数解析或灯带设置出错:', e)
    response = web_page()
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close() 