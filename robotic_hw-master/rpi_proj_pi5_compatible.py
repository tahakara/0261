import lgpio
import time
from collections import deque

# --- GPIO Pin Tanımları ---
LED_YESIL = 17
LED_SARI = 27
LED_KIRMIZI = 22
BUZZER = 23
TRIG_PIN = 5
ECHO_PIN = 6
BUTTON_PIN = 24

# --- Mesafe Sınırları ---
MESAFE_KIRMIZI_SINIR = 10
MESAFE_SARI_SINIR = 30

# --- Sistem Değişkenleri ---
STATUS_ACIK = False
SON_BUTON_BASILMA_ZAMANI = 0
MIN_BASMA_ARALIGI = 1.0

# --- Filtre Ayarları ---
MIN_DIST = 2
MAX_DIST = 200
ROLLING_WINDOW = 5
distance_buffer = deque(maxlen=ROLLING_WINDOW)

# --- lgpio Handler ---
CHIP = 0  # genelde Raspberry Pi için 0
h = None


def setup():
    global h
    h = lgpio.gpiochip_open(CHIP)

    # Çıkış pinleri
    for pin in [LED_YESIL, LED_SARI, LED_KIRMIZI, BUZZER, TRIG_PIN]:
        lgpio.gpio_claim_output(h, pin, 0)

    # Giriş pinleri
    lgpio.gpio_claim_input(h, ECHO_PIN)
    lgpio.gpio_claim_input(h, BUTTON_PIN)


def set_pin(pin, value):
    lgpio.gpio_write(h, pin, value)


def get_distance():
    set_pin(TRIG_PIN, 0)
    time.sleep(0.0002)
    set_pin(TRIG_PIN, 1)
    time.sleep(0.00001)
    set_pin(TRIG_PIN, 0)

    timeout_start = time.time()
    while lgpio.gpio_read(h, ECHO_PIN) == 0:
        if time.time() - timeout_start > 0.1:
            return -1
    pulse_start = time.time()

    timeout_start = time.time()
    while lgpio.gpio_read(h, ECHO_PIN) == 1:
        if time.time() - timeout_start > 0.1:
            return -1
    pulse_end = time.time()

    distance = (pulse_end - pulse_start) * 34300 / 2
    return round(distance, 2)


def filter_distance(distance):
    return distance if MIN_DIST <= distance <= MAX_DIST else None


def leds_off():
    for pin in [LED_YESIL, LED_SARI, LED_KIRMIZI, BUZZER]:
        set_pin(pin, 0)


def welcome_sequence():
    print("Sistem BAŞLATILIYOR...")
    for led in [LED_KIRMIZI, LED_SARI, LED_YESIL]:
        set_pin(led, 1)
        set_pin(BUZZER, 1); time.sleep(0.05)
        set_pin(BUZZER, 0)
        time.sleep(0.2)
        set_pin(led, 0)


def shutdown_sequence():
    print("Sistem KAPATILIYOR...")
    leds_off()
    for led in [LED_YESIL, LED_SARI, LED_KIRMIZI]:
        set_pin(led, 1)
        set_pin(BUZZER, 1); time.sleep(0.1)
        set_pin(BUZZER, 0)
        time.sleep(0.15)
        set_pin(led, 0)


def button_pressed():
    global STATUS_ACIK, SON_BUTON_BASILMA_ZAMANI
    now = time.time()
    if now - SON_BUTON_BASILMA_ZAMANI < MIN_BASMA_ARALIGI:
        return
    SON_BUTON_BASILMA_ZAMANI = now

    if STATUS_ACIK:
        shutdown_sequence()
        STATUS_ACIK = False
        leds_off()
        print("Sistem durdu.")
    else:
        welcome_sequence()
        STATUS_ACIK = True
        print("Sistem aktif.")


def main():
    global STATUS_ACIK
    try:
        setup()
        print("Sistem hazır. Butona basarak başlat/durdur.")

        while True:
            if lgpio.gpio_read(h, BUTTON_PIN) == 0:
                button_pressed()
                time.sleep(0.2)

            if STATUS_ACIK:
                distance = filter_distance(get_distance())
                if distance:
                    distance_buffer.append(distance)
                    avg = sum(distance_buffer)/len(distance_buffer)
                    print(f"Mesafe: {avg:.2f} cm")

                    leds_off()
                    if avg < MESAFE_KIRMIZI_SINIR:
                        set_pin(LED_KIRMIZI, 1)
                        set_pin(BUZZER, 1)
                    elif avg < MESAFE_SARI_SINIR:
                        set_pin(LED_SARI, 1)
                        set_pin(BUZZER, 1); time.sleep(0.05); set_pin(BUZZER, 0)
                    else:
                        set_pin(LED_YESIL, 1)
                        set_pin(BUZZER, 1); time.sleep(0.2); set_pin(BUZZER, 0)
                else:
                    print("Geçersiz ölçüm.")
            else:
                leds_off()

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Çıkış...")
    finally:
        leds_off()
        if h:
            lgpio.gpiochip_close(h)


if __name__ == "__main__":
    main()
