"""
author: Xuanpeng Zhao
Date: Feb 07 2024
Description: This script is designed to decode UBX messages
"""
import binascii

class UBXDecoder:
    DENOM = 1024
    HEADER_UBX = 0xB562  
    CLASS_ESF = 0x10
    ID_MEAS = 0x02
    ID_ALG = 0x14

    class MEAS:
        def __init__(self):
            self.AccelX = None
            self.AccelY = None
            self.AccelZ = None
            self.GyroX = None
            self.GyroY = None
            self.GyroZ = None
        def decode(self, recv_data):
            # num_means is at recv_data[11] and only use the first 5 bits
            num_meas = (recv_data[11] & 0xF8) >> 3
            for i in range(num_meas):
                # data is composed of 4 bytes and first 3 is data field and last one is data type
                data = recv_data[6 + 8 + i * 4 : 6 + 8 + i * 4 + 4]
                data_field = int(UBXDecoder.inverse_bytes_to_hex(data[0:3]), 16)
                data_type = data[3] & 0x3F
                
                if data_type == 14:
                    self.GyroX = data_field / UBXDecoder.DENOM
                elif data_type == 13:
                    self.GyroY = data_field / UBXDecoder.DENOM
                elif data_type == 5:
                    self.GyroZ = data_field / UBXDecoder.DENOM
                elif data_type == 16:
                    self.AccelX = data_field / UBXDecoder.DENOM
                elif data_type == 17:
                    self.AccelY = data_field / UBXDecoder.DENOM
                elif data_type == 18:
                    self.AccelZ = data_field / UBXDecoder.DENOM
                elif data_type == 0:
                    print("UBX Decoder", "No data received")
    class ALG:
        def __init__(self):
            self.yaw = None
            self.pitch = None
            self.roll = None
        def decode(self, recv_data):
            data = recv_data[6 + 8: 6 + 8 + 8]
            self.yaw =  int(UBXDecoder.inverse_bytes_to_hex(data[0:4]), 16) / UBXDecoder.DENOM
            self.pitch =  int(UBXDecoder.inverse_bytes_to_hex(data[4:6]), 16) / UBXDecoder.DENOM
            self.roll =  int(UBXDecoder.inverse_bytes_to_hex(data[6:8]), 16) / UBXDecoder.DENOM

    def __init__(self):
        self.meas = self.MEAS()
        self.alg = self.ALG()
    
    def decode(self, recv_data):
        header = recv_data[0] << 8 | recv_data[1] # recvData[0] & recvData[1] is the header
        msg_class = recv_data[2] # recvData[2] is the class
        msg_ID = recv_data[3] # recvData[3] is the ID
        if header == UBXDecoder.HEADER_UBX:
            if msg_class == 16:
                if msg_ID == UBXDecoder.ID_MEAS:
                    self.meas.decode(recv_data)

                if msg_ID == UBXDecoder.ID_ALG:
                    #print("Received data:", recv_data)
                    self.alg.decode(recv_data)
             

    """
    To do: add more ubx data type, ID
    """

    @staticmethod
    def inverse_bytes_to_hex(bytes):
        return binascii.hexlify(bytes[::-1]).decode('utf-8')
    
    