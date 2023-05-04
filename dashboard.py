import paho.mqtt.client as mqtt
from paho.mqtt import client as mqtt_client
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards
import altair as alt

# Configurações do MQTT
MQTT_BROKER = "broker.emqx.io"
client_id = 'pedro'
MQTT_PORT = 1883
MQTT_TOPIC1 = "topics/volume"
MQTT_TOPIC2 = "topics/startTime"
MQTT_USER = "user"
MQTT_PASSWORD = "password"

st.set_page_config(page_title="Water Flow Dashboard",page_icon="✅",layout="wide")
# dashboard title
st.title("Water Flow Dashboard")
# creating a single-element container
placeholder = st.empty()

# Dados recebidos do MQTT
df1 = pd.DataFrame(columns=["time", "volume"])
df2 = pd.DataFrame(columns=["time", "startTime"])

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")

        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT)
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global df1, df2
        try:
            payload = float(msg.payload.decode())
            timestamp = pd.Timestamp.now()
            if msg.topic == MQTT_TOPIC1:
                df1 = df1.append({"time": timestamp, "volume": payload}, ignore_index=True)
            elif msg.topic == MQTT_TOPIC2:
                df2 = df2.append({"time": timestamp, "startTime": payload}, ignore_index=True)

            with placeholder.container():

                    kpi1, kpi2 = st.columns(2)
                    
                    kpi1.metric(
                        label="Média de volume gasto (mL)",
                        value=round(df1.volume.mean(),2),
                        delta=round(df1.volume.mean(),2) - round(df1.iloc[:-1].volume.mean(),2)
                    )

                    kpi2.metric(
                        label="Média de tempo de torneira ligada (segundos)",
                        value=round(df2.startTime.mean(),2),
                        delta=round(df2.startTime.mean(),2) - round(df2.iloc[:-1].startTime.mean(),2)
                    )

                    fig = px.line(df1, x='time', y='volume',
                                  title='Variação do volume de água por data', markers=True)

                    fig2 = px.line(df2, x="time", y="startTime",title='Variação do tempo de torneira ligada por data',markers=True)

                    kpi1.write(fig)
                    kpi2.write(fig2)
                    style_metric_cards()
        except Exception as e:
            print(e)
            
    client.subscribe([(MQTT_TOPIC1, 0), (MQTT_TOPIC2, 0)])
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()


