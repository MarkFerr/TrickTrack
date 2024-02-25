import os
import bluetooth
import time
import board
import adafruit_icm20x
import json
import imufusion
import logging as log
import numpy as np
from datetime import datetime

import spelling

spelling.load_spellcheck_data()

server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
port = 1

server_socket.bind(("", port))
server_socket.listen(1)

print("Waiting for connection on RFCOMM channel", port)

client_socket, address = server_socket.accept()
print("Accepted connection from", address)



start_time = None
message_received = False
headder_received = False

i2c = board.I2C()
icm = adafruit_icm20x.ICM20948(i2c)

#ahrs = imufusion.Ahrs()

def getTrickFileName():
        # Get today's date
    #today_date = datetime.today().strftime('%Y-%m-%d')
    today_date = time.strftime('%Y-%m-%d', time.localtime())

    # Construct the filename with today's date
    filename = f"Recordings/{today_date}.txt"

    # Check if the file exists
    if not os.path.exists(filename):
        # Create the file
        with open(filename, 'w') as file:
            file.write(f"{today_date}.txt")

    return filename

def getSensorvalues():  #TODO make pickle/msgpack or json from data
    acc = icm.acceleration
    gro = icm.gyro
    mag = icm.magnetic
    values = np.array([acc,gro,mag])
    log.info("Sensor Values: ", values)
    return values

def wait_for_header():
    while True: #receiving messages
        try:
            print("waiting for Header")
            log.info("waiting for Header")
            received_data = client_socket.recv(1024)
            if not received_data:
                # Connection closed by the client
                break

            received_message = received_data.decode("utf-8")
            print("Received Header:", received_message)
            log.info("Received Header:", received_message)

            if received_message == "Start recording" and not message_received:
                print("Wrong data received. Waiting on Header but got Start command")
                log.info("Wrong data received. Waiting on Header but got Start command")

            if received_message[0] in ['0','1','2']:
                return received_message


        except Exception as e:
            print("Error:", e)
            break



sensor_data = np.array([])
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

        if received_message[0] in ['0','1','2']:
            print("Wrong data received. Waiting on Start command but got Header")
            log.info("Wrong data received. Waiting on Start command but got Header")

        if message_received:
            while True:
                current_time = time.time()
                elapsed_time = current_time - start_time

                if elapsed_time <= 5:
                    sensor_data = np.append(sensor_data, getSensorvalues())
                    print(str(len(sensor_data)))
                    print("Time: " + str(elapsed_time))
                    #json_data = json.dumps(sensor_data)
                    #client_socket.send(json_data.encode('utf-8'))
                    #client_socket.send("__eod")


                    time.sleep(.5)
                else:
                    client_socket.send("done__eod")
                    client_socket.send("Length = " + str(len(sensor_data)) + "\n")
                    client_socket.send("done__eod")

                    header = wait_for_header()
                    header = spelling.checkHeader(header)
                    #print(str(data))
                    #TODO get Trick & Make or not
                    #TODO write header to data (Date&Time, trick, make?)
                    with open(getTrickFileName(), 'a') as f:
                        f.write("[" + str(header) + "]," + str(sensor_data) + "\n")
                    sensor_data = np.array([])
                    message_received = False
                    break

    except Exception as e:
        print("Error:", e)
        client_socket.close()
        server_socket.close()
        #break
        server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        port = 1

        server_socket.bind(("", port))
        server_socket.listen(1)

        print("Waiting for connection on RFCOMM channel", port)

        client_socket, address = server_socket.accept()
        print("Accepted connection from", address)



client_socket.close()
server_socket.close()
