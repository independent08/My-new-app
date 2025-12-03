import streamlit as st
import pandas as pd
import plotly.express as px 
Regresja_liniowa, Random_forest, MLP = st.tabs(["Regresja_liniowa", "Random+forest", "MLP"])

with Regresja_liniowa:
    uploaded_file = st.file_uploader("Wrzuć CSV z danymi", type= "csv")
    if uploaded_file is not None:
        mapowanie_kwartalu = {"I": 1, "II": 2, "III": 3, "IV": 4}

        df = pd.read_csv(uploaded_file, sep=",")
        df["Rok"] = df["Kwartał"].str.split().str[1].astype("int") #zmieniam stringi kolumny "rok" na wartość numeryczną
        mapowanie_kwartalu = {"I": 1, "II": 2, "III": 3, "IV": 4}
        df["Kwartał"] = (df["Kwartał"].str.replace("\xa0", "", regex=False).str.split().str[0].map(mapowanie_kwartalu))
        df["Kraków"] = df["Kraków"].astype(str).str.replace("\xa0","").astype("int")
        df["Warszawa"] = df["Warszawa"].astype(str).str.replace("\xa0","").astype("int")
        df["Wrocław"] = df["Wrocław"].astype(str).str.replace("\xa0","").astype("int")
        df["Rok_kwartał"] = df["Rok"].astype(str) + "Q" + df["Kwartał"].astype(str)
        df
        with st.expander("Wykres"):
            fig = px.line(
                df,
                x="Rok_kwartał",
                y=["Kraków", "Warszawa", "Wrocław"],
                labels={"value": "Cena mieszkań", "Rok": "Data", "variable": "Miasto"},
                title="Ceny mieszkań w miastach"
            )

            st.plotly_chart(fig, use_container_width=True)

        with st.expander("Podstawowa statystyka"):
            kolumny_do_statystyki = ["Kraków", "Warszawa", "Wrocław"]
            st.write(df[kolumny_do_statystyki].describe())
        
