from machine import Pin
import time

MPU6050_ADDR = 0x68

class SoftI2C:
    def __init__(self, scl_pin, sda_pin):
        self.scl = Pin(scl_pin, Pin.OUT, Pin.PULL_UP)
        self.sda = Pin(sda_pin, Pin.OUT, Pin.PULL_UP)
        self.delay = 0.00001
        
    def start(self):
        self.sda.init(Pin.OUT)
        self.sda.value(1)
        self.scl.value(1)
        time.sleep(self.delay)
        self.sda.value(0)
        time.sleep(self.delay)
        self.scl.value(0)
        time.sleep(self.delay)
    
    def stop(self):
        self.sda.init(Pin.OUT)
        self.sda.value(0)
        time.sleep(self.delay)
        self.scl.value(1)
        time.sleep(self.delay)
        self.sda.value(1)
        time.sleep(self.delay)
    
    def write_byte(self, byte):
        self.sda.init(Pin.OUT)
        for i in range(8):
            bit = (byte >> (7-i)) & 1
            self.sda.value(bit)
            time.sleep(self.delay)
            self.scl.value(1)
            time.sleep(self.delay)
            self.scl.value(0)
            time.sleep(self.delay)
        self.sda.init(Pin.IN, Pin.PULL_UP)
        time.sleep(self.delay)
        self.scl.value(1)
        time.sleep(self.delay)
        ack = self.sda.value()
        self.scl.value(0)
        time.sleep(self.delay)
        return ack == 0
    
    def read_byte(self, ack=True):
        self.sda.init(Pin.IN, Pin.PULL_UP)
        byte = 0
        for i in range(8):
            time.sleep(self.delay)
            self.scl.value(1)
            time.sleep(self.delay)
            bit = self.sda.value()
            byte = (byte << 1) | bit
            self.scl.value(0)
        self.sda.init(Pin.OUT)
        self.sda.value(0 if ack else 1)
        time.sleep(self.delay)
        self.scl.value(1)
        time.sleep(self.delay)
        self.scl.value(0)
        time.sleep(self.delay)
        return byte
    
    def writeto_mem(self, addr, reg, data):
        self.start()
        if not self.write_byte((addr << 1) | 0):
            self.stop()
            raise OSError("Device not responding")
        if not self.write_byte(reg):
            self.stop()
            raise OSError("Register write failed")
        for b in data:
            if not self.write_byte(b):
                self.stop()
                raise OSError("Data write failed")
        self.stop()
    
    def readfrom_mem(self, addr, reg, num_bytes):
        self.start()
        if not self.write_byte((addr << 1) | 0):
            self.stop()
            raise OSError("Device not responding")
        if not self.write_byte(reg):
            self.stop()
            raise OSError("Register write failed")
        self.start()
        if not self.write_byte((addr << 1) | 1):
            self.stop()
            raise OSError("Read failed")
        data = bytearray()
        for i in range(num_bytes):
            data.append(self.read_byte(ack=(i < num_bytes-1)))
        self.stop()
        return bytes(data)
    
    def writeto(self, addr, data):
        """NOVO: Escreve dados sem registrador (para AHT20)"""
        self.start()
        if not self.write_byte((addr << 1) | 0):
            self.stop()
            raise OSError("Device not responding")
        for b in data:
            if not self.write_byte(b):
                self.stop()
                raise OSError("Data write failed")
        self.stop()
    
    def readfrom(self, addr, num_bytes):
        """NOVO: Lê dados sem registrador (para AHT20)"""
        self.start()
        if not self.write_byte((addr << 1) | 1):
            self.stop()
            raise OSError("Read failed")
        data = bytearray()
        for i in range(num_bytes):
            data.append(self.read_byte(ack=(i < num_bytes-1)))
        self.stop()
        return bytes(data)

class MPU6050:
    def __init__(self, i2c, addr=MPU6050_ADDR, temp_offset=-15.0):
        self.i2c = i2c
        self.addr = addr
        self.temp_offset = temp_offset
        self.is_ready = False
        self._initialize_sensor()
    
    def _initialize_sensor(self):
        try:
            self.i2c.writeto_mem(self.addr, 0x6B, b'\x80')
            time.sleep(0.2)
            self.i2c.writeto_mem(self.addr, 0x6B, b'\x00')
            time.sleep(0.2)
            who_am_i = self.i2c.readfrom_mem(self.addr, 0x75, 1)[0]
            if who_am_i in [0x68, 0x70]:
                self.is_ready = True
                print(f"✅ MPU6500/MPU9250 inicializado com sucesso.")
            else:
                print(f"⚠️ WHO_AM_I: 0x{who_am_i:02X}")
        except OSError as e:
            print(f"❌ MPU erro: {e}")
            self.is_ready = False
    
    def _read_word(self, reg):
        try:
            data = self.i2c.readfrom_mem(self.addr, reg, 2)
            val = (data[0] << 8) | data[1]
            if val > 32767:
                val -= 65536
            return val
        except:
            return None
    
    def get_temperature(self):
        if not self.is_ready:
            return None
        temp_raw = self._read_word(0x41)
        if temp_raw is not None:
            return (temp_raw / 340.0 + 36.53) + self.temp_offset
        return None