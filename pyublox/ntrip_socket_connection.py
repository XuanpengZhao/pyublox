import socket
import base64
import threading
from pyublox.ublox_utility import UbloxUtils

class NTRIPClient:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.mountpoint = '7ODM_RTCM3'
        self.socket = None
        self.running = False
        self.thread = None
        self.recv_data = None
        self.ntrip_source = None

    def connect(self, my_lat, my_lon):
        try:
            self.find_closest_ntrip_source(my_lat, my_lon)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.running = True
            self.thread = threading.Thread(target=self.receive)
            self.thread.start()
            self.send_auth_request()
        except Exception as e:
            print(f"Error connecting to NTRIP caster: {e}")
            self.running = False

    def find_closest_ntrip_source(self, my_lat, my_lon):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.running = True
        self.thread = threading.Thread(target=self.receive)
        self.thread.start()
        print("Connected to NTRIP caster.")
        self.get_source_list()
        self.receive()
        closest_source = None
        min_distance = float('inf')
        decoded_data = self.recv_data.decode('utf-8')
        ntrip_sources = decoded_data.split('\r\n')
        for source in ntrip_sources:
            if source.startswith('STR;'):
                sourceInfo = source.split(';')
                if len(sourceInfo) > 11:
                    source_lat = float(sourceInfo[9])
                    source_lon = float(sourceInfo[10])
                    distance = UbloxUtils.haversine(my_lat, my_lon, source_lat, source_lon)
                    if distance < min_distance:
                        min_distance = distance
                        closest_source = sourceInfo
        self.ntrip_source = closest_source
        self.mountpoint = self.ntrip_source[1]
        self.disconnect()
            
    def get_source_list(self):
        request = (f"GET / HTTP/1.1\r\n"
                   f"User-Agent: NTRIP PythonClient/1.0\r\n"
                   f"Connection: close\r\n\r\n")
        self.socket.sendall(request.encode())

    def send_auth_request(self):
        auth_token = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        request = (f"GET /{self.mountpoint} HTTP/1.1\r\n"
                   f"User-Agent: NTRIP PythonClient/1.0\r\n"
                   f"Accept: */*\r\n"
                   f"Connection: close\r\n"
                   f"Ntrip-GGA: \r\n"
                   f"Authorization: Basic {auth_token}\r\n\r\n")
        self.socket.sendall(request.encode())

    def receive(self):
        if self.running and self.socket:
            try:
                self.recv_data = self.socket.recv(4096)  # Adjust buffer size as needed
            except Exception as e:
                print(f"Error receiving data: {e}")
                self.disconnect()

    def disconnect(self):
        self.running = False
        if self.socket:
            self.socket.close()
            print("Disconnected from NTRIP caster.")
        if self.thread:
            self.thread.join()