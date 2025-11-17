import streamlit as st

pages = {
    "Moja aplikacja": [
        st.Page("app.py", title="Strona główna"),
        st.Page("regression.py", title="Ceny mieszkań")
    ],
    "Moduły": [
        st.Page("utilities.py", title="Utilities")
    ]
}

st.logo("https://media2.dev.to/dynamic/image/width=1280,height=720,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.amazonaws.com%2Fuploads%2Farticles%2F6mk8aoa97px9xhi723o1.jpg", size="large")
st.sidebar.badge("Successs", icon=":material/check:", color="green")
pg = st.navigation(pages
                   #, position= "top"
                   )

pg.run()