"""
author: Xuanpeng Zhao
Date: Feb 08 2024
Description: This script is designed to create static utility functions for ubloxs
"""
import binascii
from datetime import time

class UbloxUtils:
    @staticmethod
    def convert_to_decimal_degrees(degrees_minutes, direction):
        """
        Converts geographic coordinates from degrees and decimal minutes (DDMM.MMMM) format 
        to decimal degrees format. This format is commonly used in GPS data.

        Args:
            degrees_minutes (str): The latitude or longitude in DDMM.MMMM format. 
                                For example, '4717.11399' represents 47 degrees and 17.11399 minutes.
            direction (str): One of 'N', 'S', 'E', 'W' indicating the hemisphere (North, South, East, West).

        Returns:
            str: The latitude or longitude in decimal degrees format as a string. 
                For southern and western coordinates, this is a negative value.
        """
        degrees = int(degrees_minutes[:2])
        minutes = float(degrees_minutes[2:])
        decimal_degrees = degrees + minutes / 60
        if direction in ['S', 'W']:
            decimal_degrees *= -1
        return str(decimal_degrees)
    
    @staticmethod
    def convert_to_time(time_str):
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
    def inverse_bytes_to_hex(bytes):
        """
        Converts a byte array into its hexadecimal string representation, with bytes in reverse order.

        Args:
            bytes (bytes): A byte array to be converted.

        Returns:
            str: The hexadecimal string representation of the reversed bytes.
        """
        return binascii.hexlify(bytes[::-1]).decode('utf-8')