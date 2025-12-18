from machine import Pin
import time

class DHTBase:
    """Base class for DHT sensor family communication protocol."""
    def __init__(self, pin):
        self.pin = pin
        self.buf = bytearray(5)
        self.pin.init(Pin.OUT, Pin.PULL_DOWN)
        self.pin(1)
        time.sleep_ms(20)
    
    def measure(self):
        """Perform sensor measurement using DHT protocol timing."""
        buf = self.buf
        pin = self.pin
        
        # Reset buffer
        for i in range(5):
            buf[i] = 0
        
        # Start signal
        pin.init(Pin.OUT, Pin.PULL_DOWN)
        pin(0)
        time.sleep_ms(20)
        pin(1)
        pin.init(Pin.IN, Pin.PULL_UP)
        
        try:
            # Wait for sensor response
            t = time.ticks_us()
            while pin.value():
                if time.ticks_diff(time.ticks_us(), t) > 100:
                    raise OSError(-1)
            
            t = time.ticks_us()
            while not pin.value():
                if time.ticks_diff(time.ticks_us(), t) > 100:
                    raise OSError(-2)
            
            t = time.ticks_us()
            while pin.value():
                if time.ticks_diff(time.ticks_us(), t) > 100:
                    raise OSError(-3)
        except OSError:
            raise Exception("Timeout na comunicação")
        
        # Read 40 bits
        for i in range(40):
            t = time.ticks_us()
            while not pin.value():
                if time.ticks_diff(time.ticks_us(), t) > 100:
                    break
            
            t = time.ticks_us()
            while pin.value():
                pass
            
            dt = time.ticks_diff(time.ticks_us(), t)
            buf[i // 8] = (buf[i // 8] << 1) | (1 if dt > 40 else 0)
        
        # Verify checksum
        if (buf[0] + buf[1] + buf[2] + buf[3]) & 0xFF != buf[4]:
            raise Exception("checksum error")


class DHT11(DHTBase):
    """DHT11 temperature and humidity sensor driver."""
    
    def humidity(self):
        """Returns relative humidity in percentage."""
        return self.buf[0] + self.buf[1] / 100
    
    def temperature(self):
        """Returns temperature in degrees Celsius."""
        return self.buf[2] + self.buf[3] / 100


class DHT22(DHTBase):
    """DHT22 (AM2302) temperature and humidity sensor driver."""
    
    def humidity(self):
        """Returns relative humidity in percentage with 0.1% resolution."""
        return ((self.buf[0] << 8) | self.buf[1]) / 10
    
    def temperature(self):
        """Returns temperature in degrees Celsius with 0.1°C resolution."""
        t = ((self.buf[2] & 0x7F) << 8) | self.buf[3]
        t = t / 10
        if self.buf[2] & 0x80:
            t = -t
        return t