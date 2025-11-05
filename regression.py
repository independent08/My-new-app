import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import SGDRegressor
from sklearn.preprocessing import StandardScaler
import plotly.express as px

#--------------------------------
#Generowanie przykładowych danych
#np.random.seed(42) — ustawia ziarenko losowości, żeby wyniki były powtarzalne (ten sam „los” przy każdym uruchomieniu).
#n = 5000 — liczba wygenerowanych próbek.
#miasta i ceny_bazowe — lista miast i słownik z cenami bazowymi przypisanymi do każdego miasta.
#--------------------------------

np.random.seed(53)
n = 2000
miasta = ['Warszawa', 'Kraków', 'Wrocław', 'Gdańsk', 'Poznań']

ceny_bazowe = {
    "Warszawa": 18000,
    "Kraków": 15000,
    "Wrocław": 13000,
    "Gdańsk": 14500,
    "Poznań": 12000
}

#--------------------------------
#Tworzenie cech
#np.random.choice(miasta, n) — losujemy n etykiet miast (każda próbka ma miasto).
#np.random.randint(20, 121, n) — losujemy wielkość mieszkania w m² (20–120).
#wiek_budynku — losujemy wiek budynku 0–100.
#pietro — losujemy piętro 0–10.
#---------------------------------

miasto = np.random.choice(miasta, n)  
powierzchnia = np.random.randint(20, 121, n) 
wiek_budynku = np.random.randint(0, 101, n) 
pietro = np.random.randint(0, 11, n) 
#---------------------------------
#Genererowanie targetu (ceny) - pętla
#base — cena bazowa dla danego miasta.
#wsp_pietro = 1 + (pietro / 20) — prosty mnożnik: wyższe piętro → drożej (np. piętro 10 → współczynnik 1.2~).
#noise = np.random.normal(0, base) — losowy szum o średniej 0 i odchyleniu standardowym ~base.
#cena — wzór tworzący cenę: powierzchnia × base × korekta od wieku × korekta piętra + szum. Wynik dodawany do listy.
#---------------------------------
ceny = []

for i in range(n):
    base = ceny_bazowe[miasto[i]] 
    wsp_pietra = 1 + (pietro[i] / 20) 
    noise = np.random.normal(0, base * 2) 
    cena = (
        powierzchnia[i] * base * (1 - wiek_budynku[i] / 500) * wsp_pietra + noise
    ) 
    ceny.append(cena) 

#----------------------------------
# Dataframe
# Tworzysz pandas.DataFrame z cechami i cenami.
#----------------------------------
df = pd.DataFrame({
    "Miasto": miasto,
    "Powierzchnia_m2": powierzchnia,
    "Wiek_budynku": wiek_budynku,
    "Piętro": pietro,
    "Cena_PLN": np.round(ceny, 2)
})

df

#st.scatter_chart(df, x = "Powierzchnia_m2", y = "Cena_PLN")
st.title("Interaktywna regresja iteracyjna - ceny mieszkań w Polsce")
st.markdown("""Interaktywny przykład pokazuje, 
            jak iteracyjna regresja (SGD) 
            uczy się przewidywać cenę mieszkania na podstawie jego
            powierzchni, wieku i piętra z możliwością regulacji liczby iteracji""")

wybrane_miasto = st.selectbox(":green[Wybierz miasto]", sorted(df["Miasto"].unique())) 
dane_miasto = df[df["Miasto"] == wybrane_miasto]

min_pow = dane_miasto["Powierzchnia_m2"].min()
max_pow = dane_miasto["Powierzchnia_m2"].max()
min_wiek = dane_miasto["Wiek_budynku"].min()
max_wiek = dane_miasto["Wiek_budynku"].max()
with st.sidebar:
    st.sidebar.header("Parametry mieszkania i modelu")
    powierzchnia_input = st.sidebar.slider("Powierzchnia mieszkania (m2)", min_pow, max_pow)
    wiek_input = st.sidebar.slider("Wiek budynku (lata)", min_wiek, max_wiek)
    pietro_input = st.sidebar.slider("Piętro", 0, 10)
    max_iter = st.sidebar.slider("Liczba iteracji uczenia modelu", 100, 5000, step=100) 

# --------------------------------
# regresja iteracyjna (sgd) - Stochastyczny spadek gradientu
# Przygotowanie cech (X) i targetu (y)
# X to macierz cech, y to wektor cen. Są to surowe dane z filtrowanego DataFrame.
#---------------------------------
 

X = dane_miasto[["Powierzchnia_m2", "Wiek_budynku", "Piętro"]]
y = dane_miasto["Cena_PLN"]

# --------------------------------
# Normalizujemy dane – żeby wartości były w podobnej skali
# Skalowanie / normalizacja
# StandardScaler usuwa średnią i dzieli przez odchylenie standardowe: cechy mają mean≈0 i std≈1.
# Skalujesz X i także y (target). Skalowanie y jest opcjonalne, ale sensowne przy algorytmach gradientowych — poprawia stabilność uczenia.
# reshape(-1, 1) bo StandardScaler oczekuje 2D; .ravel() żeby znowu mieć wektor 1D dla y_scaled.
#---------------------------------


scaler_X = StandardScaler()
scaler_y = StandardScaler()

X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y.values.reshape(-1, 1)).ravel()

# --------------------------------
# Tworzenie i trenowanie modelu SGD
# SGDRegressor(...) — tworzysz model. Parametry:
# max_iter=max_iter — maksymalna liczba epok (iteracji).
# tol=None — brak kryterium wczesnego stopu (czyli model wykona dokładnie max_iter epok).
# penalty=None — tutaj mała uwaga: różne wersje scikit-learn rozróżniają penalty='none' (string) i penalty=None. W nowszych wersjach poprawne wyłączenie regularizacji to 'none'. 
# random_state=42 — determinizm przy losowych elementach uczenia (np. shuffle).
# model.fit(X_scaled, y_scaled) — uczysz model na zeskalowanych danych. SGD uczy się iteracyjnie, aktualizując współczynniki przy każdej próbce / mini-batchu.
#----------------------------------

model = SGDRegressor(max_iter=max_iter, tol=None, penalty=None, random_state=42)
model.fit(X_scaled, y_scaled)

# --------------------------------
# Predykcja dla wybranych parametrów użytkownika
# scaler_X.transform(...) — musisz zastosować tę samą standaryzację co przy uczeniu.
# model.predict(...) — zwraca przewidywanie w skali znormalizowanej (y_scaled).
# scaler_y.inverse_transform — odwracasz skalowanie, żeby uzyskać cenę w PLN. Zwracasz 2D, dlatego indeksowanie [...,0][0].
#---------------------------------

X_user_scaled = scaler_X.transform([[powierzchnia_input, wiek_input, pietro_input]])
y_pred_scaled = model.predict(X_user_scaled)[0] #y_pred_scaled = 0.83 > wynik w skali śrdnia=0 a std=1
predicted_price = scaler_y.inverse_transform([[y_pred_scaled]])[0][0]
                                                                   
#wyniki
st.markdown(f"Szacowana cena mieszkania w {wybrane_miasto}: **{predicted_price} PLN**")
st.caption(f"Model uczony przez {max_iter} iteracji metodą gradientu prostego")

fig = px.scatter(
    dane_miasto,
    x = "Powierzchnia_m2",
    y= "Cena_PLN",
    color = "Wiek_budynku",
    title= f"Zależności między powierzchnią a ceną mieszkań w {wybrane_miasto}",
    opacity= 0.7,
    color_continuous_scale= "Viridis" #Inferno
)

fig.add_scatter(
    x=[powierzchnia_input],
    y=[predicted_price],
    mode="markers",
    marker=dict(size=12, color="red"),
    name="Predykcja"
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------
# Współczynników modelu
# model.coef_ — wektor współczynników dla cech, ale te współczynniki odnoszą się do znormalizowanych cech (bo trenowałeś na X_scaled). Nie są to bezpośrednio
#  „złotówki za 1 m2” — trzeba je zdeskalaować, jeśli chcesz interpretować w oryginalnej jednostce.
# Metryki: liczba iteracji i R²
# model.score(X_scaled, y_scaled) liczy R² na danych treningowych (znormalizowanych). Daje info jak dobrze model tłumaczy 
# wariancję danych — ale uwaga: to R² liczone na tym samym zbiorze, na którym uczono model (czyli optymistyczne).
#----------------------------------

st.subheader("Współczynniki modelu")
coef_df = pd.DataFrame({
    "Cechy": X.columns,
    "Współczynnik (znormalizowany)": np.round(model.coef_, 3)
    })

st.table(coef_df)

st.metric("Liczba iteracji", max_iter)
st.metric("Współczynnik dopasowania (R^2)", f"{model.score(X_scaled, y_scaled)}")