# Arquivo: bmp180.py
# Biblioteca para o sensor de pressão e temperatura BMP180

from machine import I2C
import time

class BMP180:
    """
    Driver do MicroPython para o sensor barométrico BMP180.
    """
    _BMP180_ADDR = 0x77  # Endereço I2C fixo do BMP180

 
    _REG_AC1 = 0xAA
    _REG_CHIP_ID = 0xD0
    _REG_CTRL = 0xF4
    _REG_DATA = 0xF6
    _CMD_READ_TEMP = 0x2E
    _CMD_READ_PRESSURE = [0x34, 0x74, 0xB4, 0xF4] # Depende do oversampling

    def __init__(self, i2c_bus, oss=0):
        self.i2c = i2c_bus
        self.oss = oss  # Oversampling setting (0 a 3)
        self._coeffs = {}
        self.chip_id = self._read_chip_id()
        if self.chip_id != 0x55:
            raise RuntimeError(f"Chip ID incorreto: esperado 0x55, mas obtido {hex(self.chip_id)}")
        self._load_calibration()
        print("BMP180: Sensor de temperatura e pressão pronto.")

    def _read_chip_id(self):
        return self.i2c.readfrom_mem(self._BMP180_ADDR, self._REG_CHIP_ID, 1)[0]

    def _read_word(self, reg, signed=True):
        """Lê uma palavra de 16 bits (2 bytes) do barramento I2C."""
        high, low = self.i2c.readfrom_mem(self._BMP180_ADDR, reg, 2)
        val = (high << 8) + low
        if signed and val > 32767:
            val -= 65536
        return val

    def _load_calibration(self):
        """Carrega os coeficientes de calibração da memória do sensor."""
        self._coeffs['ac1'] = self._read_word(0xAA)
        self._coeffs['ac2'] = self._read_word(0xAC)
        self._coeffs['ac3'] = self._read_word(0xAE)
        self._coeffs['ac4'] = self._read_word(0xB0, signed=False)
        self._coeffs['ac5'] = self._read_word(0xB2, signed=False)
        self._coeffs['ac6'] = self._read_word(0xB4, signed=False)
        self._coeffs['b1'] = self._read_word(0xB6)
        self._coeffs['b2'] = self._read_word(0xB8)
        self._coeffs['mb'] = self._read_word(0xBA)
        self._coeffs['mc'] = self._read_word(0xBC)
        self._coeffs['md'] = self._read_word(0xBE)

    def _read_raw_temp(self):
        """Lê a temperatura bruta do sensor."""
        self.i2c.writeto_mem(self._BMP180_ADDR, self._REG_CTRL, bytearray([self._CMD_READ_TEMP]))
        time.sleep_ms(5)
        return self._read_word(self._REG_DATA, signed=False)

    def _read_raw_pressure(self):
        """Lê a pressão bruta do sensor."""
        cmd = self._CMD_READ_PRESSURE[self.oss]
        self.i2c.writeto_mem(self._BMP180_ADDR, self._REG_CTRL, bytearray([cmd]))
        time.sleep_ms([5, 8, 14, 26][self.oss])
        msb, lsb, xlsb = self.i2c.readfrom_mem(self._BMP180_ADDR, self._REG_DATA, 3)
        return ((msb << 16) + (lsb << 8) + xlsb) >> (8 - self.oss)

    def get_data(self):
        """
        Retorna a temperatura (°C) e a pressão (hPa) compensadas.
        """
        # Leitura da temperatura e cálculo de B5
        ut = self._read_raw_temp()
        x1 = (ut - self._coeffs['ac6']) * self._coeffs['ac5'] // 2**15
        x2 = self._coeffs['mc'] * 2**11 // (x1 + self._coeffs['md'])
        b5 = x1 + x2
        temp = ((b5 + 8) / 2**4) / 10.0

        # Leitura da pressão
        up = self._read_raw_pressure()
        b6 = b5 - 4000
        x1 = (self._coeffs['b2'] * (b6 * b6 // 2**12)) // 2**11
        x2 = self._coeffs['ac2'] * b6 // 2**11
        x3 = x1 + x2
        b3 = (((self._coeffs['ac1'] * 4 + x3) << self.oss) + 2) // 4
        x1 = self._coeffs['ac3'] * b6 // 2**13
        x2 = (self._coeffs['b1'] * (b6 * b6 // 2**12)) // 2**16
        x3 = ((x1 + x2) + 2) // 2**2
        b4 = self._coeffs['ac4'] * (x3 + 32768) // 2**15
        b7 = (up - b3) * (50000 >> self.oss)
        if b7 < 0x80000000:
            p = (b7 * 2) // b4
        else:
            p = (b7 // b4) * 2
        x1 = (p // 2**8)**2
        x1 = (x1 * 3038) // 2**16
        x2 = (-7357 * p) // 2**16
        pressure_pa = p + (x1 + x2 + 3791) // 2**4
        pressure_hpa = pressure_pa / 100.0

        return temp, pressure_hpa