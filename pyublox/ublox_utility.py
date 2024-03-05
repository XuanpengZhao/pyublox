"""
author: Xuanpeng Zhao
Date: Feb 08 2024
Description: This script is designed to create static utility functions for ubloxs
"""
import binascii
from datetime import time
import serial.tools.list_ports
import configparser
import math

class UbloxUtils:
    @staticmethod
    def convert_gps_to_decimal(degrees_minutes, direction):
        """
        Converts geographic coordinates from degrees and decimal minutes (DDMM.MMMMMM or DDDMM.MMMMMM) format 
        to decimal degrees format. This format is commonly used in GPS data.

        Args:
            degrees_minutes (str): The latitude (DDMM.MMMMMM) or longitude (DDDMM.MMMMMM) in degrees and decimal minutes format.
                                For example, '3723.465877' for latitude (37 degrees and 23.465877 minutes).
                                '12202.269578' for longitude (122 degrees and 02.269578 minutes).
            direction (str): One of 'N', 'S', 'E', 'W' indicating the hemisphere (North, South, East, West).

        Returns:
            str: The latitude or longitude in decimal degrees format as a string. 
                For southern and western coordinates, this is a negative value.
        """
        if not degrees_minutes:
            return None

        # Determine if it's latitude or longitude based on the direction
        if direction in ['N', 'S']:  # Latitude
            degrees_length = 2
        elif direction in ['E', 'W']:  # Longitude
            degrees_length = 3
        else:
            raise ValueError("Invalid direction. Must be one of 'N', 'S', 'E', 'W'.")

        degrees = int(degrees_minutes[:degrees_length])
        minutes = float(degrees_minutes[degrees_length:])

        decimal_degrees = degrees + minutes / 60

        if direction in ['S', 'W']:
            decimal_degrees *= -1

        return str(decimal_degrees)
    
    
    @staticmethod
    def convert_HHMMSSsss_to_time(time_str):
        """
        Converts a UTC time string into a datetime.time object. The input string
        should be in the format of 'HHMMSS.sss', where 'HH' is hours, 'MM' is minutes,
        'SS' is seconds, and 'sss' is milliseconds.

        Args:
            time_str (str): A time string in the format 'HHMMSS.sss'.

        Returns:
            datetime.time: A datetime.time object representing the input time. If the
                           input string is invalid, returns None.
        """
        if len(time_str) >= 6:
            hours = int(time_str[0:2])
            minutes = int(time_str[2:4])
            seconds = int(time_str[4:6])
            microseconds = 0

            if '.' in time_str and len(time_str) > 6:
                milliseconds = time_str.split('.')[1]
                milliseconds = milliseconds.ljust(3, '0')  # Padding with zeros if necessary
                microseconds = int(milliseconds) * 1000  # Convert milliseconds to microseconds

            return time(hour=hours, minute=minutes, second=seconds, microsecond=microseconds)
        else:
            return None
    
    @staticmethod
    def get_quality(quality):
        """
        Retrieves the description of the GPS quality indicator.

        Args:
            quality (str): A string representing the quality indicator, typically a single digit.

        Returns:
            str: A textual description of the GPS quality. Returns 'Unknown quality' for undefined codes.
        """
        quality_descriptions = {
            0: "No fix",
            1: "2D",
            2: "3D",
            4: "RTK fixed",
            5: "RTK float",
            6: "DR fixed"
        }
        return quality_descriptions.get(int(quality), "Unknown quality")  # Returns 'Unknown quality' for undefined codes
    
    @staticmethod
    def get_posMode(pos_mode):
        """
        Retrieves the description of the GPS position mode indicator.

        Args:
            pos_mode (str): A string representing the position mode indicator, typically a single character.

        Returns:
            str: A textual description of the GPS position mode. Returns 'Unknown mode' for undefined codes.
        """
        pos_mode_descriptions = {
            'N': "No fix",
            'E': "DR fixed",
            'A': "2D",
            'D': "3D",
            'F': "RTK float",
            'R': "RTK fixed"
        }
        return pos_mode_descriptions.get(pos_mode, "Unknown mode")

    @staticmethod
    def inverse_bytes_to_signed_decimal(bytes):
        """
        Converts a byte array into its signed decimal representation, with bytes in reverse order.

        Args:
            bytes (bytes): A byte array to be converted.

        Returns:
            int: The signed decimal representation of the reversed bytes.
        """
        # Calculate the bit length of the byte array
        bit_length = len(bytes) * 8

        # Convert bytes to an integer
        int_value = int(binascii.hexlify(bytes[::-1]).decode('utf-8'), 16)

        # Check if the highest bit (sign bit) is set
        if int_value & (1 << (bit_length - 1)):
            int_value -= 1 << bit_length

        return int_value
    
    @staticmethod
    def find_ublox_device(ublox_devices):
        """
        Searches connected USB devices and returns the port name of the device that matches the given vendor and product IDs.

        This method scans through all the USB devices currently connected to the system and looks for a device that has the specified vendor ID and product ID. If such a device is found, the method returns the name of the serial port to which the device is connected. If no matching device is found, it returns None.

        Args:
            vendor_id (int): The vendor ID of the USB device to search for.
            product_id (int): The product ID of the USB device to search for.

        Returns:
            str or None: The name of the serial port if a matching device is found, otherwise None.
        """
        for vendor_id, product_id in ublox_devices:
            ports = serial.tools.list_ports.comports()
            for port in ports:
                if port.vid == vendor_id and port.pid == product_id:
                    return port.device
        return None
    
    @staticmethod
    def ubx_checksum(recv_data):
        """
        Calculates the UBX checksum for a given message.

        Args:
            recv_data (bytes): The UBX message data including header and checksum. 
                               The checksum needs to be calculated on the payload, 
                               excluding the header and existing checksum bytes.

        Returns:
            bytes: A two-byte checksum calculated from the payload of the UBX message.
        """
        payload = recv_data[2:-2]
        CK_A = 0
        CK_B = 0
        for buffer in payload:
            CK_A = (CK_A + buffer) & 0xFF  # Ensure it stays within 8 bits
            CK_B = (CK_B + CK_A) & 0xFF  # Ensure it stays within 8 bits

        return bytes([CK_A, CK_B])
    
    @staticmethod
    def read_credentials(file_path):
        config = configparser.ConfigParser()
        config.read(file_path)

        return {
            'host': config['DEFAULT']['host'],
            'port': int(config['DEFAULT']['port']),
            'username': config['DEFAULT']['username'],
            'password': config['DEFAULT']['password'],
        }
    
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        """
        Calculate the great circle distance in kilometers between two points 
        on the earth (specified in decimal degrees)
        """
        # Convert decimal degrees to radians 
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a)) 
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles
        return c * r