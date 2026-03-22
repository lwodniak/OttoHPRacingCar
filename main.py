import network

import socket

import time

import machine

from machine import Pin, ADC

from ottomotor import OttoMotor

from ottobuzzer import OttoBuzzer

from ottoneopixel import OttoUltrasonic, OttoNeoPixel



led = Pin(2, Pin.OUT)

motor = OttoMotor(13, 14)

buzzer = OttoBuzzer(25)



ultrasonic = OttoUltrasonic(18, 19)



ring = OttoNeoPixel(4, 13) 



analog_l = ADC(Pin(32))

analog_r = ADC(Pin(33))



offset_l = 0

offset_r = 0



FWD_L, FWD_R = 109, 43

BACK_L, BACK_R = 43, 109

LEFT_L, LEFT_R = 60, 29

RIGHT_L, RIGHT_R = 127, 95



mode_line_follow = False

lights_on = False

current_action = "STOP"

joystick_y = 0



HTML = """<!DOCTYPE html>

<html lang="en">

<head>

  <meta charset="utf-8">

  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">

  <title>Otto RC Controller</title>

  <style>

    body { font-family: Arial, sans-serif; background: #111; color: white; text-align: center; margin: 0; padding: 20px; touch-action: none; user-select: none; -webkit-user-select: none; }

    h1 { margin-bottom: 20px; color: #fff; }

    .status { color: #bbb; margin-bottom: 30px; font-size: 20px; font-weight: bold; }

    

    .joystick-container { position: relative; width: 260px; height: 260px; background: rgba(255, 255, 255, 0.1); border-radius: 50%; margin: 0 auto 30px auto; box-shadow: inset 0 0 20px rgba(0,0,0,0.5); }

    .knob { position: absolute; width: 100px; height: 100px; background: #1f7a1f; border-radius: 50%; top: 80px; left: 80px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); pointer-events: none; }

    

    .btn-row { margin-bottom: 15px; }

    .extra-btn { border: none; color: white; font-size: 18px; font-weight: bold; padding: 15px 25px; margin: 0 5px; border-radius: 12px; cursor: pointer; min-width: 120px; }

    .extra-btn:active { opacity: 0.7; }

    

    .btn-horn { background: #444; }

    .btn-lights { background: #e6b800; }

    .btn-line { background: #008080; }

    .btn-stop { background: #a02020; width: 80%; max-width: 260px; margin-top: 10px; padding: 20px; font-size: 22px; }

  </style>

</head>

<body>

  <h1>Otto Controller</h1>

  

  <div class="status">Status: <span id="statusText" style="color: #4CAF50;">STOP</span></div>

  

  <div class="joystick-container" id="zone">

    <div class="knob" id="knob"></div>

  </div>



  <div class="btn-row">

      <button class="extra-btn btn-horn" onclick="sendCommand('/h')">HORN</button>

  </div>

  <div class="btn-row">

      <button class="extra-btn btn-lights" onclick="sendCommand('/lights')">LIGHTS</button>

      <button class="extra-btn btn-line" onclick="sendCommand('/line')">LINE MODE</button>

  </div>

  <div class="btn-row">

      <button class="extra-btn btn-stop" onclick="sendCommand('/stop_all')">EMERGENCY STOP</button>

  </div>



  <script>

    const zone = document.getElementById('zone');

    const knob = document.getElementById('knob');

    const statusText = document.getElementById('statusText');

    

    let active = false;

    let lastSendTime = 0;



    function sendCommand(cmd) {

      fetch(cmd)

        .then(response => response.text())

        .then(text => { 

            if (cmd === '/stop_all') statusText.innerText = 'STOP'; 

            else if (cmd === '/line') statusText.innerText = 'LINE FOLLOWER';

        })

        .catch(e => {});

    }



    function sendDrive(x, y) {

      let now = Date.now();

      if (now - lastSendTime > 100) {

        fetch(`/d?x=${Math.round(x)}&y=${Math.round(y)}`).catch(e => {});

        lastSendTime = now;

      }

    }



    function handleMove(e) {

      if (!active) return;

      e.preventDefault();

      

      const rect = zone.getBoundingClientRect();

      const centerX = rect.width / 2;

      const centerY = rect.height / 2;

      

      const clientX = e.touches ? e.touches[0].clientX : e.clientX;

      const clientY = e.touches ? e.touches[0].clientY : e.clientY;

      

      let dx = clientX - rect.left - centerX;

      let dy = clientY - rect.top - centerY;

      

      const distance = Math.sqrt(dx*dx + dy*dy);

      const maxDist = 80; 

      

      if (distance > maxDist) {

        dx = (dx / distance) * maxDist;

        dy = (dy / distance) * maxDist;

      }

      

      knob.style.transform = `translate(${dx}px, ${dy}px)`;

      

      let percentX = (dx / maxDist) * 100;

      let percentY = (-dy / maxDist) * 100;

      

      if (distance < 25) {

        statusText.innerText = 'STOP';

        sendDrive(0, 0);

      } else {

        statusText.innerText = 'DRIVING';

        sendDrive(percentX, percentY);

      }

    }



    function handleEnd(e) {

      active = false;

      knob.style.transform = `translate(0px, 0px)`;


      sendCommand('/js_stop'); 

      setTimeout(() => { sendCommand('/js_stop'); }, 150);

    }



    function handleStart(e) { active = true; handleMove(e); }



    zone.addEventListener('touchstart', handleStart, {passive: false});

    document.addEventListener('touchmove', handleMove, {passive: false});

    document.addEventListener('touchend', handleEnd);

    

    zone.addEventListener('mousedown', handleStart);

    document.addEventListener('mousemove', handleMove);

    document.addEventListener('mouseup', handleEnd);

  </script>

</body>

</html>

"""



def set_motor_frequency():

    motor.leftServo.freq(50)

    motor.rightServo.freq(50)



def stop_motors():

    set_motor_frequency()

    motor.leftServo.duty(0)

    motor.rightServo.duty(0)

    led.off()



def stop_all_actions():

    global mode_line_follow, current_action, joystick_y

    mode_line_follow = False

    current_action = "STOP"

    joystick_y = 0

    stop_motors()



def drive_forward():

    set_motor_frequency()

    motor.leftServo.duty(FWD_L + offset_l)

    motor.rightServo.duty(FWD_R + offset_r)

    led.on()



def drive_backward():

    set_motor_frequency()

    motor.leftServo.duty(BACK_L + offset_l)

    motor.rightServo.duty(BACK_R + offset_r)

    led.on()



def turn_left():

    set_motor_frequency()

    motor.leftServo.duty(LEFT_L + offset_l)

    motor.rightServo.duty(LEFT_R + offset_r)

    led.on()



def turn_right():

    set_motor_frequency()

    motor.leftServo.duty(RIGHT_L + offset_l)

    motor.rightServo.duty(RIGHT_R + offset_r)

    led.on()



def sound_horn():

    buzzer.playNote(523, 80)

    time.sleep(0.03)

    buzzer.playNote(659, 80)



def send_html_response(client, html_content):

    body = html_content.encode("utf-8")

    header = ("HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: %d\r\nConnection: close\r\n\r\n" % len(body))

    client.sendall(header.encode("utf-8"))

    client.sendall(body)



def send_text_response(client, text):

    body = text.encode("utf-8")

    header = ("HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: %d\r\nConnection: close\r\n\r\n" % len(body))

    client.sendall(header.encode("utf-8"))

    client.sendall(body)



def get_obstacle_distance():

    try:

        distance = ultrasonic.readultrasonicRGB(1)

        return distance if distance is not None else 999

    except:

        return 999



def run_line_following_logic():

    set_motor_frequency() 

    try:

        left_val = analog_l.read()

        right_val = analog_r.read()

        

        if left_val > 600:

            motor.leftServo.duty(64 + offset_l)

            motor.rightServo.duty(41 + offset_r)

        elif right_val > 600:

            motor.leftServo.duty(114 + offset_l)

            motor.rightServo.duty(90 + offset_r)

        else:

            motor.leftServo.duty(90 + offset_l)

            motor.rightServo.duty(64 + offset_r)

    except:

        pass



def handle_background_tasks():

    global current_action, mode_line_follow, lights_on, joystick_y

    distance = get_obstacle_distance()

    current_time = time.ticks_ms()



    if lights_on:

        ultrasonic.ultrasonicRGB1("ffffff", "ffffff")

    else:

        ultrasonic.clearultrasonicRGB()



    if distance <= 15:

        if current_action == "FWD" or (current_action == "JOYSTICK" and joystick_y > 0):

            stop_motors()

            current_action = "STOP"

            joystick_y = 0

        elif mode_line_follow:

            stop_motors() 

            

        ring.fillAllRGBRing("fe0000")

        

 

    elif 15 < distance <= 20:

        if (current_time // 200) % 2 == 0:

            ring.fillAllRGBRing("fe0000") 

        else:

            ring.clearRGB()

            

        if mode_line_follow:

            run_line_following_logic()

            

 

    else:

        ring.clearRGB() 

            

        if mode_line_follow:

            run_line_following_logic()


def drive_arcade(x, y):
    global current_action, mode_line_follow, joystick_y
    
   
    if mode_line_follow:
        return 

    joystick_y = y

    if abs(x) < 15 and abs(y) < 15:
        stop_motors()
        current_action = "STOP"
        return

    distance = get_obstacle_distance()
    if distance <= 15 and y > 0: 
        stop_motors()
        current_action = "STOP"
        return

    set_motor_frequency()
    
    left_speed = y + x
    right_speed = y - x
    
    SPEED_LIMIT = 0.75 
    left_speed = left_speed * SPEED_LIMIT
    right_speed = right_speed * SPEED_LIMIT
    
    left_speed = max(-100, min(100, left_speed))
    right_speed = max(-100, min(100, right_speed))

    duty_l = int(76 + (left_speed * 33 / 100)) + offset_l
    duty_r = int(76 - (right_speed * 33 / 100)) + offset_r

    motor.leftServo.duty(duty_l)
    motor.rightServo.duty(duty_r)
    led.on()
    current_action = "JOYSTICK"





def start_access_point():

    network.WLAN(network.STA_IF).active(False) 

    

    ap = network.WLAN(network.AP_IF)

    ap.active(True)

    try: 

        ap.config(essid="Otto_Robot")

    except: 

        ap.config(ssid="Otto_Robot")

        

    return ap





def run_server():

    global mode_line_follow, current_action, lights_on, joystick_y



    ap_interface = start_access_point()

    ip_address = ap_interface.ifconfig()[0]



    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try: 

        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    except: 

        pass

        

    server_socket.bind(('', 80))

    server_socket.listen(5)

    server_socket.settimeout(0.05) 



    print("Robot is ready at: http://%s" % ip_address)

    stop_all_actions()



    led_state = 0

    loop_counter = 0



    while True:

        handle_background_tasks() 

        

        loop_counter += 1

        if loop_counter % 20 == 0: 

            led_state = not led_state

            led.value(led_state)



        try:

            client, addr = server_socket.accept()

            client.settimeout(1.0)

            request = client.recv(1024)

            

            if not request:

                client.close()

                continue



            request_text = request.decode("utf-8").strip()

            if not request_text:

                continue



            first_line = request_text.split("\r\n")[0]

            parts = first_line.split(" ")

            path = parts[1] if len(parts) >= 2 else "/"



            if path == "/":

                send_html_response(client, HTML)

            else:

                response = "OK"

                

             

                if path == "/stop_all":

                    stop_all_actions()

                    response = "EMERGENCY STOP"

                elif path == "/js_stop":

                    if not mode_line_follow:

                        stop_motors()

                        current_action = "STOP"

                        joystick_y = 0

                    response = "JOYSTICK RELEASED"

                elif path == "/h":

                    sound_horn()

                    response = "HORN"

                elif path == "/line":

                    mode_line_follow = True

                    current_action = "LINE"

                    response = "LINE MODE ACTIVE"

                elif path == "/lights":

                    lights_on = not lights_on

                    response = "LIGHTS TOGGLED"

                

                

                elif path.startswith("/d?"):

                    x, y = 0, 0

                    try:

                        params = path.split("?")[1].split("&")

                        for p in params:

                            k, v = p.split("=")

                            if k == 'x': x = int(v)

                            if k == 'y': y = int(v)

                    except Exception: 

                        pass

                    

                    if not mode_line_follow:

                        drive_arcade(x, y)

                        response = "DRIVING"

                    else:

                        response = "LOCKED (LINE MODE)"

                

                send_text_response(client, response)

                

            client.close()

            

        except OSError:

            pass 

        except Exception as e:

            try: client.close()

            except: pass



run_server()

