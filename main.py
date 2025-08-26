# main.py - Datalogger Completo com Múltiplos Sensores, RTC, SD Card e Display OLED

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

# --- LED e Botão ---
led = Pin("LED", Pin.OUT)
# Botão de Ejeção Segura no GP3 (PULL_DOWN significa que o valor é 0 quando não pressionado)
eject_button = Pin(3, Pin.IN, Pin.PULL_DOWN)

# --- Configuração dos Barramentos I2C ---
# Barramento I2C 1 (Sensores Originais)
SDA1_PIN = 18
SCL1_PIN = 19
i2c1 = I2C(1, sda=Pin(SDA1_PIN), scl=Pin(SCL1_PIN), freq=100000)

# Barramento I2C 0 (BMP180 e Display OLED)
SDA0_PIN = 16
SCL0_PIN = 17
i2c0 = I2C(0, sda=Pin(SDA0_PIN), scl=Pin(SCL0_PIN), freq=100000)

# --- Configuração do SD Card (SPI) ---
spi = SPI(1,
          baudrate=1000000,
          sck=Pin(10),
          mosi=Pin(11),
          miso=Pin(12))
cs = Pin(13, Pin.OUT)

# --- Configuração dos Sensores Individuais ---
# DS18x20 (OneWire no pino 2)
ds_pin = Pin(2, Pin.IN)
ds = ds18x20.DS18X20(onewire.OneWire(ds_pin))

# NTC (ADC no pino 28)
ntc_sensor = NTC(28)

# DHT11 (Pino Digital 9)
try:
    dht_sensor = DHT11(Pin(9))
    print("✓ Sensor DHT11 inicializado com sucesso no pino 9.")
except Exception as e:
    print(f"✗ ERRO: Falha ao inicializar DHT11: {e}")
    dht_sensor = None

# === INICIALIZAÇÃO DOS DISPOSITIVOS E SISTEMA ===

print("\n" + "="*50)
print("INICIALIZANDO SISTEMA DE MONITORAMENTO E DATALOGGER")
print("="*50 + "\n")

# --- Montagem do SD Card e Criação do Arquivo de Log ---
try:
    sd = SDCard(spi, cs)
    os.mount(sd, '/sd')
    print("✓ Cartão SD montado com sucesso.")
    
    log_file_path = '/sd/datalogger_completo.csv'
    
    # Define o cabeçalho para o arquivo CSV
    csv_header = (
        "Timestamp,Temp_MPU6050_C,Temp_AHT20_C,Umid_AHT20_pct,"
        "Temp_BMP280_C,Press_BMP280_hPa,Temp_BMP180_C,Press_BMP180_hPa,"
        "Temp_DS18B20_C,Temp_NTC_C,Temp_DHT11_C,Umid_DHT11_pct\n"
    )

    # Cria o arquivo com cabeçalho apenas se ele não existir
    try:
        with open(log_file_path, 'r') as f:
            pass # Arquivo já existe, não faz nada
        print(f"✓ Usando arquivo de log existente: {log_file_path}")
    except OSError:
        # O arquivo não existe, então o criamos com o cabeçalho
        with open(log_file_path, 'w') as f:
            f.write(csv_header)
        print(f"✓ Novo arquivo de log criado: {log_file_path}")
        
except Exception as e:
    print(f"✗ FALHA CRÍTICA AO MONTAR O CARTÃO SD: {e}")
    print("O programa será interrompido. Verifique as conexões e o cartão.")
    raise # Interrompe a execução

# --- Inicialização do Relógio de Tempo Real (RTC) ---
rtc = RTC()
# IMPORTANTE: Na primeira vez que rodar, descomente a linha abaixo
# e ajuste para a data e hora atuais para acertar o relógio.
# Formato: (ano, mês, dia, dia_da_semana, hora, minuto, segundo, microssegundo)
# Exemplo para 25 de Agosto de 2025, 22:05:00 (Segunda-feira = 0)
# rtc.datetime((2025, 8, 25, 0, 22, 5, 0, 0))
print("✓ RTC inicializado.")

# --- Inicialização dos Sensores I2C e OLED ---
print("\n--- Verificando Sensores nos Barramentos I2C ---")
# Barramento 1
devices1 = i2c1.scan()
print(f"I2C 1 (SDA={SDA1_PIN}, SCL={SCL1_PIN}) - Dispositivos: {[hex(d) for d in devices1]}")
mpu_sensor = MPU6050(i2c1)
aht_sensor = AHT20(i2c1)
bmp280_sensor = BMP280(i2c1)

# Barramento 0
devices0 = i2c0.scan()
print(f"I2C 0 (SDA={SDA0_PIN}, SCL={SCL0_PIN}) - Dispositivos: {[hex(d) for d in devices0]}")
bmp180_sensor = BMP180(i2c0)
oled = SSD1306(128, 64, i2c0)

# --- Verificação do Sensor OneWire ---
roms = ds.scan()
if not roms:
    print("✗ ERRO: Nenhum sensor DS18x20 encontrado no pino 2!")
else:
    print(f"✓ Sensor DS18x20 encontrado: {roms}")


print("\n--- REGISTRO INICIADO ---")
print("Pressione o botão no GP3 para desmontar o cartão com segurança.")
screen = 0 # Variável para alternar a tela do OLED

# === LOOP PRINCIPAL ===
while True:
    # 1. VERIFICAR BOTÃO DE EJEÇÃO
    if eject_button.value() == 1:
        print("\nBotão de ejeção pressionado. Finalizando...")
        break

    try:
        print("-" * 50)
        
        # 2. LEITURA DE TODOS OS SENSORES
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

        # 3. OBTER TIMESTAMP DO RTC
        current_time = rtc.datetime()
        timestamp_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            current_time[0], current_time[1], current_time[2],
            current_time[4], current_time[5], current_time[6]
        )
        print(f"Timestamp: {timestamp_str}")

        # 4. EXIBIÇÃO NO CONSOLE
        print(f"TempA (MPU6050) = {tempA:.2f} C" if tempA is not None else "TempA: Falha")
        print(f"TempB (AHT20) = {tempB:.2f} C, UmidA = {umidA:.2f} %" if tempB is not None else "TempB/UmidA: Falha")
        print(f"TempC (BMP280) = {tempC:.2f} C, PressA = {pressA:.2f} hPa" if tempC is not None else "TempC/PressA: Falha")
        print(f"TempD (BMP180) = {tempD:.2f} C, PressB = {pressB:.2f} hPa" if tempD is not None else "TempD/PressB: Falha")
        print(f"TempE (DS18B20) = {tempE:.2f} C" if tempE is not None else "TempE: Falha")
        print(f"TempF (NTC) = {tempF:.2f} C" if tempF is not None else "TempF: Falha")
        print(f"TempG (DHT11) = {tempG:.2f} C, UmidB = {umidB:.2f} %" if tempG is not None else "TempG/UmidB: Falha")

        # 5. EXIBIÇÃO NO DISPLAY OLED
        oled.fill(0)
        if screen == 0:
            oled.text(f"TmpA(MPU):{tempA:.1f}C" if tempA is not None else "TmpA:--", 0, 0)
            oled.text(f"TmpB(AHT):{tempB:.1f}C" if tempB is not None else "TmpB:--", 0, 10)
            oled.text(f"TmpC(B280):{tempC:.1f}C" if tempC is not None else "TmpC:--", 0, 20)
            oled.text(f"TmpD(B180):{tempD:.1f}C" if tempD is not None else "TmpD:--", 0, 30)
            oled.text(f"TmpE(DS18):{tempE:.1f}C" if tempE is not None else "TmpE:--", 0, 40)
            oled.text(f"TmpF(NTC):{tempF:.1f}C" if tempF is not None else "TmpF:--", 0, 50)
        else:
            oled.text(f"TmpG(DHT):{tempG:.1f}C" if tempG is not None else "TmpG:--", 0, 0)
            oled.text(f"UmdB(DHT):{umidB:.1f}%" if umidB is not None else "UmdB:--", 0, 10)
            oled.text(f"UmdA(AHT):{umidA:.1f}%" if umidA is not None else "UmdA:--", 0, 20)
            oled.text(f"PrsA(B280):{pressA:.0f}" if pressA is not None else "PrsA:--", 0, 30)
            oled.text(f"PrsB(B180):{pressB:.0f}" if pressB is not None else "PrsB:--", 0, 40)
        oled.show()
        screen = 1 - screen # Alterna a tela (0 -> 1, 1 -> 0)

        # 6. GRAVAÇÃO DOS DADOS NO ARQUIVO CSV
        # Formata cada valor para o CSV, deixando em branco se a leitura falhou
        data_row = (
            f"{timestamp_str},"
            f"{tempA:.2f}," if tempA is not None else ","
            f"{tempB:.2f}," if tempB is not None else ","
            f"{umidA:.2f}," if umidA is not None else ","
            f"{tempC:.2f}," if tempC is not None else ","
            f"{pressA:.2f}," if pressA is not None else ","
            f"{tempD:.2f}," if tempD is not None else ","
            f"{pressB:.2f}," if pressB is not None else ","
            f"{tempE:.2f}," if tempE is not None else ","
            f"{tempF:.2f}," if tempF is not None else ","
            f"{tempG:.2f}," if tempG is not None else ","
            f"{umidB:.2f}\n" if umidB is not None else "\n"
        )
        
        try:
            with open(log_file_path, 'a') as f:
                f.write(data_row)
            
            # Pisca o LED para indicar que o registro foi salvo
            led.on()
            time.sleep_ms(50)
            led.off()
            print("✓ Registro salvo no SD Card.")
            
        except Exception as e:
            print(f"✗ ERRO AO SALVAR NO ARQUIVO: {e}")

    except Exception as e:
        print(f"Ocorreu um erro inesperado no loop principal: {e}")
        # Em caso de erro grave, tentamos desmontar o SD antes de parar
        break 
        
    # 7. AGUARDAR PARA O PRÓXIMO CICLO
    time.sleep(5)

# === FINALIZAÇÃO E EJEÇÃO SEGURA ===
print("\nDesmontando o sistema de arquivos do cartão SD...")
try:
    os.umount('/sd')
    print("✓ Cartão SD desmontado com segurança!")
    
    # Pisca o LED 5 vezes para sinalizar que é seguro remover o cartão
    for _ in range(5):
        led.on()
        time.sleep(0.2)
        led.off()
        time.sleep(0.2)
        
except Exception as e:
    print(f"✗ Erro ao desmontar o cartão SD: {e}")

print("Programa finalizado. É seguro remover o cartão.")