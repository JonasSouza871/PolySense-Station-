from machine import I2C
import time

# BMP280 I2C address
BMP280_ADDR = 0x77

class BMP280:
    """
    Driver for BMP280 temperature and pressure sensor with calibration.
    Implements official Bosch compensation algorithm.
    """
    def __init__(self, i2c):
        self.i2c = i2c
        self.addr = BMP280_ADDR
        self.is_ready = False
        self.cal_params = {}
        self.t_fine = 0
        self._initialize_sensor()

    def _initialize_sensor(self):
        """
        Initialize sensor and verify chip ID.
        Accepts both BMP280 (0x58) and BME280 (0x60) chip IDs.
        """
        try:
            chip_id = self.i2c.readfrom_mem(self.addr, 0xD0, 1)[0]
            
            # Accept 0x58 (BMP280) OR 0x60 (BME280)
            if chip_id in [0x58, 0x60]:
                self._read_calibration_params()
                # Configure sensor (oversampling x1 for temp and pressure, normal mode)
                self.i2c.writeto_mem(self.addr, 0xF4, b'\x27') 
                self.is_ready = True
                print(f"BMP/BME280: Sensor ready (Chip ID: {hex(chip_id)}).")
            else:
                print(f"BMP280: Initialization error. Unexpected Chip ID: {hex(chip_id)}")
        except OSError as e:
            print(f"BMP280: I2C communication error during initialization: {e}")
            self.is_ready = False
            
    def _read_word_le(self, reg, signed=False):
        """
        Read 16-bit word in little-endian format from register.
        
        Args:
            reg: Register address
            signed: Interpret as signed integer if True
        """
        data = self.i2c.readfrom_mem(self.addr, reg, 2)
        val = data[0] | (data[1] << 8)
        if signed and val > 32767:
            val -= 65536
        return val

    def _read_calibration_params(self):
        """
        Read factory calibration parameters from sensor EEPROM.
        Required for temperature and pressure compensation.
        """
        self.cal_params['dig_T1'] = self._read_word_le(0x88)
        self.cal_params['dig_T2'] = self._read_word_le(0x8A, signed=True)
        self.cal_params['dig_T3'] = self._read_word_le(0x8C, signed=True)
        self.cal_params['dig_P1'] = self._read_word_le(0x8E)
        self.cal_params['dig_P2'] = self._read_word_le(0x90, signed=True)
        self.cal_params['dig_P3'] = self._read_word_le(0x92, signed=True)
        self.cal_params['dig_P4'] = self._read_word_le(0x94, signed=True)
        self.cal_params['dig_P5'] = self._read_word_le(0x96, signed=True)
        self.cal_params['dig_P6'] = self._read_word_le(0x98, signed=True)
        self.cal_params['dig_P7'] = self._read_word_le(0x9A, signed=True)
        self.cal_params['dig_P8'] = self._read_word_le(0x9C, signed=True)
        self.cal_params['dig_P9'] = self._read_word_le(0x9E, signed=True)
        
    def _compensate_temperature(self, adc_T):
        """
        Apply temperature compensation algorithm using calibration data.
        
        Args:
            adc_T: Raw ADC temperature value
            
        Returns:
            Temperature in degrees Celsius
        """
        dig_T1 = self.cal_params['dig_T1']
        dig_T2 = self.cal_params['dig_T2']
        dig_T3 = self.cal_params['dig_T3']

        var1 = (adc_T / 16384.0 - dig_T1 / 1024.0) * dig_T2
        var2 = ((adc_T / 131072.0 - dig_T1 / 8192.0) *
                (adc_T / 131072.0 - dig_T1 / 8192.0)) * dig_T3
        self.t_fine = int(var1 + var2)
        temp_celsius = (var1 + var2) / 5120.0
        return temp_celsius

    def _compensate_pressure(self, adc_P):
        """
        Apply pressure compensation algorithm using calibration data.
        Requires prior temperature compensation for t_fine value.
        
        Args:
            adc_P: Raw ADC pressure value
            
        Returns:
            Pressure in hectopascals (hPa)
        """
        dig_P1 = self.cal_params['dig_P1']
        dig_P2 = self.cal_params['dig_P2']
        dig_P3 = self.cal_params['dig_P3']
        dig_P4 = self.cal_params['dig_P4']
        dig_P5 = self.cal_params['dig_P5']
        dig_P6 = self.cal_params['dig_P6']
        dig_P7 = self.cal_params['dig_P7']
        dig_P8 = self.cal_params['dig_P8']
        dig_P9 = self.cal_params['dig_P9']

        var1 = self.t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * dig_P6 / 32768.0
        var2 = var2 + var1 * dig_P5 * 2.0
        var2 = var2 / 4.0 + dig_P4 * 65536.0
        var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * dig_P1
        if var1 == 0:
            return 0  # Prevent division by zero
        p = 1048576.0 - adc_P
        p = ((p - var2 / 4096.0) * 6250.0) / var1
        var1 = dig_P9 * p * p / 2147483648.0
        var2 = p * dig_P8 / 32768.0
        p = p + (var1 + var2 + dig_P7) / 16.0
        return p / 100.0  # Convert to hPa

    def get_data(self):
        """
        Read and return compensated temperature and pressure values.
        
        Returns:
            tuple: (temperature_celsius, pressure_hpa) or (None, None) on error
        """
        if not self.is_ready:
            return None, None
            
        try:
            self.i2c.writeto_mem(self.addr, 0xF4, b'\x27') 
            time.sleep(0.1)

            temp_raw = self.i2c.readfrom_mem(self.addr, 0xFA, 3)
            adc_T = (temp_raw[0] << 12) | (temp_raw[1] << 4) | (temp_raw[2] >> 4)
            
            press_raw = self.i2c.readfrom_mem(self.addr, 0xF7, 3)
            adc_P = (press_raw[0] << 12) | (press_raw[1] << 4) | (press_raw[2] >> 4)
            
            temp_celsius = self._compensate_temperature(adc_T)
            pressure_hpa = self._compensate_pressure(adc_P)
            
            return temp_celsius, pressure_hpa
        except OSError as e:
            print(f"BMP280: Data read error: {e}")
            return None, None