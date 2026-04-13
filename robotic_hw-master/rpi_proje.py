import RPi.GPIO as GPIO
import time
from collections import deque

# --- GPIO Pin Tanımlamaları (BCM) ---
LED_YESIL = 17
LED_SARI = 27
LED_KIRMIZI = 22
BUZZER = 23  # Pasif buzzer
TRIG_PIN = 5
ECHO_PIN = 6
BUTTON_PIN = 24

# --- Mesafe Sınırları ---
MESAFE_KIRMIZI_SINIR = 10
MESAFE_SARI_SINIR = 30

# --- Buton ve sistem ayarları ---
STATUS_ACIK = False
SON_BUTON_BASILMA_ZAMANI = 0
MIN_BASMA_ARALIGI = 1.0  # saniye

# --- Spike filtresi ve rolling average ayarları ---
MIN_DIST = 2     # cm
MAX_DIST = 200   # cm
ROLLING_WINDOW = 5
distance_buffer = deque(maxlen=ROLLING_WINDOW)

# --- GPIO Kurulumu ---
def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([LED_YESIL, LED_SARI, LED_KIRMIZI, BUZZER], GPIO.OUT)
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.output([LED_YESIL, LED_SARI, LED_KIRMIZI, BUZZER], GPIO.LOW)

# --- Mesafe ölçüm fonksiyonu ---
def get_distance():
    GPIO.output(TRIG_PIN, GPIO.LOW)
    time.sleep(0.0002)
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, GPIO.LOW)

    pulse_start = time.time()
    pulse_end = time.time()

    timeout = time.time()
    while GPIO.input(ECHO_PIN) == GPIO.LOW:
        pulse_start = time.time()
        if pulse_start - timeout > 0.1:
            return -1

    timeout = time.time()
    while GPIO.input(ECHO_PIN) == GPIO.HIGH:
        pulse_end = time.time()
        if pulse_end - timeout > 0.1:
            return -1

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 34300 / 2
    return round(distance, 2)

# --- Spike filtresi ---
def filter_distance(distance):
    if distance < MIN_DIST or distance > MAX_DIST:
        return None
    return distance

# --- Karşılama animasyonu ---
def welcome_sequence():
    print("Sistem BAŞLATILIYOR...")
    for led in [LED_KIRMIZI, LED_SARI, LED_YESIL]:
        GPIO.output(led, GPIO.HIGH)
        GPIO.output(BUZZER, GPIO.HIGH); time.sleep(0.05)
        GPIO.output(BUZZER, GPIO.LOW)
        time.sleep(0.20)
        GPIO.output(led, GPIO.LOW)

# --- Kapanış animasyonu ---
def shutdown_sequence():
    print("Sistem KAPATILIYOR...")
    GPIO.output(BUZZER, GPIO.LOW)
    GPIO.output([LED_YESIL, LED_SARI, LED_KIRMIZI], GPIO.LOW)
    time.sleep(0.5)
    for led in [LED_YESIL, LED_SARI, LED_KIRMIZI]:
        GPIO.output(led, GPIO.HIGH)
        GPIO.output(BUZZER, GPIO.HIGH); time.sleep(0.1)
        GPIO.output(BUZZER, GPIO.LOW)
        time.sleep(0.15)
        GPIO.output(led, GPIO.LOW)

# --- Buton callback ---
def button_callback(channel):
    global STATUS_ACIK, SON_BUTON_BASILMA_ZAMANI
    an = time.time()
    if an - SON_BUTON_BASILMA_ZAMANI < MIN_BASMA_ARALIGI:
        print("Hızlı basım, yoksayılıyor.")
        return
    SON_BUTON_BASILMA_ZAMANI = an

    if STATUS_ACIK:
        shutdown_sequence()
        STATUS_ACIK = False
        GPIO.output([LED_YESIL, LED_SARI, LED_KIRMIZI, BUZZER], GPIO.LOW)
        print("Sistem durdu.")
    else:
        welcome_sequence()
        STATUS_ACIK = True
        print("Sistem aktif.")

# --- Ana Döngü ---
def main():
    try:
        setup()
        GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=200)
        print("Sistem hazır. Butona basarak başlatın/durdurun.")

        while True:
            if STATUS_ACIK:
                distance = get_distance()
                distance = filter_distance(distance)
                if distance is not None:
                    distance_buffer.append(distance)
                if len(distance_buffer) > 0:
                    avg_distance = sum(distance_buffer)/len(distance_buffer)
                else:
                    avg_distance = None

                if avg_distance is not None:
                    print(f"Filtrelenmiş Mesafe: {avg_distance:.2f} cm")
                    # LED ve buzzer kontrolü
                    GPIO.output([LED_YESIL, LED_SARI, LED_KIRMIZI, BUZZER], GPIO.LOW)
                    if avg_distance < MESAFE_KIRMIZI_SINIR:
                        GPIO.output(LED_KIRMIZI, GPIO.HIGH)
                        GPIO.output(BUZZER, GPIO.HIGH)  # Sürekli ses
                    elif avg_distance < MESAFE_SARI_SINIR:
                        GPIO.output(LED_SARI, GPIO.HIGH)
                        GPIO.output(BUZZER, GPIO.HIGH); time.sleep(0.05); GPIO.output(BUZZER, GPIO.LOW); time.sleep(0.05)
                    else:
                        GPIO.output(LED_YESIL, GPIO.HIGH)
                        GPIO.output(BUZZER, GPIO.HIGH); time.sleep(0.2); GPIO.output(BUZZER, GPIO.LOW)
                else:
                    print("Spike atlandı, ölçüm geçersiz.")

            else:
                GPIO.output([LED_YESIL, LED_SARI, LED_KIRMIZI, BUZZER], GPIO.LOW)

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Çıkış yapılıyor...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()