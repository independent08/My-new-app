import streamlit as st
import pandas as pd
import plotly.express as px 
from pmdarima import auto_arima
import plotly.graph_objects as go


Arima, Random_forest, MLP = st.tabs(["Arima", "Random+forest", "MLP"])

with Arima:
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
        with st.expander("Model ARIMA - prognoza cen"):
            # Tworzymy oś czasu dla ARIMA
            df["t"] = df["Rok"] + (df["Kwartał"] - 1) / 4
            df_arima = df.set_index("t")

            def fit_arima(city):
                st.write(f"## {city}")
                series = df_arima[city]
                # Trenowanie modelu
                model = auto_arima(
                    series,
                    seasonal=True,
                    m=4,   # sezonowość kwartalna
                    trace=False,
                    error_action="ignore",
                    suppress_warnings=True
                )
                st.write(f"Model ARIMA: {model.order}, sezonowe: {model.seasonal_order}")
                # Prognoza na 8 kolejnych kwartałów (2 lata)
                forecast_periods = 8
                forecast = model.predict(forecast_periods)
                # Tworzymy kolejne kwartały na osi czasu
                last_t = df["t"].max()
                future_t = [last_t + i * 0.25 for i in range(1, forecast_periods + 1)]
                # Wykres
                fig = go.Figure()
                # Dane historyczne
                fig.add_trace(go.Scatter(
                    x=df_arima.index,
                    y=series,
                    mode="lines",
                    name="Historyczne"
                ))
                # Prognoza
                fig.add_trace(go.Scatter(
                    x=future_t,
                    y=forecast,
                    mode="lines",
                    name="Prognoza"
                ))
                fig.update_layout(
                    title=f"Prognoza cen mieszkań - {city} (ARIMA)",
                    xaxis_title="Rok",
                    yaxis_title="Cena"
                )
                fig.update_yaxes(
                    tickformat=".",
                    ticksuffix="k"
                )
                st.plotly_chart(fig)

                df_forecast = pd.DataFrame({
                    "Rok_kwartał": future_t,
                    f"{city}_forecast": forecast
                })
                df_forecast
                
                return model
            for city in ["Kraków", "Warszawa", "Wrocław"]:
                fit_arima(city)

            

