import streamlit as st
import datetime
import pandas as pd
st.title("Moja pierwsza aplikacja w Streamlit")
st.write(1+1)

def dodaj(): ## stworzenie funkcji
    a = st.number_input("podaj liczbę a", key="liczbaa")
    b = st.number_input("podaj liczbę b", key="liczbab")
    if st.button("Dodaj"):
        wynik = a + b
        st.success(f"Wynik: {wynik}")


st.divider()   
birthday = st.date_input("Kiedy masz urodziny?", value = None)
st.write("Masz urodziny dnia:", birthday)

st.divider()
uploaded_file = st.file_uploader("Upload data", type="csv")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df 


VIDEO_URL = "https://www.youtube.com/watch?v=DRFHklnN-SM&list=RDDRFHklnN-SM&start_radio=1"
st.video(VIDEO_URL, width="stretch", muted=True)