"""
author: Xuanpeng Zhao
Date: Feb 07 2024
Description: This script is designed to read NMEA messages
"""

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
                self.time = NMEAReader.convert_to_utc(data_fields[1])
                self.NS = data_fields[3]
                self.lat = NMEAReader.convert_to_decimal_degrees(data_fields[2], self.NS)
                self.EW = data_fields[5]
                self.lon = NMEAReader.convert_to_decimal_degrees(data_fields[4], self.EW)
                self.quality = NMEAReader.get_quality_description(data_fields[6])
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
            self.cog_true = data_fields[3]
            

    def __init__(self):
        self.gga = self.GGA()
        self.vtg = self.VTG()

    def decode(self, recv_data):
        header = recv_data[0]
        talker_ID = recv_data[1:3]
        sentence_formatter = recv_data[3:6]
        if header == NMEAReader.HEADER_NMEA:
            decoded_data = recv_data.decode('utf-8')
            data_fields = decoded_data.split(",")
            if sentence_formatter == NMEAReader.SF_GGA:
                self.gga.decode(data_fields)
            if sentence_formatter == NMEAReader.SF_VTG:
                self.vtg.decode(data_fields)

    @staticmethod
    def convert_to_decimal_degrees(degrees_minutes, direction):
        degrees = int(degrees_minutes[:2])
        minutes = float(degrees_minutes[2:])
        decimal_degrees = degrees + minutes / 60
        if direction in ['S', 'W']:
            decimal_degrees *= -1
        return str(decimal_degrees)
    
    @staticmethod
    def convert_to_utc(time_str):
        if len(time_str) >= 6:
            hours = time_str[0:2]
            minutes = time_str[2:4]
            seconds = time_str[4:6]
            milliseconds = ''
            if '.' in time_str and len(time_str) > 6:
                milliseconds = time_str.split('.')[1]  # Extracting the part after the decimal
                milliseconds = milliseconds.ljust(3, '0')  # Padding with zeros if necessary
            return f"{hours}:{minutes}:{seconds}.{milliseconds}"
        else:
            return None
    
    @staticmethod
    def get_quality_description(quality):
        quality_descriptions = {
            0: "No fix",
            1: "2D",
            2: "3D",
            4: "RTK fixed",
            5: "RTK float",
            6: "DR fixed"
        }
        return quality_descriptions.get(int(quality), "Unknown quality")  # Returns 'Unknown quality' for undefined codes
