# main.py - Datalogger Otimizado para Bateria (sem saídas no console/serial)
# Todas as instruções 'print()' foram removidas para economizar energia.
# O feedback é fornecido pelo display OLED e pelo LED da placa.

# === IMPORTAÇÕES ===
import os
import machine
from machine import Pin, I2C, ADC, SPI, RTC
import time

# Bibliotecas dos Sensores e Dispositivos
from ssd1306 import SSD1306
from mpu6050_temp import MPU6050
from AHT20 import AHT20
from bmp280 import BMP280
from bmp180 import BMP180
import onewire
import ds18x20
from ntc import NTC
from dht11 import DHT11
from sdcard import SDCard

# === CONFIGURAÇÕES GERAIS E DE HARDWARE ===
led = Pin("LED", Pin.OUT)
eject_button = Pin(3, Pin.IN, Pin.PULL_DOWN)
SDA1_PIN = 18
SCL1_PIN = 19
i2c1 = I2C(1, sda=Pin(SDA1_PIN), scl=Pin(SCL1_PIN), freq=100000)
SDA0_PIN = 16
SCL0_PIN = 17
i2c0 = I2C(0, sda=Pin(SDA0_PIN), scl=Pin(SCL0_PIN), freq=100000)
spi = SPI(1, baudrate=1000000, sck=Pin(10), mosi=Pin(11), miso=Pin(12))
cs = Pin(13, Pin.OUT)
ds_pin = Pin(2, Pin.IN)
ds = ds18x20.DS18X20(onewire.OneWire(ds_pin))
ntc_sensor = NTC(28)
try:
    dht_sensor = DHT11(Pin(9))
except Exception as e:
    dht_sensor = None

# === INICIALIZAÇÃO DOS DISPOSITIVOS E SISTEMA ===

# --- Montagem do SD Card e Criação do Arquivo de Log ---
try:
    sd = SDCard(spi, cs)
    os.mount(sd, '/sd')
    log_file_path = '/sd/datalogger_completo.csv'
    csv_header = (
        "Timestamp,Temp_MPU6050_C,Temp_AHT20_C,Umid_AHT20_pct,"
        "Temp_BMP280_C,Press_BMP280_hPa,Temp_BMP180_C,Press_BMP180_hPa,"
        "Temp_DS18B20_C,Temp_NTC_C,Temp_DHT11_C,Umid_DHT11_pct\n"
    )
    try:
        with open(log_file_path, 'r') as f:
            pass # Arquivo existe
    except OSError:
        with open(log_file_path, 'w') as f:
            f.write(csv_header) # Arquivo não existe, cria com cabeçalho
except Exception as e:
    # Em caso de falha crítica na inicialização do SD, pisca o LED rapidamente como sinal de erro
    while True:
        led.toggle()
        time.sleep_ms(100)

# --- Inicialização do Relógio de Tempo Real (RTC) ---
rtc = RTC()
# IMPORTANTE: Para acertar o relógio, conecte ao computador uma vez e rode
# o código com a linha abaixo descomentada e com a hora atual.
# rtc.datetime((2025, 8, 25, 0, 22, 12, 0, 0)) # (ano, mês, dia, dia_da_semana(0=Seg), hora, minuto, segundo, microssegundo)

# --- Inicialização dos Sensores I2C, OLED e OneWire ---
mpu_sensor = MPU6050(i2c1)
aht_sensor = AHT20(i2c1)
bmp280_sensor = BMP280(i2c1)
bmp180_sensor = BMP180(i2c0)
oled = SSD1306(128, 64, i2c0)
roms = ds.scan()

# Variáveis para a tela de status
screen = 0
record_count = 0
log_status = "Aguardando"
start_time = time.ticks_ms()

# === LOOP PRINCIPAL ===
while True:
    if eject_button.value() == 1:
        break

    try:
        # 1. LEITURA DE TODOS OS SENSORES
        tempA = mpu_sensor.get_temperature()
        tempB, umidA = aht_sensor.get_data()
        tempC, pressA = bmp280_sensor.get_data()
        tempD, pressB = bmp180_sensor.get_data()
        tempE = None
        if roms:
            ds.convert_temp()
            time.sleep_ms(750)
            tempE = ds.read_temp(roms[0])
        tempF = ntc_sensor.get_temperature()
        tempG, umidB = None, None
        if dht_sensor:
            for attempt in range(3):
                try:
                    if dht_sensor.measure():
                        tempG = dht_sensor.temperature()
                        umidB = dht_sensor.humidity()
                        break
                except Exception:
                    time.sleep_ms(100)

        # 2. OBTER TIMESTAMP DO RTC
        current_time = rtc.datetime()
        timestamp_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            current_time[0], current_time[1], current_time[2],
            current_time[4], current_time[5], current_time[6]
        )

        # 3. GRAVAÇÃO DOS DADOS NO ARQUIVO CSV
        row_values = [
            timestamp_str,
            f"{tempA:.2f}" if tempA is not None else "",
            f"{tempB:.2f}" if tempB is not None else "",
            f"{umidA:.2f}" if umidA is not None else "",
            f"{tempC:.2f}" if tempC is not None else "",
            f"{pressA:.2f}" if pressA is not None else "",
            f"{tempD:.2f}" if tempD is not None else "",
            f"{pressB:.2f}" if pressB is not None else "",
            f"{tempE:.2f}" if tempE is not None else "",
            f"{tempF:.2f}" if tempF is not None else "",
            f"{tempG:.2f}" if tempG is not None else "",
            f"{umidB:.2f}" if umidB is not None else ""
        ]
        data_row_string = ",".join(row_values) + "\n"

        try:
            with open(log_file_path, 'a') as f:
                f.write(data_row_string)
            
            led.on()
            time.sleep_ms(50)
            led.off()
            
            log_status = "Gravando OK"
            record_count += 1
            
        except Exception as e:
            log_status = "ERRO GRAVACAO"

        # 4. EXIBIÇÃO NO DISPLAY OLED
        oled.fill(0)
        if screen == 0:
            oled.text("--- TEMPS 1/2 ---", 5, 0)
            oled.text(f"A(MPU):{tempA:.1f}C" if tempA is not None else "A:--", 0, 12)
            oled.text(f"B(AHT):{tempB:.1f}C" if tempB is not None else "B:--", 0, 22)
            oled.text(f"C(B280):{tempC:.1f}C" if tempC is not None else "C:--", 0, 32)
            oled.text(f"D(B180):{tempD:.1f}C" if tempD is not None else "D:--", 0, 42)
            oled.text(f"E(DS18):{tempE:.1f}C" if tempE is not None else "E:--", 0, 52)
        elif screen == 1:
            oled.text("--- TEMPS 2/2 ---", 5, 0)
            oled.text(f"F(NTC) :{tempF:.1f}C" if tempF is not None else "F:--", 0, 12)
            oled.text(f"G(DHT) :{tempG:.1f}C" if tempG is not None else "G:--", 0, 22)
            oled.text(f"Umd(AHT):{umidA:.1f}%" if umidA is not None else "UmdA:--", 0, 32)
            oled.text(f"Umd(DHT):{umidB:.1f}%" if umidB is not None else "UmdB:--", 0, 42)
            oled.text(f"Prs(B280):{pressA:.0f}" if pressA is not None else "PrsA:--", 0, 52)
        else:
            oled.text("--- STATUS ---", 15, 0)
            oled.text(f"Status: {log_status}", 0, 15)
            oled.text(f"Registros: {record_count}", 0, 30)
            uptime_s = time.ticks_diff(time.ticks_ms(), start_time) // 1000
            mins = uptime_s // 60
            hours = mins // 60
            uptime_str = f"{hours:02d}:{(mins % 60):02d}:{(uptime_s % 60):02d}"
            oled.text(f"Uptime: {uptime_str}", 0, 45)
        oled.show()
        screen = (screen + 1) % 3

    except Exception as e:
        log_status = "ERRO FATAL"
        # Mesmo com erro, tenta mostrar no display antes de parar
        try:
            oled.fill(0)
            oled.text("--- ERRO FATAL ---", 0, 20)
            oled.text("Reinicie o dispos.", 0, 40)
            oled.show()
        except:
            pass # Se até o display falhar, não há o que fazer
        break 
        
    # 5. AGUARDAR PARA O PRÓXIMO CICLO
    time.sleep(5)

# === FINALIZAÇÃO E EJEÇÃO SEGURA ===
try:
    os.umount('/sd')
    # Pisca o LED 5 vezes para sinalizar que é seguro remover o cartão
    for _ in range(5):
        led.on()
        time.sleep(0.2)
        led.off()
        time.sleep(0.2)
except Exception as e:
    # Se a desmontagem falhar, pisca rapidamente
    while True:
        led.toggle()
        time.sleep_ms(100)