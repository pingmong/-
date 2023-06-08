import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time
import json
import adafruit_dht
import psutil

for proc in psutil.process_iter():
    if proc.name() == 'libgpiod_pulsein':
        proc.kill()
        
dht_device = adafruit_dht.DHT22(4)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

Y_LED = 23
G_LED = 24
R_LED = 25
BUZZER = 12
GPIO.setup(Y_LED, GPIO.OUT)
GPIO.setup(G_LED, GPIO.OUT)
GPIO.setup(R_LED, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)

MQTT_HOST = "broker.emqx.io"
MQTT_PORT = 1883 
MQTT_KEEPALIVE_INTERVAL = 60

MQTT_PUB_TOPIC = "mobile/nayeon/sensing"
MQTT_SUB_TOPIC = "mobile/nayeon/message"

client = mqtt.Client()


client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
client.subscribe(MQTT_SUB_TOPIC)
client.loop_start()

plant_humidity_ranges = {
    "plant1": (30, 60),  # 식물1의 습도 범위: 30% 이상 60% 미만
    "plant2": (40, 70),  # 식물2의 습도 범위: 40% 이상 70% 미만
    "plant3": (50, 80),  # 식물3의 습도 범위: 50% 이상 80% 미만
}

def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    print(f"Received message:  + {payload}")
    
    if received_value in plant_humidity_ranges:
        plant = received_value
        min_range, max_range = plant_humidity_ranges[plant]
        response = f"{plant}의 습도 범위는 {min_range}% 이상 {max_range}% 미만입니다."
        client.publish(MQTT_PUB_TOPIC, response)
        print(response)
    else:
        response = "식물 정보를 찾을 수 없습니다."
        client.publish(MQTT_PUB_TOPIC, response)
        print(response)

client.on_message = on_message

scale = [294, 349, 440]
list_A = [3, 3, 3, 3, 3, 3, 3]
list_B = [2, 1, 2, 1, 2, 1, 2]
term = [2, 2, 2, 2, 2, 2]

plant = input("Enter a plant name: ")
client.publish("input/plant", plant)
print("Published value:", plant)
min_range, max_range = plant_humidity_ranges[plant]
response = f"{plant}의 습도 범위는 {min_range}% 이상 {max_range}% 미만입니다."

plantt = {
    "result": response
}
value2 = json.dumps(plantt, ensure_ascii=False)
client.publish(MQTT_PUB_TOPIC, value2)
print(value2)

            
            
try:   
    while True:

        try:

            min_range, max_range = plant_humidity_ranges[plant]
            response = f"{plant}의 습도 범위는 {min_range}% 이상 {max_range}% 미만입니다."
            plantt = {
                "result": response
            }
            humidity = dht_device.humidity
            
            if humidity >= 20 and humidity < 60:
                GPIO.output(G_LED, GPIO.HIGH)
                time.sleep(10)
                GPIO.output(G_LED, GPIO.LOW)
            
            elif humidity < 20:
                GPIO.output(Y_LED, GPIO.HIGH)
                p = GPIO.PWM(BUZZER, 100)
                p.start(100)
                p.ChangeDutyCycle(90)
                for i in range(6):
                    p.ChangeFrequency(scale[list_A[i]])
                    time.sleep(term[i])        
                p.stop()
                time.sleep(10)
                GPIO.output(Y_LED, GPIO.LOW)


            elif humidity >= 60:
                GPIO.output(R_LED, GPIO.HIGH)
                p = GPIO.PWM(BUZZER, 100)
                p.start(100)
                p.ChangeDutyCycle(90)
                for j in range(6):
                    p.ChangeFrequency(scale[list_B[j]])
                    time.sleep(term[j])
                p.stop()
                time.sleep(10)
                GPIO.output(R_LED, GPIO.LOW)

            sensing = {
                
                "humidity": humidity
            
            }

            value = json.dumps(sensing, ensure_ascii=False)
            client.publish(MQTT_PUB_TOPIC, value)
            print(value)

        except RuntimeError:
            time.sleep(2)
            continue
            
        time.sleep(10)

except KeyboardInterrupt:
    print("사용자가 프로그램을 종료했습니다.")
    
finally:
    dht_device.exit()
    client.disconnect()
