import time
from pyublox.ublox_serial_connection import UBloxSerialConnection
from pyublox.ubx_decoder import UBXDecoder
from pyublox.nmea_reader import NMEAReader
from pyublox.ublox_constants import UbloxConst
from pyublox.ublox_utility import UbloxUtils
from pyublox.ntrip_socket_connection import NTRIPClient
import configparser

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

    enable_RTK = True

    try:
        while True:
            ublox_connection.read()
            recv_data = ublox_connection.recv_data
            if recv_data:
                if recv_data[0] == UbloxConst.HEADER_NMEA:
                    nmea_reader.decode(recv_data)
                if (recv_data[0] << 8 | recv_data[1]) == UbloxConst.HEADER_UBX:
                    ubx_decoder.decode(recv_data)
                if nmea_reader.vtg.cog_mag:
                    print(nmea_reader.vtg.cog_mag) # heading


                # if enable_RTK and nmea_reader.gga.lat and nmea_reader.gga.lon:
                #     rtk_test(nmea_reader.gga.lat, nmea_reader.gga.lon)
            time.sleep(0.1)
           

    except KeyboardInterrupt:
        print("\nExiting due to keyboard interrupt")

    finally:
        ublox_connection.disconnect()

def rtk_test(my_lat, my_lon):

    # host, port, username, password, mountpoint
    credential = UbloxUtils.read_credentials(".\credentials.ini")
    ntrip_client = NTRIPClient(credential["host"], credential["port"], credential["username"], credential["password"])
    ntrip_client.connect(my_lat, my_lon)
    print(ntrip_client.ntrip_source)
    for i in range(10):
        ntrip_client.receive()
        print(str(ntrip_client.recv_data))
    # b'STR;7ODM_RTCM3;7ODM_RTCM3;RTCM 3.1;1004(1),1005(60),1007(60),1012(1),1033(60);2;GPS+GLO;UNAVCO;USA;34.12;-117.09;0;0;TRIMBLE NETR9;None;B;N;0;;\r\n

if __name__ == "__main__":
    #main()
    rtk_test(33.974584, -117.316830)

    # # recv_data = b"\xb5b\x10\x02\x1c\x00\xd0\xd8\x07\x00\x18\x20\x00\x00\x7c\x06\x00\x0e\xcb\xfe\xff\x0d\xac\xf9\xff\x05\x09\x0b\x00\x0c\xd0\xd8\x07\x00\xf2\xae"
    # recv_data = b"\xb5b\x10\x02\x18\x00\xd5\xd8\x07\x00\x18\x18\x00\x00\x4d\xfd\xff\x10\x45\x02\x00\x11\x1f\x28\x00\x12\xd5\xd8\x07\x00\xcc\xac"
    # ubx_decoder = UBXDecoder()
    # ubx_decoder.decode(recv_data)
    # print(ubx_decoder.meas.AccelZ)

    # #recv_data = b'\x24\x47\x4E\x47\x47\x41\x2C\x32\x32\x32\x34\x30\x34\x2E\x35'
    # #recv_data = "$GPGGA,092725.00,4717.11399,N,00833.91590,E,1,08,1.01,499.6,M,48.0,M,,*5B\r\n"
    