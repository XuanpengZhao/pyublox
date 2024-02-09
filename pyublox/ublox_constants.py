"""
author: Xuanpeng Zhao
Date: Feb 08 2024
Description: This script is designed to store all ublox constants
"""

class UbloxConst:
    UBLOX_DEVICE = [
            (0x1546, 0x01a8), # ublox: F9R
            (0x1546, 0x01aa), # ublox: M8P
    ]
    # header
    HEADER_NMEA = "$"
    HEADER_UBX = 0xB562  
    # Talker ID
    TID_GPS_SBAS = "GP"
    TID_GLONASS = "GL"
    TID_Galileo = "GA"
    TID_BeiDou = "GB"
    TID_QZSS = "GQ"
    TID_ANY = "GN" # combine of any
    # Sentence Formatter
    SF_GGA = "GGA" # Global positioning system fix data
    SF_VTG = "VTG" # Course over ground and ground speed

    DENOM = 1024
    CLASS_ESF = 0x10
    ID_MEAS = 0x02
    ID_ALG = 0x14