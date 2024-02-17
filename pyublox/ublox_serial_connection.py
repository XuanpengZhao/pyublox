"""
author: Xuanpeng Zhao
Date: Feb 07 2024lf.__password
Description: This script is designed to create serial connection to ubloxs
"""
import serial
import threading

class UBloxSerialConnection:
    def __init__(self, port, baud_rate=38400):
        self.__port = port
        self.__baud_rate = baud_rate
        self.__serial_conn = None
        self.__thread = None
        self.__running = False
        self.__recv_data_callback = None
        self.recv_data = None

    def connect(self):
        try:
            self.__serial_conn = serial.Serial(self.__port, self.__baud_rate)
            self.__running = True
            self.__thread = threading.Thread(target=self.__read)
            self.__thread.start()
            print("Connected to UBLOX on port", self.__port)
        except serial.SerialException as e:
            print("Error ublox serial connection: ", f"connect: {e}")
            self.__running = False

    def __read(self):
        while self.__running:
            if self.__serial_conn and self.__serial_conn.in_waiting > 0:
                try:
                    self.recv_data = self.__serial_conn.readline()
                    if self.__recv_data_callback:
                        self.__recv_data_callback(self)
                except serial.SerialException as e:
                    print("Error ublox serial connection: ", f"__read: {e}")
                    self.disconnect()

    def disconnect(self):
        self.__running = False
        if self.__thread:
            self.__thread.join()
        if self.__serial_conn:
            self.__serial_conn.close()

    def write(self, data):
        if self.__serial_conn and self.__serial_conn.is_open:
            try:
                self.__serial_conn.write(data.encode('utf-8'))
            except serial.SerialException as e:
                print("Error ublox serial connection: ", f"write: {e}")

    def set_callback(self, callback):
        self.__recv_data_callback = callback

# Example usage
if __name__ == "__main__":
    ublox_connection = UBloxSerialConnection("COM3", 9600)  # Replace COM3 with your port
    ublox_connection.connect()
    ublox_connection.disconnect()