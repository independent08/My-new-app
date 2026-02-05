import streamlit as st
import pandas as pd
import plotly.express as px 
from pmdarima import auto_arima
import plotly.graph_objects as go
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.exponential_smoothing.ets import ETSModel
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

def mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


Arima, HoltWinters, ETS = st.tabs(["Arima", "Holt-Winters", "ETS"])

with Arima:
    uploaded_file = st.file_uploader("Wrzuć CSV z danymi", type= "csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, sep=",")
        mapowanie_kwartalu = {"I": 1, "II": 2, "III": 3, "IV": 4}
        df["Rok"] = df["Kwartał"].str.split().str[1].astype(int)
        df["Kwartał"] = df["Kwartał"].str.replace("\xa0","").str.split().str[0].map(mapowanie_kwartalu)
        for city in ["Kraków", "Warszawa", "Wrocław"]:
            df[city] = df[city].astype(str).str.replace("\xa0","").astype(int)
        df["Rok_kwartał"] = df["Rok"].astype(str) + "Q" + df["Kwartał"].astype(str)
        df_arima = df.copy()
        df_arima = df.set_index("Rok_kwartał")

        # --- Expander: MAE/RMSE na ostatnich 8 kwartałach historycznych ---
        with st.expander(":blue[Precyzyjność modelu ARIMA – ostatnie 8 kwartałów]"):
            test_start_idx = df_arima.index.get_loc("2023Q3")
            test_end_idx = df_arima.index.get_loc("2025Q2")
            last8 = df_arima.iloc[test_start_idx:test_end_idx+1]

            results = []
            for city in ["Kraków", "Warszawa", "Wrocław"]:
                series = df_arima[city]
                train = series.iloc[:test_end_idx+1]  # model na danych do II 2025
                model = auto_arima(train, seasonal=True, m=4,
                                trace=False, error_action="ignore", suppress_warnings=True)
                forecast = model.predict(n_periods=8)  # prognoza na te same 8 punktów
                
                mae = mean_absolute_error(last8[city], forecast)
                rmse = np.sqrt(mean_squared_error(last8[city], forecast))
                mape_val = mape(last8[city], forecast)
                results.append({"Miasto": city, "MAE": round(mae,2), "RMSE": round(rmse,2), "MAPE": round(mape_val,2)})

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=last8.index, y=last8[city],
                                        mode="lines+markers", name="Historyczne"))
                fig.add_trace(go.Scatter(x=last8.index, y=forecast,
                                        mode="lines+markers", name="Prognoza ARIMA"))
                fig.update_layout(title=f"{city} – ARIMA ostatnie 8 kwartałów",
                                xaxis_title="Kwartał", yaxis_title="Cena")
                st.plotly_chart(fig)

            st.subheader("Błędy prognozy na danych historycznych")
            st.dataframe(pd.DataFrame(results))

        with st.expander(":green[Wykres]"):
            fig = px.line(
                df,
                x="Rok_kwartał",
                y=["Kraków", "Warszawa", "Wrocław"],
                labels={"value": "Cena mieszkań", "Rok": "Data", "variable": "Miasto"},
                title="Ceny mieszkań w miastach"
            )

            st.plotly_chart(fig, use_container_width=True)

        with st.expander(":green[Podstawowa statystyka]"):
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

with HoltWinters:
    uploaded_file = st.file_uploader("Wrzuć CSV z danymi", type= "csv", key="HoltWinters")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, sep=",")
        #df
        
        df["Rok"] = df["Kwartał"].str.split().str[1].astype("int") #zmieniam stringi kolumny "rok" na wartość numeryczną
        mapowanie_kwartalu = {"I": 1, "II": 2, "III": 3, "IV": 4}
        df["Kwartał"] = (df["Kwartał"].str.replace("\xa0", "", regex=False).str.split().str[0].map(mapowanie_kwartalu))

        for city in ["Kraków", "Warszawa", "Wrocław"]:
            df[city] = df[city].astype(str).str.replace("\xa0", "").astype(int)
        
        df["t"] = df["Rok"] + (df["Kwartał"] - 1) / 4
        df = df.sort_values("t").set_index("t")
        df_hw = df.copy()


        with st.expander(":blue[Precyzyjność modelu Holt-Winters (MAE / RMSE) – ostatnie 8 kwartałów historycznych]"):
            # Definicja okresu walidacyjnego
            test_periods = 8
            test_start = 2023.5  # III 2023
            test_end = 2025.25   # II 2025

            results = []

            for city in ["Kraków", "Warszawa", "Wrocław"]:
                series = df_hw[city].dropna()
                # Wyciągamy ostatnie 8 kwartałów historycznych
                series_test = series[(series.index >= test_start) & (series.index <= test_end)]
                
                if len(series_test) != test_periods:
                    st.warning(f"{city}: brak pełnych 8 kwartałów – pomijam")
                    continue

                # Tworzymy model na pełnym szeregu historycznym do test_end (włącznie)
                train = series[series.index <= test_end]
                model = ExponentialSmoothing(train, trend="add", seasonal="add", seasonal_periods=4).fit(optimized=True)
                
                # Prognoza na 8 kwartałów historycznych (nakładająca się z serią testową)
                forecast_hist = model.forecast(test_periods)

                # Obliczamy MAE i RMSE wyłącznie na danych historycznych
                mae = mean_absolute_error(series_test, forecast_hist)
                rmse = np.sqrt(mean_squared_error(series_test, forecast_hist))
                mape_val = mape(series_test, forecast_hist)
                results.append({"Miasto": city, "MAE": round(mae,2), "RMSE": round(rmse,2), "MAPE": round(mape_val, 2)})

                # Etykiety kwartalne dla osi X
                x_test = [f"{int(t)}Q{int(round((t-int(t))*4)+1)}" for t in series_test.index]

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=x_test, y=series_test, mode="lines+markers", name="Historyczne"))
                fig.add_trace(go.Scatter(x=x_test, y=forecast_hist, mode="lines+markers", name="Prognoza modelu HW"))
                fig.update_layout(
                    title=f"{city} - Holt-Winters (ostatnie 8 kwartałów historycznych)",
                    xaxis_title="Kwartał",
                    yaxis_title="Cena"
                )
                st.plotly_chart(fig)

            st.subheader("Błędy prognozy na danych historycznych")
            st.dataframe(pd.DataFrame(results))


        with st.expander("Model Holt-Winters - prognoza cen"):
            st.subheader("Holt-Winters - prognoza (trend + sezonowość)")

            def fit_hw(city):
                st.write(f"### {city}")
                series = df[city]
                model = ExponentialSmoothing(series, trend="add", seasonal="add", seasonal_periods=4).fit(optimized=True)
                forecast_periods=8
                forecast = model.forecast(forecast_periods)
                future_t = [series.index.max() + i * 0.25
                            for i in range(1, forecast_periods + 1)]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=series.index, y=series, mode="lines", name="Historyczne"))
                fig.add_trace(go.Scatter(x=future_t, y=forecast, mode="lines", name="Prognoza"))
                fig.update_layout(title=f"Prognoza cen mieszkań - {city}(Holt-Winters)",xaxis_title="Rok", yaxis_title="Cena")
                st.plotly_chart(fig)

                df_forecast = pd.DataFrame({
                    "Rok": future_t,
                    f"{city}_forecast": forecast
                })
                st.write("Prognoza")
                st.dataframe(df_forecast)

                return model

            for city in ["Kraków", "Warszawa", "Wrocław"]:
                fit_hw(city)

with ETS:
    uploaded_file = st.file_uploader("Wrzuć CSV z danymi", type= "csv", key="ets")
    if uploaded_file is not None:
        df_ets = pd.read_csv(uploaded_file, sep=",")
        
        df_ets["Rok"] = df_ets["Kwartał"].str.split().str[1].astype("int") #zmieniam stringi kolumny "rok" na wartość numeryczną
        mapowanie_kwartalu = {"I": 1, "II": 2, "III": 3, "IV": 4}
        df_ets["Kwartał"] = (df_ets["Kwartał"].str.replace("\xa0", "", regex=False).str.split().str[0].map(mapowanie_kwartalu))

        for city in ["Kraków", "Warszawa", "Wrocław"]:
            df_ets[city] = df_ets[city].astype(str).str.replace("\xa0", "").astype(int)
        
        df_ets["t"] = df_ets["Rok"] + (df_ets["Kwartał"] - 1) / 4
        df_ets = df_ets.sort_values("t").set_index("t")
        
        with st.expander(":violet[Precyzyjność modelu ETS (MAE / RMSE / MAPE) – ostatnie 8 kwartałów historycznych]"):

            test_periods = 8
            test_start = 2023.5   # III 2023
            test_end = 2025.25    # II 2025

            results = []

            for city in ["Kraków", "Warszawa", "Wrocław"]:
                series = df_ets[city].dropna()

                series_test = series[
                    (series.index >= test_start) & (series.index <= test_end)
                ]

                if len(series_test) != test_periods:
                    st.warning(f"{city}: brak pełnych 8 kwartałów – pomijam")
                    continue

                train = series[series.index <= test_end]

                model = ETSModel(
                    series,
                    error="add",
                    trend="add",
                    seasonal="add",
                    seasonal_periods=8
                ).fit()


                forecast_hist = model.forecast(test_periods)

                mae = mean_absolute_error(series_test, forecast_hist)
                rmse = np.sqrt(mean_squared_error(series_test, forecast_hist))
                mape_val = mape(series_test, forecast_hist)

                results.append({
                    "Miasto": city,
                    "MAE": round(mae, 2),
                    "RMSE": round(rmse, 2),
                    "MAPE": round(mape_val, 2)
                })

                x_test = [
                    f"{int(t)}Q{int(round((t - int(t)) * 4) + 1)}"
                    for t in series_test.index
                ]

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=x_test,
                    y=series_test,
                    mode="lines+markers",
                    name="Historyczne"
                ))
                fig.add_trace(go.Scatter(
                    x=x_test,
                    y=forecast_hist,
                    mode="lines+markers",
                    name="Prognoza ETS"
                ))

                fig.update_layout(
                    title=f"{city} – ETS (ostatnie 8 kwartałów historycznych)",
                    xaxis_title="Kwartał",
                    yaxis_title="Cena"
                )

                st.plotly_chart(fig, use_container_width=True)

            st.subheader("Błędy prognozy na danych historycznych")
            st.dataframe(pd.DataFrame(results))
        with st.expander("Model ETS - prognoza cen"):
            st.subheader("ETS - prognoza (trend + sezonowość + błąd)")

            def fit_ets(city):
                st.write(f"### {city}")

                series = df_ets[city]

                model = ETSModel(
                    series,
                    error="add",
                    trend="add",
                    seasonal="add",
                    seasonal_periods=8
                ).fit()

                forecast_periods = 8
                forecast = model.forecast(forecast_periods)

                future_t = [
                    series.index.max() + i * 0.25
                    for i in range(1, forecast_periods + 1)
                ]

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=series.index,
                    y=series,
                    mode="lines",
                    name="Historyczne"
                ))
                fig.add_trace(go.Scatter(
                    x=future_t,
                    y=forecast,
                    mode="lines",
                    name="Prognoza"
                ))

                fig.update_layout(
                    title=f"Prognoza cen mieszkań – {city} (ETS)",
                    xaxis_title="Rok",
                    yaxis_title="Cena"
                )

                st.plotly_chart(fig, use_container_width=True)

                df_forecast = pd.DataFrame({
                    "Rok": future_t,
                    f"{city}_forecast": forecast
                })

                st.write("Prognoza")
                st.dataframe(df_forecast)

            for city in ["Kraków", "Warszawa", "Wrocław"]:
                fit_ets(city)
