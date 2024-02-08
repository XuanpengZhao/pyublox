"""
author: Xuanpeng Zhao
Date: Feb 07 2024
Description: This script is designed to create serial connection to ubloxs
"""
import serial
import threading

class UBloxSerialConnection:
    def __init__(self, port, baud_rate=38400):
        self.port = port
        self.baud_rate = baud_rate
        self.serial_conn = None
        self.read_thread = None
        self.running = False

    def connect(self):
        try:
            self.serial_conn = serial.Serial(self.port, self.baud_rate)
            self.running = True
            self.read_thread = threading.Thread(target=self.read)
            self.read_thread.start()
            print("Connected to UBLOX on port", self.port)
        except serial.SerialException as e:
            print("Error connecting to serial port:", e)
            self.running = False

    def read(self):
        if self.serial_conn and self.serial_conn.in_waiting > 0:
            try:
                #data = self.serial_conn.readline().decode('utf-8').rstrip()
                data = self.serial_conn.readline()
                return data
            except serial.SerialException as e:
                print("Error reading from serial port:", e)
                self.disconnect()
        return None

    def disconnect(self):
        self.running = False
        if self.read_thread:
            self.read_thread.join()
        if self.serial_conn:
            self.serial_conn.close()
            print("Disconnected from UBLOX")

    def write(self, data):
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.write(data.encode('utf-8'))
            except serial.SerialException as e:
                print("Error writing to serial port:", e)


# Example usage
if __name__ == "__main__":
    ublox_connection = UBloxSerialConnection("COM3", 9600)  # Replace COM3 with your port
    ublox_connection.connect()
    ublox_connection.disconnect()