import streamlit as st ## low-code web app framework
import pandas as pd  ##pandas to najpopularniejsza biblioteka do manipulacji i analizy danych

with st.sidebar:
    st.header('Panel boczny') #dodanie panelu bocznego
    st.code('fragment kodu')
    st.selectbox('Wybierz opcję', options=["Opcja1", "Opcja 2", "Opcja 3"])
st.title("Moja apka")
tab1, tab2 = st.tabs(["Opisy", "Dane"])

with tab1:
    with st.expander("Opisy"):    #kontener do rozwijania
        st.subheader("To jest nagłówek")
        st.subheader("To jest podnagłówek")
        st.text("To jest zwykły tekst")
        st.markdown("To jest pogrubiony tekst napisany w _Markdown_")

    url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv"

    df = pd.read_csv(url) ##czytanie z pliku csv
    st.dataframe(df.head()) #dataframe to tabelka danych (head to jest pierwsze 5 rekordów)
    #st.dataframe(df.tail()) #tail to jest ostatnie 5 wierszy/rekordów
    ###
    #Podstawowa statystyka z csv
    ###
    st.dataframe(df.describe())
    st.dataframe(df['sex'].value_counts()) #liczba wystąpień wartości w kolumnie
    st.dataframe(df.groupby('day')['tip'].mean().sort_values(ascending=False)) #średnia wartość napiwku w podziale na dni, posortowane malejąco


with tab2:
    url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv"
    df_bis = pd.read_csv(url)
    # --- Tytuł
    st.subheader("Analiza napiwków w restauracji")
    st.write("Przykładowe dane z biblioteki Seaborn") #Seaborn to biblioteka ogólnodostępna
    # --- Filtry
    day_filter = st.multiselect("Wybierz dni tygodnia", options=df_bis['day'].unique()) #st.multiselect to wybieranie kilka spośród wielu (unique to wybieranie unikalnych wartości(nie ma duplikatów))
    sex_filter = st.selectbox("Wybierz płeć", options = ["Wszyscy"] + df_bis['sex'].unique().tolist(), index=None) # tolist z wartości z dataframe robi listę
    # --- Wyświetlenie przefiltrowanych danych
    filtered_df = df_bis[df_bis['day'].isin(day_filter)] #filtracja list # isin sprawdza czy jakaś wartość jest w liście i zwraca tylko te, które mają boolean = True
    if sex_filter != "Wszyscy": #filtracja stringów  # != w pythonie to zaprzeczenie
        filtered_df = filtered_df[filtered_df['sex'] == sex_filter] # == to w pythonie po prostu równanie
    # --- Wyświetlanie tabeli
    st.subheader("Przefiltrowane dane")
    st.dataframe(filtered_df)
    # --- Podstawowa statystyka
    avg_tip = round(filtered_df['tip'].mean(), 2)
    sum_tip = round(filtered_df['tip'].sum(), 2)
    max_tip = round(filtered_df['tip'].max(), 2)
    min_tip = round(filtered_df['tip'].min(), 2)
    median_tip = round(filtered_df['tip'].median(), 2)

    avg_total = round(filtered_df['total_bill'].mean(), 2)
    sum_total = round(filtered_df['total_bill'].sum(), 2)
    max_total = round(filtered_df['total_bill'].max(), 2)
    min_total = round(filtered_df['total_bill'].min(), 2)
    median_total = round(filtered_df['total_bill'].median(), 2)

    num_bills = filtered_df.shape[0] #liczba rachunków po filtracji
    avg_tip_pct = round((filtered_df['tip'] / filtered_df['total_bill']).mean() * 100, 2) #średni procent napiwku, zaokrąglony do 2 miejsc po przecinku

    if filtered_df.empty:
        st.warning("Wybierz kryteria filtracji, aby zobaczyc dane")
    else:
        st.subheader("Wyświetlanie danych statystycznych") # mogę jeszcze dać "icon", aby dodać emotkę
        col1, col2, col3 = st.columns([1,1,1])
        col1.metric(label="Średni napiwek", value=f"{avg_tip}")
        col2.metric(label="Średni napiwek", value=f"{avg_total}")
        col3.metric(label="Liczba rachunków", value=f"{num_bills}")

        col1.metric(label="Napiwek - min", value=f"{min_tip}")
        col2.metric(label="Napiwek - max", value=f"{max_tip}")
        col3.metric(label="Napiwek - mediana", value=f"{median_tip}")
        
        col1.metric(label="Rachunek - min", value=f"{min_total}")
        col2.metric(label="Rachunek - max", value=f"{max_total}")
        col3.metric(label="Rachunek - mediana", value=f"{median_total}")

        st.success(f"{avg_tip_pct}%" + " Średni procent napiwku od rachunku")
        st.info(f"suma napiwków: {sum_tip}" + " |" + f"suma rachunków: {sum_total}")
        st.area_chart(filtered_df['total_bill'])
        
        


