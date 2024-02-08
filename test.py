import time
from pyublox.ublox_serial_connection import UBloxSerialConnection
from pyublox.ubx_decoder import UBXDecoder
from pyublox.nmea_reader import NMEAReader
from pyublox.ublox_constants import UbloxConst
from pyublox.ublox_utility import UbloxUtils
import base64

def main():
    # Replace with the actual serial port and baud rate
    device_port = "COM10"  # Example: "COM3" on Windows or "/dev/ttyUSB0" on Linux
    baud_rate = 38400

    # Replace with your device's vendor ID and product ID
    vendor_id = 0x1546  # Example Vendor ID
    product_id = 0x01a8  # Example Product ID

    device_port = UbloxUtils.find_usb_device(vendor_id, product_id)
    if device_port is None:
        print("Device not found")
        return
    
    # Initialize and connect UBloxSerialConnection
    ublox_connection = UBloxSerialConnection(device_port, baud_rate)
    ublox_connection.connect()

    ubx_decoder = UBXDecoder()
    nmea_reader = NMEAReader()

    try:
        while True:
            recv_data = ublox_connection.read()
            if recv_data:
                if recv_data[0] == UbloxConst.HEADER_NMEA:
                    nmea_reader.decode(recv_data)
                if (recv_data[0] << 8 | recv_data[1]) == UbloxConst.HEADER_UBX:
                    ubx_decoder.decode(recv_data)
                if nmea_reader.vtg.cog_mag:
                    print(nmea_reader.vtg.cog_mag) # heading
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
    main()
    #recv_data = b'\x24\x47\x4E\x47\x47\x41\x2C\x32\x32\x32\x34\x30\x34\x2E\x35'
    #recv_data = "$GPGGA,092725.00,4717.11399,N,00833.91590,E,1,08,1.01,499.6,M,48.0,M,,*5B\r\n"
    