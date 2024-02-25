'''
import bluetooth
import time
import board
import adafruit_icm20x
import json
import imufusion
import numpy as np

server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
port = 1

server_socket.bind(("", port))
server_socket.listen(1)

print("Waiting for connection on RFCOMM channel", port)

client_socket, address = server_socket.accept()
print("Accepted connection from", address)

start_time = None
message_received = False

i2c = board.I2C()
icm = adafruit_icm20x.ICM20948(i2c)

ahrs = imufusion.Ahrs()

def getSensorvalues():  #TODO make pickle/msgpack or json from data
    acc = icm.acceleration
    gro = icm.gyro
    mag = icm.magnetic
    #acc = tuple(round(value, 2) for value in acc)
    #gro = tuple(round(value, 2) for value in gro)
    #mag = tuple(round(value, 2) for value in mag)
    ahrs.update_no_magnetometer(np.array(gro),np.array(acc), 1/100)
    euler = ahrs.quaternion.to_euler()
    rounded_euler = tuple(float(round(value, 2)) for value in euler)
    return rounded_euler
    #ONTO something here!!! TODO check orientation with Anroid app!!!

while True: #receiving messages
    try:
        print("waiting for message")
        received_data = client_socket.recv(1024)
        if not received_data:
            # Connection closed by the client
            break

        received_message = received_data.decode("utf-8")
        print("Received message:", received_message)

        if received_message == "Start recording" and not message_received:
            start_time = time.time()
            message_received = True
            data = []

        if message_received:
            while True:
                current_time = time.time()
                elapsed_time = current_time - start_time

                if elapsed_time <= 1000:
                    sensor_data = getSensorvalues()
                    json_data = json.dumps(sensor_data)
                    client_socket.send(json_data.encode('utf-8'))
                    client_socket.send("__eod")


                    time.sleep(.05)
                else:
                    client_socket.send("done__eod")
                    client_socket.send("Length = " + str(len(data)) + "\n")
                    print(str(data))
                    message_received = False
                    break

    except Exception as e:
        print("Error:", e)
        break

client_socket.close()
server_socket.close()

'''
print("HI")
