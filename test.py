import time
from pyublox.ubx_serial_connection import UBXSerialConnection
from pyublox.ubx_decoder import UBXDecoder
import base64

def main():
    # Replace with the actual serial port and baud rate
    serial_port = "COM10"  # Example: "COM3" on Windows or "/dev/ttyUSB0" on Linux
    baud_rate = 38400
    
    # Initialize and connect UBLOXSerialConnection
    ublox_connection = UBXSerialConnection(serial_port, baud_rate)
    ublox_connection.connect()

    ubx_decoder = UBXDecoder()

    try:
        while True:
            recv_data = ublox_connection.read()
            if recv_data:
                ubx_decoder.decode(recv_data)
                

            time.sleep(0.1)
           

    except KeyboardInterrupt:
        print("\nExiting due to keyboard interrupt")

    finally:
        ublox_connection.disconnect()

def convert_to_decimal_degrees(degrees_minutes, direction):
        degrees = int(degrees_minutes[:2])
        minutes = float(degrees_minutes[2:])
        decimal_degrees = degrees + minutes / 60
        if direction in ['S', 'W']:
            decimal_degrees *= -1
        return decimal_degrees

if __name__ == "__main__":
    #main()
    recv_data = b'\x24\x47\x4E\x47\x47\x41\x2C\x32\x32\x32\x34\x30\x34\x2E\x35'
    recv_data = "$GPGGA,092725.00,4717.11399,N,00833.91590,E,1,08,1.01,499.6,M,48.0,M,,*5B\r\n"
    # decoded_string = recv_data.decode('utf-8')
    recv_data = recv_data.split(",")
    print(recv_data[2])
    a = 4717.11399
    b = convert_to_decimal_degrees(recv_data[2], "N")
    print(b)