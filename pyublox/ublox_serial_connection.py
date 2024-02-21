"""
author: Xuanpeng Zhao
Date: Feb 07 2024 
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
        self.__recv_data = None
        self.__buffer = bytearray()
        

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
                    byte = self.__serial_conn.read(1)
                    if byte is None:
                        continue
                    self.__buffer += byte
                    if len(self.__buffer) > 1 and (self.__buffer[-2:] == b'\xb5\x62' or self.__buffer[-2:] == b'$G'):
                        # Process the current packet, excluding the last 2 bytes
                        self.__recv_data = self.__buffer[:-2]
                        if self.__recv_data_callback:
                            self.__recv_data_callback(self.__recv_data)
                        # Start new buffer with the beginning of the next packet
                        self.__buffer = self.__buffer[-2:]
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