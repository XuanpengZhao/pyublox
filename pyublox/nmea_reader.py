"""
author: Xuanpeng Zhao
Date: Feb 07 2024
Description: This script is designed to read NMEA messages
"""
from pyublox.ublox_utility import UbloxUtils
from pyublox.ublox_constants import UbloxConst

class NMEAReader:

    HEADER_NMEA = "$"
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

    def __init__(self):
        self.gga = self.GGA()
        self.vtg = self.VTG()

    def decode(self, recv_data):
        header = recv_data[0]
        talker_ID = recv_data[1:3]
        sentence_formatter = recv_data[3:6]
        if header == UbloxConst.HEADER_NMEA:
            decoded_data = recv_data.decode('utf-8')
            data_fields = decoded_data.split(",")
            if sentence_formatter == UbloxConst.SF_GGA:
                self.gga.decode(data_fields)
            if sentence_formatter == UbloxConst.SF_VTG:
                self.vtg.decode(data_fields)
        else:
            print("Wrong input for NMEA reader")

    class GGA:
        def __init__(self):
            self.time = None  # UTC time of the fix (hhmmss.ss format)
            self.lat = None  # Latitude (ddmm.mmmmm format)
            self.NS = None  # North/South indicator (N or S)
            self.lon = None  # Longitude (dddmm.mmmmm format)
            self.EW = None  # East/West indicator (E or W)
            self.quality = None  # Quality indicator for position fix
            self.numSV = None  # Number of satellites used
            self.HDOP = None  # Horizontal Dilution of Precision
            self.alt = None  # Altitude above mean sea level
            self.sep = None  # Geoid separation: difference between ellipsoid and mean sea level
            self.diffAge = None  # Age of differential corrections (null when DGPS is not used)
            self.diffStation = None  # ID of station providing differential corrections (null when DGPS is not used)
        def decode(self, data_fields):
            if len(data_fields) >= 14:
                self.time = UbloxUtils.convert_to_time(data_fields[1])
                self.NS = data_fields[3]
                self.lat = UbloxUtils.convert_to_decimal_degrees(data_fields[2], self.NS)
                self.EW = data_fields[5]
                self.lon = UbloxUtils.convert_to_decimal_degrees(data_fields[4], self.EW)
                self.quality = UbloxUtils.get_quality(data_fields[6])
                self.numSV = data_fields[7]
                self.HDOP = data_fields[8]
                self.alt = data_fields[9]
                self.sep = data_fields[11]
                self.diffAge = data_fields[13]
                self.diffStation = data_fields[14]
    class VTG:
        def __init__(self):
            self.cog_true = None  # Course over ground (true), in degrees
            self.cog_mag = None  # Course over ground (magnetic), in degrees
            self.sog_knots = None  # Speed over ground, in knots
            self.sog_kmh = None  # Speed over ground, in kilometers per hour
            self.pos_mode = None  # Mode indicator (available in NMEA 2.3 and later)
        def decode(self, data_fields):
            self.cog_true = data_fields[1]
            self.cog_mag = data_fields[3]
            self.sog_knots = data_fields[5]
            self.sog_kmh = data_fields[7]
            self.pos_mode = UbloxUtils.get_posMode(data_fields[9])


