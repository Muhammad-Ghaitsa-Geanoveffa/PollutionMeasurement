import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMA

# Pengaturan MongoDB
MONGO_URI = "mongodb+srv://ghaitsageanoveffa:Polumer24@pollutionmeasurement.8t9pk8x.mongodb.net/?retryWrites=true&w=majority&appName=PollutionMeasurement"
client = MongoClient(MONGO_URI)
db = client.Polumer
collection = db.sensor

# Fungsi untuk mengambil data dari MongoDB
def fetch_data():
    data = list(collection.find({}, {"_id": 0}))
    return pd.DataFrame(data)

# Fungsi untuk memberikan rekomendasi berdasarkan Udara dan UV Index
def get_recommendation(sensor_name, value):
    if sensor_name == 'CO2':
        if value <= 1000:
            return "Selalu jaga lingkungan sekitarmu!"
        elif value <= 2000:
            return "Selalu jaga lingkungan sekitarmu!!"
        elif value <= 5000:
            return "Gunakan masker dan kurangi berkegiatan di luar ruangan!"
        else:
            return "Hindari berada di dalam ruangan!"
    elif sensor_name == 'UV Index':
        if value <= 5:
            return "Selamat beraktivitas dan selalu menjaga kesehatan tubuh dari paparan sinar matahari!"
        elif value <= 7:
            return "Gunakan sunscreen atau pakaian tertutup untuk berkegiatan di luar ruangan!"
        elif value <= 10:
            return "Disarankan untuk tidak berkegiatan di luar ruangan!"
        else:
            return "Hindari berkegiatan di luar ruangan karena risiko kulit terbakar!"

# Fungsi untuk menampilkan dashboard data sensor
def show_dashboard(data):
    st.title('Polusi Hari Ini')

    if not data.empty:
        # Menghitung rata-rata CO2, CO, dan UV Index untuk seluruh data
        avg_co2 = data['CO2'].mean() if 'CO2' in data.columns else None
        avg_co = data['CO'].mean() if 'CO' in data.columns else None
        avg_uv_index = data['UV Index'].mean() if 'UV Index' in data.columns else None

        # Menampilkan rata-rata CO2, CO, dan UV Index dalam teks besar di tengah
        col1, col2, col3 = st.columns(3)
        with col1:
            if avg_co2 is not None:
                st.metric(label="CO2", value=f"{avg_co2:.2f} ppm", delta=get_recommendation_color('CO2', avg_co2))
                st.info(get_recommendation('CO2', avg_co2))
        with col2:
            if avg_co is not None:
                st.metric(label="CO", value=f"{avg_co:.2f} ppm")
        with col3:
            if avg_uv_index is not None:
                st.metric(label="Indeks UV", value=f"{avg_uv_index:.2f}", delta=get_recommendation_color('UV Index', avg_uv_index))
                st.info(get_recommendation('UV Index', avg_uv_index))

        # Menghitung dan menampilkan grafik batang untuk data rata-rata
        avg_data = {
            'CO2': avg_co2,
            'CO': avg_co,
            'UV Index': avg_uv_index,
            'Suhu': data['Suhu'].mean() if 'Suhu' in data.columns else None,
            'Kelembapan': data['Kelembapan'].mean() if 'Kelembapan' in data.columns else None,
            'Intensitas Cahaya': data['Intensitas Cahaya'].mean() if 'Intensitas Cahaya' in data.columns else None
        }

        avg_df = pd.DataFrame(list(avg_data.items()), columns=['Sensor', 'Rata-rata'])
        avg_df = avg_df.dropna()

        colors = {
            'CO2': 'lightgreen',
            'CO': 'lightcoral',
            'UV Index': 'purple',
            'Suhu': 'lightblue',
            'Kelembapan': 'darkblue',
            'Intensitas Cahaya': 'gray'
        }

        bar_fig = px.bar(avg_df, x='Sensor', y='Rata-rata', title='Rata-rata Data Sensor', 
                         labels={'Sensor': 'Sensor', 'Rata-rata': 'Rata-rata'},
                         color='Sensor', color_discrete_map=colors)
        st.plotly_chart(bar_fig)

    else:
        st.write("Tidak ada data untuk ditampilkan.")

# Fungsi untuk mendapatkan warna delta berdasarkan nilai
def get_recommendation_color(sensor_name, value):
    if sensor_name == 'CO2':
        if value <= 1000:
            return "Udara Aman"
        elif value <= 2000:
            return "Udara Sedang"
        elif value <= 5000:
            return "Udara Tidak Sehat"
        else:
            return "Udara Bahaya"
    elif sensor_name == 'CO':
        if value <= 25:
            return "Udara Aman"
        elif value <= 50:
            return "Udara Sedang"
        elif value <= 100:
            return "Udara Tidak Sehat"
        else:
            return "Udara Bahaya"
    elif sensor_name == 'UV Index':
        if value <= 5:
            return "UV Aman"
        elif value <= 7:
            return "UV Tinggi"
        elif value <= 10:
            return "UV Sangat Tinggi"
        else:
            return "UV Bahaya"

# Fungsi untuk menampilkan prediksi data sensor
def show_sensor_prediction(data):
    st.title('Data & Prediksi')

    # Menampilkan grafik untuk tipe data yang dipilih
    data_type = st.radio("Pilih tipe data untuk prediksi", ["CO2", "CO", "UV Index", "Suhu", "Kelembapan", "Intensitas Cahaya"], key="prediction")

    # Hanya ambil kolom timestamp dan data_type
    filtered_data = data[['timestamp', data_type]].dropna()

    if not filtered_data.empty:
        def display_graph(data, column, label, line_color):
            st.subheader(f'Data dan Prediksi {label}')
            fig = px.line(data, x='timestamp', y=column, title=f'{label} Data', labels={'timestamp': 'Waktu', column: label}, color_discrete_sequence=[line_color])
            st.plotly_chart(fig)
            forecast = predict_arima(data, column, periods=24)
            forecast_fig = px.line(forecast, x='timestamp', y=column, title=f'Prediksi {label}', labels={'timestamp': 'Waktu', column: label}, color_discrete_sequence=[line_color])
            st.plotly_chart(forecast_fig)

        # Fungsi untuk prediksi menggunakan model ARIMA
        def predict_arima(data, column, periods):
            # Persiapkan data untuk ARIMA
            df_arima = data[['timestamp', column]].rename(columns={'timestamp': 'ds', column: 'y'})
            df_arima.set_index('ds', inplace=True)

            # Fit model ARIMA
            model = ARIMA(df_arima, order=(1, 1, 1))
            model_fit = model.fit()

            # Buat prediksi
            forecast = model_fit.get_forecast(steps=periods)
            next_day = (df_arima.index[-1] + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            forecast_index = pd.date_range(start=next_day, periods=periods, freq='H')
            forecast_df = pd.DataFrame({'timestamp': forecast_index, column: forecast.predicted_mean.values})

            return forecast_df

        colors = {
            'CO2': 'lightgreen',
            'CO': 'lightcoral',
            'UV Index': 'purple',
            'Suhu': 'lightblue',
            'Kelembapan': 'darkblue',
            'Intensitas Cahaya': 'gray'
        }

        display_graph(filtered_data, data_type, data_type, colors[data_type])

    else:
        st.write(f"Tidak ada data untuk {data_type}.")

# Fungsi utama untuk menjalankan aplikasi Streamlit
def main():
    data = fetch_data()

    if data.empty:
        st.write("Tidak ada data di MongoDB.")
        return

    data['timestamp'] = pd.to_datetime(data['timestamp'])

    # Menu navigasi menggunakan radio button dengan key yang unik
    page = st.radio("Pilih Halaman", ["Dashboard", "Data & Prediksi",])

    if page == "Dashboard":
        show_dashboard(data)

    elif page == "Data & Prediksi":
        show_sensor_prediction(data)

# Menjalankan aplikasi Streamlit
if __name__ == '__main__':
    st.title('POLLUTION MEASUREMENT')
    main()
