# OttoHPRacingCar
Program code that can be used to control the Otto HP robot via WIFI

Upload the main.py file to your Otto robot (e.g., using Arduino Lab for MicroPython).

After powering on, the robot will create a Wi-Fi access point:

SSID: Otto_Robot
Password: none (open network)

Connect to this network and open your browser:

👉 http://192.168.4.1

🎮 Features

From the web interface you can:

Control the robot using a virtual joystick
Turn the lights on/off
Activate the buzzer
Enable Line Follower mode
Immediately stop the robot
🤖 Obstacle Detection

The robot includes a built-in obstacle detection system:

🔴 When approaching an obstacle → the top light flashes red
⛔ When very close → the robot automatically stops
Behavior by mode:
Line Follower mode
Robot will not move forward until the obstacle is removed
Manual control mode
Forward movement is blocked
You can still move backward using the joystick

**My 3D printable racing car model for HP Otto:**
👉 https://www.printables.com/model/1646795-otto-formula-racing-car-modular-chassis-for-hp-rob


**Otto HP racing car assembly instructions**
👉  https://www.youtube.com/watch?v=AATVmyTIUfo

**Otto HP robot racing car first race**
👉  https://www.youtube.com/watch?v=d6Y3AL3Ex9U
