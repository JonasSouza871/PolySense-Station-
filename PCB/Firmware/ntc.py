import machine
import time
import math

class NTC:
    def __init__(self, adc_pin):
        """
        Initialize NTC thermistor sensor
        Args:
            adc_pin: ADC pin number for reading thermistor voltage
        """
        self.adc = machine.ADC(adc_pin)
    
    def get_temperature(self):
        """
        Read temperature from NTC thermistor using Steinhart-Hart equation
        Returns:
            temperature in degrees Celsius
        """
        # Read raw ADC value (0-65535 for 0-3.3V range)
        raw = self.adc.read_u16()
        
        # Convert ADC reading to voltage
        voltage = raw * (3.3 / 65535)
        
        # Calculate resistance using voltage divider formula
        # Circuit: R_fixed (10kΩ) -> ADC -> NTC -> GND
        resistance = 10000 * voltage / (3.3 - voltage)
        
        # Calculate temperature using Steinhart-Hart equation
        # For typical NTC: R0=10kΩ, B=3950, T0=25°C (298.15K)
        temp_kelvin = 1 / (math.log(resistance / 10000) / 3950 + 1 / 298.15)
        
        # Convert from Kelvin to Celsius
        temperature = temp_kelvin - 273.15
        
        return temperature