from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)

# Temporary storage for MQTT messages
temp_data = {}

# MongoDB settings
MONGO_URI = "mongodb+srv://ghaitsageanoveffa:Polumer24@pollutionmeasurement.8t9pk8x.mongodb.net/?retryWrites=true&w=majority&appName=PollutionMeasurement"
client = MongoClient(MONGO_URI)
db = client.Polumer
collection = db.sensor

# MQTT settings
MQTT_BROKER = "a40113311e554f6daff3add1404152bb.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_TOPIC_SUHU = "dht11/Suhu"
MQTT_TOPIC_KELEMBAPAN = "dht11/Kelembapan"
MQTT_TOPIC_CO2 = "mq135/CO2"
MQTT_TOPIC_CO = "mq135/CO"
MQTT_TOPIC_UDARA = "mq135/Udara"
MQTT_TOPIC_INTENSITAS_CAHAYA = "ldr/IntensitasCahaya"
MQTT_TOPIC_CAHAYA = "ldr/Cahaya"
MQTT_TOPIC_UV_INDEX = "uv/Index"
MQTT_USERNAME = "MuhammadGhaitsa"
MQTT_PASSWORD = "Polumer24"

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC_SUHU)
    client.subscribe(MQTT_TOPIC_KELEMBAPAN)
    client.subscribe(MQTT_TOPIC_CO2)
    client.subscribe(MQTT_TOPIC_CO)
    client.subscribe(MQTT_TOPIC_UDARA)
    client.subscribe(MQTT_TOPIC_INTENSITAS_CAHAYA)
    client.subscribe(MQTT_TOPIC_CAHAYA)
    client.subscribe(MQTT_TOPIC_UV_INDEX)

def on_message(client, userdata, msg):
    global temp_data
    payload = msg.payload.decode()
    topic = msg.topic
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Pesan yang diterima '{payload}' pada topik '{topic}'")
    
    if topic == MQTT_TOPIC_SUHU:
        temp_data['Suhu'] = float(payload)
    elif topic == MQTT_TOPIC_KELEMBAPAN:
        temp_data['Kelembapan'] = float(payload)
    elif topic == MQTT_TOPIC_CO2:
        temp_data['CO2'] = float(payload)
    elif topic == MQTT_TOPIC_CO:
        temp_data['CO'] = float(payload)
    elif topic == MQTT_TOPIC_UDARA:
        temp_data['Udara'] = payload  # Simpan kualitas udara sebagai string
    elif topic == MQTT_TOPIC_INTENSITAS_CAHAYA:
        temp_data['Intensitas Cahaya'] = float(payload)
    elif topic == MQTT_TOPIC_CAHAYA:
        temp_data['Cahaya'] = payload  # Simpan intensitas cahaya sebagai string
    elif topic == MQTT_TOPIC_UV_INDEX:
        temp_data['UV Index'] = float(payload)

    # Periksa jika semua nilai sudah tersedia
    if all(k in temp_data for k in ('Suhu', 'Kelembapan', 'CO2', 'CO', 'Udara', 'Intensitas Cahaya', 'Cahaya', 'UV Index')):
        data = {
            'timestamp': timestamp,
            'Suhu': temp_data['Suhu'],
            'Kelembapan': temp_data['Kelembapan'],
            'CO2': temp_data['CO2'],
            'CO': temp_data['CO'],
            'Udara': temp_data['Udara'],
            'Intensitas Cahaya': temp_data['Intensitas Cahaya'],
            'Cahaya': temp_data['Cahaya'],
            'UV Index': temp_data['UV Index']
        }
        # Periksa apakah data yang sama sudah ada di MongoDB
        existing_data = collection.find_one(data)
        if existing_data:
            print(f"Data sudah ada di MongoDB: {data}")
        else:
            collection.insert_one(data)  # Masukkan data ke MongoDB
            print(f"Data dimasukkan ke MongoDB: {data}")
        temp_data = {}  # Bersihkan temp_data setelah penyimpanan

client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
client.tls_set()

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

@app.route('/sensor/data', methods=['GET'])
def get_data():
    data = list(collection.find({}, {"_id": 0}))  # Ambil data dari MongoDB
    print(f"Daftar data pada permintaan GET: {data}")
    return jsonify(data), 200

@app.route('/sensor/data/search', methods=['GET'])
def search_data():
    timestamp = request.args.get('timestamp')
    if not timestamp:
        return jsonify({"error": "Parameter timestamp tidak ditemukan"}), 400

    data = list(collection.find({"timestamp": timestamp}, {"_id": 0}))
    return jsonify(data), 200

@app.route('/sensor/data/search_after', methods=['GET'])
def search_data_after():
    start_date = request.args.get('start_date')
    if not start_date:
        return jsonify({"error": "Parameter start_date tidak ditemukan"}), 400

    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({"error": "Format tanggal tidak valid. Gunakan 'YYYY-MM-DD HH:MM:SS'"}), 400

    data = list(collection.find({"timestamp": {"$gte": start_date}}, {"_id": 0}))
    return jsonify(data), 200

@app.route('/sensor/data/delete', methods=['DELETE'])
def delete_data():
    timestamp = request.args.get('timestamp')
    if not timestamp:
        return jsonify({"error": "Parameter timestamp tidak ditemukan"}), 400

    result = collection.delete_many({"timestamp": timestamp})
    return jsonify({"message": f"Terhapus {result.deleted_count} dokumen"}), 200

@app.route('/sensor/cahaya', methods=['GET'])
def get_cahaya():
    if 'Cahaya' in temp_data:
        cahaya = temp_data['Cahaya']
    else:
        cahaya = "Data intensitas cahaya belum tersedia"
    return jsonify({"Cahaya": cahaya}), 200

if __name__ == '__main__':
    app.run(port=5000)
