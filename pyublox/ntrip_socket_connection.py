import socket
import base64
import threading
from pyublox.ublox_utility import UbloxUtils

class NTRIPSocketConnection:
    def __init__(self, host, port, username, password, ublox_connection, buffersize=65536, recv_data_callback=None):
        self.__host = host
        self.__port = port
        self.__username = username
        self.__password = password
        self.__buffersize = buffersize
        self.__socket = None
        self.__running = False
        self.__thread = None
        self.__recv_data_callback = recv_data_callback
        self.__ublox_connection = ublox_connection
        self.recv_data = None
        self.mountpoint = None # '7ODM_RTCM3'
        self.closest_ntrip_source = None
        self.ntrip_sources_list = None

    def connect(self):
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.connect((self.__host, self.__port))
            self.__running = True
            self.__send_auth_request()
            self.recv_data = self.__socket.recv(self.__buffersize)
            # b'ICY 200 OK\r\n\r\n'
            if (b"ICY 200 OK") in self.recv_data:
                self.__thread = threading.Thread(target=self.__read)
                self.__thread.start()
            else:
                print("Error NTRIP socket connection: ", "Failed to receive ICY 200 OK")
        except Exception as e:
            print("Error NTRIP socket connection: ", f"connect: {e}")
            self.__running = False

    def find_closest_ntrip_source(self, my_lat, my_lon):
        self.__get_ntrip_sources_list()
        closest_source = None
        min_distance = float('inf')
        for source in self.ntrip_sources_list:
            if source.startswith('STR;'):
                sourceInfo = source.split(';')
                if len(sourceInfo) > 11:
                    # ['STR', '7ODM_RTCM3', '7ODM_RTCM3', 'RTCM 3.1', '1004(1),1005(60),1007(60),1012(1),1033(60)', '2', 'GPS+GLO', 'UNAVCO', 'USA', '34.12', '-117.09', '0', '0', 'TRIMBLE NETR9', 'None',
                    source_lat = float(sourceInfo[9])
                    source_lon = float(sourceInfo[10])
                    distance = UbloxUtils.haversine(my_lat, my_lon, source_lat, source_lon)
                    if distance < min_distance:
                        min_distance = distance
                        closest_source = sourceInfo
        self.ntrip_source = closest_source
        self.mountpoint = self.ntrip_source[1]
        return self.ntrip_source
            
    def __get_ntrip_sources_list(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect((self.__host, self.__port))
        self.__running = True
        print("Get NTRIP sources list")
        request = (f"GET / HTTP/1.1\r\n"
                   f"User-Agent: NTRIP PythonClient/1.0\r\n"
                   f"Connection: close\r\n\r\n")
        self.__socket.sendall(request.encode())
        if self.__running and self.__socket:
            recv_data = self.__socket.recv(self.__buffersize)
            # b'SOURCETABLE 200 OK\r\nServer: NTRIP BKG Caster 2.0.45/2.0\r\nDate: Fri, 09 Feb 2024 22:56:27 GMT\r\nConnection: close\r\nContent-Type: text/plain\r\nContent-Length: 173416\r\n\r\n'
            if (b"SOURCETABLE 200 OK") in recv_data:
                recv_data = self.__socket.recv(self.__buffersize)
            else:
                print("Error NTRIP socket connection: ", "Failed to receive SOURCETABLE 200 OK")
        decoded_data = recv_data.decode('utf-8')
        self.ntrip_sources_list = decoded_data.split('\r\n')
        self.disconnect()

    def __send_auth_request(self):
        auth_token = base64.b64encode(f"{self.__username}:{self.__password}".encode()).decode()
        request = (f"GET /{self.mountpoint} HTTP/1.1\r\n"
                   f"User-Agent: NTRIP PythonClient/1.0\r\n"
                   f"Accept: */*\r\n"
                   f"Connection: close\r\n"
                   f"Ntrip-GGA: \r\n"
                   f"Authorization: Basic {auth_token}\r\n\r\n")
        self.__socket.sendall(request.encode())

    def __read(self):
        while self.__running:
            if self.__socket:
                try:
                    self.recv_data = self.__socket.recv(self.__buffersize)
                    self.__ublox_connection.write(self.recv_data)
                    if self.__recv_data_callback:
                        self.__recv_data_callback(self.recv_data)
                except Exception as e:
                    print("Error NTRIP socket connection: ", f"__read: {e}")
                    self.disconnect()

    def disconnect(self):
        self.__running = False
        if self.__socket:
            self.__socket.close()
            print("Disconnected from NTRIP caster.")
        if self.__thread:
            self.__thread.join()