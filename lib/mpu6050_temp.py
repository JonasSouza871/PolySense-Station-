from machine import I2C
import time

# Endereço I2C padrão do MPU6050 (AD0 em GND → 0x68, AD0 em VCC → 0x69)
MPU6050_ADDR = 0x68

class MPU6050:
    """
    Biblioteca simples para ler a temperatura do MPU6050 em MicroPython.
    """

    def __init__(self, i2c, addr=MPU6050_ADDR, temp_offset=0.0):
        """
        Inicializa a classe.
        :param i2c: Objeto I2C já configurado.
        :param addr: Endereço I2C (0x68 ou 0x69).
        :param temp_offset: Offset de calibração (em °C).
        """
        self.i2c = i2c
        self.addr = addr
        self.temp_offset = temp_offset
        self.is_ready = False
        self._initialize_sensor()

    def _initialize_sensor(self):
        """Inicializa e verifica a conexão com o sensor."""
        try:
            # Reset
            self.i2c.writeto_mem(self.addr, 0x6B, b'\x80')
            time.sleep(0.2)

            # Wake-up (sair do sleep mode)
            self.i2c.writeto_mem(self.addr, 0x6B, b'\x00')
            time.sleep(0.2)

            # Testa o WHO_AM_I
            who_am_i = self.i2c.readfrom_mem(self.addr, 0x75, 1)[0]
            if who_am_i == 0x68:
                self.is_ready = True
                print("✅ MPU6050 inicializado com sucesso.")
            else:
                print(f"⚠️ WHO_AM_I inesperado: {hex(who_am_i)} (esperado 0x68)")
        except OSError as e:
            print(f"❌ Erro de comunicação I2C: {e}")
            self.is_ready = False

    def _read_word(self, reg):
        """Lê um valor de 16 bits assinado de um registrador."""
        try:
            data = self.i2c.readfrom_mem(self.addr, reg, 2)
            val = (data[0] << 8) | data[1]
            if val > 32767:
                val -= 65536
            return val
        except OSError as e:
            print(f"❌ Erro ao ler registrador {hex(reg)}: {e}")
            return None

    def get_temperature(self, raw=False):
        """
        Retorna a temperatura em °C (com offset de calibração).
        Se raw=True, retorna também o valor cru TEMP_OUT.
        """
        if not self.is_ready:
            return None

        temp_raw = self._read_word(0x41)
        if temp_raw is not None:
            temp_c = (temp_raw / 340.0 + 36.53) + self.temp_offset
            if raw:
                return temp_c, temp_raw
            return temp_c
        return None

    def calibrate(self, real_temp):
        """
        Faz a calibração simples: ajusta o offset para alinhar a leitura
        com a temperatura real (medida por outro termômetro).
        """
        measured = self.get_temperature()
        if measured is not None:
            self.temp_offset = real_temp - measured
            print(f"✅ Calibração aplicada. Offset = {self.temp_offset:.2f} °C")
        else:
            print("❌ Não foi possível calibrar (sensor não pronto).")
