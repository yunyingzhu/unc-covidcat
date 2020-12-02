import webbrowser
import datetime
from PIL import Image
import streamlit as st
import pandas as pd
import numpy as np
import collections
import functools
import inspect
import textwrap
import altair as alt
import matplotlib.pyplot as plt
import base64
import time
import another
import sir


def valid_input_range(num):
    if num < 0 or num > 100:
        st.sidebar.error("Error! Please put a number between 0 and 100.")


def download_link(object_to_download, download_filename, download_link_text):
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


st.set_option('deprecation.showfileUploaderEncoding', False)

img = Image.open(r"logo.png")
st.image(img)
st.title('COVID-CAT')

st.markdown("COVID-CAT is a tool for hospital and emergency department (ED) managers, physicians, "
            "and health care workers to quickly convert predictions of future COVID-19 patient arrivals "
            "into predictions of future COVID-19 census levels in the ED, main hospital, and the ICU. ")

link = '[A complete description of the methodology is provided here]' \
       '(https://covidcat.web.unc.edu/files/2020/06/COVID-CAT.pdf)'

# if st.checkbox("Click here to see methodology", key="M"):
st.markdown("Below is a visual representation of what the mathematical model assumes regarding patient flow. "
            "COVID-19 suspected or confirmed patients arrive at the ED. After their stay in the ED is complete, "
            "they are either discharged from the ED, admitted to the main hospital COVID-19 unit, "
            "or admitted directly to the ICU. Patients who are admitted to the COVID-19 unit initially may later "
            "be transferred to the ICU if their condition deteriorates; "
            "similarly, patients who are first admitted to the ICU may be transferred to the COVID-19 unit "
            "in the hospital if their condition improves. The user may set the percentages of admission "
            "to the hospital and the ICU so as to account for these possibilities. "
            "However, it is important to note that the mathematical model assumes that patients start "
            "occupying a bed in the hospital and/or the ICU right after the patient’s stay in the ED is over "
            "and therefore the model would be biased towards capturing the bed demand in the hospital "
            "and the ICU slightly early.")
img2 = Image.open(r"Patient-Flow.png")
st.image(img2, width=720)

st.markdown("The methodology behind COVID-CAT is based on known results from queueing theory, "
            "more specifically the analysis of the $M_t/G/\infty$ queue, which assumes Poisson arrivals "
            "with time-variant rates and infinitely many servers.")
st.markdown(link, unsafe_allow_html=True)
st.markdown("One implicit assumption of the model is that all patients who arrive at "
            "the ED are admitted, and all patients who need hospitalization and/or ICU are also admitted. "
            "This means that the model assumes that there are no limits on the numbers of COVID-19 patients "
            "the ED, the hospital, and the ICU can have at any point in time. Therefore, the predictions made by "
            "COVID-CAT should be interpreted as bed capacities that would be needed to fully meet the patient "
            "demand at different points in time in the future. They should NOT be interpreted as what "
            "the actual census levels will be as those levels would be ED and hospital specific depending on "
            "the number of beds available as well as the policies the ED and the hospital would adopt to deal with "
            "the excess demand. By not making specific assumptions on bed capacities as well as such "
            "policy choices, we aim to make the tool useful not only for UNC but other EDs and hospitals as well.")

h = "2.4842813,2.2664266,1.7720543,1.5247536,1.3480775,1.5012884,1.7366275,2.9432267,2.5958554," \
    "3.9499138,4.9269258,6.2161113,6.2630417,5.927403,6.0686522,6.1514675,6.1395059,6.4808964,5.8744918," \
    "5.957078,5.4332597,4.7976382,4.1677685,3.4732549"

# h = h.split(",")
# h2 = []
# for i in h:
    # st.write(type(float(i)))
#     h2.append(float(i))
# st.write(h2)
# st.write(type(h2))

st.sidebar.subheader("SIR")
current_hospitalized = st.sidebar.number_input("Current Hospitalized Patients", value=50)
doubling_time = st.sidebar.number_input("Doubling Time in Days (Up to Today)", value=8)
hospitalized_rate = st.sidebar.number_input("Hospitalized Rate (%)", value=10.0)
infectious_days = st.sidebar.number_input("Infectious Days", value=10)
market_share = st.sidebar.number_input("Hospital Market Share (%)", value=30)
n_days = st.sidebar.number_input("Days To Predict From Today", value=20)
population = st.sidebar.number_input("Regional Population", value=100000)
recovered = st.sidebar.number_input("Recovered Patients", value=200)
mitigation_date = st.sidebar.date_input("Mitigation Date (YYYY-MM-DD)", value=datetime.date(2010, 10, 2))
relative_contact_rate = st.sidebar.number_input("Relative Contact Rate (%)", value=50.0)
arriving_rate = st.sidebar.number_input("Arriving Rate (%)", value=50.0)
hourly_ratio = st.sidebar.text_input("24-Hourly Arriving Percentage (Only for ED: %)", value=h)
hourly_ratio = hourly_ratio.split(",")
hourly_distribution = []
for i in hourly_ratio:
    # st.write(type(float(i)))
    hourly_distribution.append(float(i))

p = sir.parameter(current_hospitalized, doubling_time, hospitalized_rate, infectious_days, market_share,
                  n_days, population, recovered, mitigation_date, relative_contact_rate, arriving_rate)
s = sir.Sir(p).get_SIR_model()
sir_data = pd.DataFrame(
    {
        "Susceptible": s[0],
        "Infected": s[1],
        "Recovered": s[2]
    }
)
st.subheader("SIR")
st.line_chart(sir_data)

st.markdown(f"The estimated number of currently infected individuals is {round(s[1][0])}. "
            f"This is based on current inputs for Hospitalizations {current_hospitalized}, "
            f"Hospitalization rate {hospitalized_rate}, Regional population {population}, "
            f"and Hospital market share {market_share}.")
st.markdown(f"An initial doubling time of {doubling_time} days and a recovery time of {infectious_days} days "
            f"imply an $R_0$ of {round(s[2][0])}.")

p = sir.parameter(current_hospitalized, doubling_time, hospitalized_rate, infectious_days, market_share,
                  n_days, population, recovered, mitigation_date, relative_contact_rate, arriving_rate)
r_daily = sir.Sir(p).get_prediction()

p_hourly = sir.parameter(current_hospitalized, doubling_time, hospitalized_rate, infectious_days, market_share,
                         n_days, population, recovered, mitigation_date, relative_contact_rate, arriving_rate,
                         hourly_distribution)
r_hourly = sir.Sir(p_hourly).get_hourly_prediction()

r_daily = list(r_daily)
# st.write(rd)
# st.write(type(rd))
# st.write(r_daily)
# st.write(type(r_daily))
# st.write(r_hourly)
# st.write(type(r_hourly))
# st.write(len(r_daily))

st.sidebar.subheader("ED")
ed_mean = st.sidebar.number_input("Mean ED LOS (Hours)", value=7.5)
ed_std = st.sidebar.number_input("STD. ED LOS (Hours)", value=8.2)
ed_initial = st.sidebar.number_input("Current Census (Patients)", value=8, key="E")
ed_capacity = st.sidebar.number_input("ED Bed Capacity", value=50)

st.sidebar.subheader("Hospital")
h_mean = st.sidebar.number_input("Mean H LOS (Days)", value=8)
h_std = st.sidebar.number_input("STD. H LOS (Days)", value=6)
h_initial = st.sidebar.number_input("Current Census (Patients)", value=15, key="HOS")
p_hos = st.sidebar.number_input("% COVID Patients Hospitalized:", value=30) / 100
valid_input_range(p_hos)
h_capacity = st.sidebar.number_input("Hospital Bed Capacity", value=100)

st.sidebar.subheader("ICU")
icu_mean = st.sidebar.number_input("Mean ICU LOS (Days)", value=13)
icu_std = st.sidebar.number_input("STD. ICU LOS (Days)", value=8)
icu_initial = st.sidebar.number_input("Current Census (Patients)", value=3, key="ICU")
p_icu = st.sidebar.number_input("% COVID Patients Need ICU:", value=6) / 100
valid_input_range(p_icu)
icu_capacity = st.sidebar.number_input("ICU Bed Capacity", value=20)

if st.sidebar.button("Run normal approximation"):
    if ed_mean != 0 and ed_std != 0 and r_hourly is not None and r_daily is not None:
        st.subheader("ED")

        tlist, mt, mt5, mt95, df = another.ed_nor(ed_mean, ed_std, ed_initial, r_daily, r_hourly, ed_capacity)
        # st.write(len(mt))
        # st.write(len(mt5))
        # st.write(len(mt95))

        dfr = pd.DataFrame(list(zip(mt, mt5, mt95)),
                           columns=["Mean", "Lower", "Upper"],
                           index=pd.RangeIndex(len(tlist), name="x"))
        line = alt.Chart(dfr.reset_index()).mark_line(color="#0E6678").encode(
            x="x",
            y="Mean",
        )
        band = line.mark_area(opacity=0.5, color="#9CD3E7").encode(
            x='x',
            y='Lower',
            y2='Upper'
        )
        band.encoding.x.title = "Hours"
        band.encoding.y.title = "Census"
        st.markdown(f"The output is based on the ED staying hours with a mean of {ed_mean}, "
                    f"standard deviation of {ed_std}, current ED patients {ed_initial}, "
                    "and daily and hourly arrival rate according to SIR")

        line + band
        st.write(df)

        if df is not None:
            tmp_download_link = download_link(df, 'ED_data.csv', 'Click here to download the data report')
            st.markdown(tmp_download_link, unsafe_allow_html=True)

    if h_mean != 0 and h_std != 0 and r_daily is not None and p_hos != 0:
        st.subheader("Hospital")
        # st.write(type(r_daily)) list
        tlist, mt, mt5, mt95, df = another.h_nor(h_mean, h_std, h_initial, r_daily, p_hos, h_capacity)

        st.write(len(mt))
        st.write(len(mt5))
        st.write(len(mt95))

        dfr = pd.DataFrame(list(zip(mt, mt5, mt95)),
                           columns=["Mean", "Lower", "Upper"],
                           index=pd.RangeIndex(len(tlist), name="x"))
        line = alt.Chart(dfr.reset_index()).mark_line(color="#0E6678").encode(
            x="x",
            y="Mean",
        )
        band = line.mark_area(opacity=0.5, color="#9CD3E7").encode(
            x='x',
            y='Lower',
            y2='Upper'
        )
        band.encoding.x.title = "Days"
        band.encoding.y.title = "Census"

        st.markdown(f"The output is based on the hospital staying hours with a mean of {h_mean}, "
                    f"standard deviation of {h_std}, current hospital patients {h_initial},"
                    f" percentage of hospitalized patients {p_hos} "
                    "and daily arrival rate according to SIR")

        line + band
        st.write(df)

        if df is not None:
            tmp_download_link = download_link(df, 'hospital_data.csv', 'Click here to download the data report')
            st.markdown(tmp_download_link, unsafe_allow_html=True)

    if icu_mean != 0 and icu_std != 0 and r_daily is not None and p_icu != 0:
        st.subheader("ICU")
        tlist, mt, mt5, mt95, df = another.icu_nor(icu_mean, icu_std, icu_initial, r_daily, p_icu, icu_capacity)

        dfr = pd.DataFrame(list(zip(mt, mt5, mt95)),
                           columns=["Mean", "Lower", "Upper"],
                           index=pd.RangeIndex(len(tlist), name="x"))
        line = alt.Chart(dfr.reset_index()).mark_line(color="#0E6678").encode(
            x="x",
            y="Mean",
        )
        band = line.mark_area(opacity=0.5, color="#9CD3E7").encode(
            x='x',
            y='Lower',
            y2='Upper'
        )
        band.encoding.x.title = "Days"
        band.encoding.y.title = "Census"
        st.markdown(f"The output is based on the hospital staying hours with a mean of {icu_mean}, "
                    f"standard deviation of {icu_std}, current hospital patients {icu_initial}, "
                    f"percentage of patients that needed ICU {p_icu},"
                    "and daily arrival rate according to SIR")

        line + band
        st.write(df)

        if df is not None:
            tmp_download_link = download_link(df, 'hospital_data.csv', 'Click here to download the data report')
            st.markdown(tmp_download_link, unsafe_allow_html=True)

if st.sidebar.button("Run"):
    if ed_mean != 0 and ed_std != 0 and r_hourly is not None and r_daily is not None:
        # with st.spinner("Running .. progress shown here"):
        st.subheader("ED")
        tlist, mt, mt5, mt95, df = another.ed_run(ed_mean, ed_std, ed_initial, r_daily, r_hourly, ed_capacity)
        dfr = pd.DataFrame(list(zip(mt, mt5, mt95)),
                           columns=["Mean", "Lower", "Upper"],
                           index=pd.RangeIndex(len(tlist), name="x"))
        line = alt.Chart(dfr.reset_index()).mark_line(color="#0E6678").encode(
            x="x",
            y="Mean",
        )
        band = line.mark_area(opacity=0.5, color="#9CD3E7").encode(
            x='x',
            y='Lower',
            y2='Upper'
        )
        band.encoding.x.title = "Hours"
        band.encoding.y.title = "Census"
        st.markdown(f"The output is based on the ED staying hours with a mean of {ed_mean}, "
                    f"standard deviation of {ed_std}, current ED patients {ed_initial}, "
                    "and daily and hourly arrival rate according to SIR")

        line + band
        st.write(df)

        if df is not None:
            tmp_download_link = download_link(df, 'ED_data.csv', 'Click here to download the data report')
            st.markdown(tmp_download_link, unsafe_allow_html=True)

    if h_mean != 0 and h_std != 0 and r_daily is not None and p_hos != 0:
        st.subheader("Hospital")
        tlist, mt, mt5, mt95, df = another.hos_run(h_mean, h_std, h_initial, r_daily, p_hos, h_capacity)
        dfr = pd.DataFrame(list(zip(mt, mt5, mt95)),
                           columns=["Mean", "Lower", "Upper"],
                           index=pd.RangeIndex(len(tlist), name="x"))
        line = alt.Chart(dfr.reset_index()).mark_line(color="#0E6678").encode(
            x="x",
            y="Mean",
        )
        band = line.mark_area(opacity=0.5, color="#9CD3E7").encode(
            x='x',
            y='Lower',
            y2='Upper'
        )
        band.encoding.x.title = "Days"
        band.encoding.y.title = "Census"

        st.markdown(f"The output is based on the hospital staying hours with a mean of {h_mean}, "
                    f"standard deviation of {h_std}, current hospital patients {h_initial}, "
                    f"percentage of hospitalized patients {p_hos}"
                    "and daily arrival rate according to SIR")

        line + band
        st.write(df)

        if df is not None:
            tmp_download_link = download_link(df, 'hospital_data.csv', 'Click here to download the data report')
            st.markdown(tmp_download_link, unsafe_allow_html=True)

    if icu_mean != 0 and icu_std != 0 and r_daily is not None and p_icu != 0:
        st.subheader("ICU")
        tlist, mt, mt5, mt95, df = another.icu_run(icu_mean, icu_std, icu_initial, r_daily, p_icu, icu_capacity)

        dfr = pd.DataFrame(list(zip(mt, mt5, mt95)),
                           columns=["Mean", "Lower", "Upper"],
                           index=pd.RangeIndex(len(tlist), name="x"))
        line = alt.Chart(dfr.reset_index()).mark_line(color="#0E6678").encode(
            x="x",
            y="Mean",
        )
        band = line.mark_area(opacity=0.5, color="#9CD3E7").encode(
            x='x',
            y='Lower',
            y2='Upper'
        )
        band.encoding.x.title = "Days"
        band.encoding.y.title = "Census"
        st.markdown(f"The output is based on the hospital staying hours with a mean of {icu_mean}, "
                    f"standard deviation of {icu_std}, current hospital patients {icu_initial}, "
                    f"percentage of patients that needed ICU {p_icu},"
                    "and daily arrival rate according to SIR")

        line + band
        st.write(df)

        if df is not None:
            tmp_download_link = download_link(df, 'hospital_data.csv', 'Click here to download the data report')
            st.markdown(tmp_download_link, unsafe_allow_html=True)
