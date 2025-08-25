from machine import Pin
import time

class DHTBase:
    # A classe base continua a mesma, sem mudanças.
    def __init__(self, pin):
        self.pin = pin
        self.buf = bytearray(5)
        self.pin.init(Pin.OUT, Pin.PULL_DOWN)
        self.pin(1)
        time.sleep_ms(20)

    def measure(self):
        buf = self.buf
        pin = self.pin
        pin.init(Pin.OUT, Pin.PULL_DOWN)
        pin(0)
        time.sleep_ms(20)
        pin(1)
        pin.init(Pin.IN, Pin.PULL_UP)
        try:
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
            return

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

        if (buf[0] + buf[1] + buf[2] + buf[3]) & 0xFF != buf[4]:
            raise Exception("checksum error")

# >>> ESTA É A CLASSE DHT11 MODIFICADA <<<
class DHT11(DHTBase):
    def humidity(self):
        # DHT11 usa o byte 0 para umidade (parte inteira) e byte 1 para a parte decimal.
        # No entanto, a maioria dos DHT11 tem a parte decimal sempre zero.
        # A forma mais precisa é ler os dois bytes.
        return (self.buf[0] + self.buf[1] / 100)
    
    def temperature(self):
        # DHT11 usa o byte 2 para temperatura (parte inteira) e byte 3 para a parte decimal.
        # Se for um DHT11, a parte decimal é geralmente 0. Mas esta forma lida com os dois.
        return (self.buf[2] + self.buf[3] / 100)
