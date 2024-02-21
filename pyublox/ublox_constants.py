"""
author: Xuanpeng Zhao
Date: Feb 08 2024
Description: This script is designed to store all ublox constants
"""

class UbloxConst:
    UBLOX_DEVICE = [
            (0x1546, 0x01a9), # ublox: F9R
            (0x1546, 0x01aa), # ublox: M8P
    ]
    # header
    HEADER_NMEA = b"$G"
    HEADER_UBX = b'\xb5\x62'
    # Talker ID
    TID_GPS_SBAS = b"GP"
    TID_GLONASS = b"GL"
    TID_Galileo = b"GA"
    TID_BeiDou = b"GB"
    TID_QZSS = b"GQ"
    TID_ANY = b"GN" # combine of any
    # Sentence Formatter
    SF_GGA = b"GGA" # Global positioning system fix data
    SF_VTG = b"VTG" # Course over ground and ground speed

    DENOM = 1024
    CLASS_ESF = 0x10
    ID_MEAS = 0x02
    ID_ALG = 0x14