import serial
import time
import datetime as dt


class CGcontactor:
    __RS485_chip = None
    __xx = "01"
    __IG_pressure = ""
    __CG1_pressure = ""
    __CG2_pressure = ""

    def __init__(self, port, baudrate=19200, timeout=1, bytesize=8, parity='N', stopbits=1):
        self.__RS485_chip = serial.Serial(port=port,
                        baudrate=baudrate,
                        timeout=timeout,
                        bytesize=bytesize,
                        parity=parity,
                        stopbits=stopbits)
        
        # prestart
        self.__send_to_chip("RDS")
        time.sleep(0.1)
    
    def __send_to_chip(self, command: str) -> str:
        """takes 'command' and sends it to the chip, returns chip answer as string"""
        received = ""

        self.__RS485_chip.reset_input_buffer()
        self.__RS485_chip.reset_output_buffer()

        self.__RS485_chip.write(f"#{self.__xx}{command}\r".encode())

        while received == "":
            received = self.__RS485_chip.readline().decode()
                
        time.sleep(0.06)
        # print(received)

        return received
    
    def get_device_status(self)->bool:
        """returns True if device is connected, Flase otherwise"""
        #TODO check if it's possible, or even if this function is needed
        pass

    # Feliment
    def is_feliment_safe_to_start(self)->bool:
        """returns True if feliment is safe to turn on, Flase otherwise"""
        #TODO validate that this is correct
        tmp = self.get_CG1_pressure().split("E")
        y, p = tmp[0], tmp[1][:2]
        y, p = float(y), float(p)
        if p < -3 or (p == -3 and y == 1):
            return True
        if p == 0 and y == 0:
            return True
        return False

    def get_feliment_status(self)->bool:
        """returns True if feliment is on, Flase otherwise"""
        return "on" in self.__send_to_chip("IGS").lower()

    def turn_feliment_on(self)->bool:
        """turns feliment on, returns True on success, False on otherwise"""
        if not self.is_feliment_safe_to_start():
            return False
        return "ok" in self.__send_to_chip("IG1").lower()

    def turn_feliment_off(self)->bool:
        """turns feliment off, returns True on success, False on otherwise"""
        return "ok" in self.__send_to_chip("IG0").lower()

    # IG
    def get_IG_status(self)->bool:
        """returns True if IG is on, Flase otherwise"""
        return "9.90E+09" not in self.__send_to_chip("RD")

    def get_IG_pressure(self)->str:
        """returns pressure value informat y.yyEzyy
        where y.yy = mantissa, 
        z = sign of the exponent, i.e., +/- 
        and pp = the exponent."""
        res = self.__send_to_chip("RD")[4:12]
        try:
            float(res)
        except:
            res = res[:-1]
        return res

    # CG1
    def get_CG1_status(self)->bool:
        """returns True if CG1 is connected, Flase otherwise"""
        return "1.01E+03" not in self.__send_to_chip("RDCG1")

    def get_CG1_pressure(self)->str:
        """returns pressure value informat y.yyEzyy
        where y.yy = mantissa, 
        z = sign of the exponent, i.e., +/- 
        and pp = the exponent."""
        res = self.__send_to_chip("RDCG1")[4:12]
        try:
            float(res)
        except:
            res = res[:-1]
        return res

    # CG2
    def get_CG2_status(self)->bool:
        """returns True if CG2 is connected, Flase otherwise"""
        return "1.01E+03" not in self.__send_to_chip("RDCG2")

    def get_CG2_pressure(self)->str:
        """returns pressure value informat y.yyEzyy
        where y.yy = mantissa, 
        z = sign of the exponent, i.e., +/- 
        and pp = the exponent."""
        res = self.__send_to_chip("RDCG2")[4:12]
        try:
            float(res)
        except:
            res = res[:-1]
        return res
