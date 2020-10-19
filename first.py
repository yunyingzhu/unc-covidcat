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


def valid_input_number(num):
    try:
        float(num)
    except:
        st.sidebar.error("Error! Not a number.")


def valid_input_range(num):
    try:
        float(num)
    except:
        st.sidebar.error("Error! Not a number")
    else:
        if float(num) < 0 or float(num) > 100:
            st.sidebar.error("Error! Please put a number between 0 and 100.")


@st.cache
def open_file(file):
    if file is not None:
        txtstr = ""
        lines = file.readlines()
        Daily_arrival_rate = []
        try:
            for line in lines:
                txtstr = txtstr + line
                line = line.strip('\n')
                Daily_arrival_rate.extend(line.split(' '))
            return Daily_arrival_rate
        except:
            st.warning("Error! Incorrect format.")


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

# st.markdown("Below is a screen-shot of the COVID-CAT output when it is run with hypothetical data and estimates.")

link = '[A complete description of the methodology is provided here]' \
       '(https://covidcat.web.unc.edu/files/2020/06/COVID-CAT.pdf)'

if st.checkbox("Click here to see methodology", key="M"):
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

if st.checkbox("Click here to see sample output"):
    img3 = Image.open(r"Sample.jpeg")
    st.image(img3, width=720)

st.sidebar.subheader("Click for SIR Model or Upload Files")
if st.sidebar.checkbox("Use SIR Model"):
    current_hospitalized = int(st.sidebar.text_input("Current Hospitalized Patients", value=50))
    doubling_time = float(st.sidebar.text_input("Doubling Time", value=8))
    hospitalized_rate = float(st.sidebar.text_input("Hospitalized Rate (%)", value=10))
    infectious_days = int(st.sidebar.text_input("Infectious Days", value=10))
    market_share = float(st.sidebar.text_input("Hospital Market Share (%)", value=30))
    n_days = int(st.sidebar.text_input("n_days", value=20))
    population = float(st.sidebar.text_input("Regional Population", value=100000))
    recovered = int(st.sidebar.text_input("Recovered Patients", value=200))
    mitigation_date = st.sidebar.text_input("Mitigation Date (YYYY-MM-DD)", value=datetime.date(2020, 10, 8))
    relative_contact_rate = float(st.sidebar.text_input("Relative Contact Rate (%)", value=50))
    arriving_rate = float(st.sidebar.text_input("Arriving Rate (%)", value=50))

    hourly_ratio = st.sidebar.text_input("Hourly Ratio (Only for ED: input ratio for 24 hrs)")
    hourly_ratio = hourly_ratio.split(":")
    hourly_distribution = []
    # st.write(type(hourly_ratio[1]))
    # st.write(type(int(hourly_ratio[1])))
    for i in hourly_ratio:
        hourly_distribution.append(int(i))
    # st.write(hourly_distribution)
    # st.write(type(hourly_distribution))
    # a = np.array(hourly_distribution)

    p = sir.parameter(current_hospitalized, doubling_time, hospitalized_rate, infectious_days, market_share,
                      n_days, population, recovered, mitigation_date, relative_contact_rate, arriving_rate)
    r_daily = sir.Sir(p).get_prediction()

    p_hourly = sir.parameter(current_hospitalized, doubling_time, hospitalized_rate, infectious_days, market_share,
                             n_days, population, recovered, mitigation_date, relative_contact_rate, arriving_rate,
                             hourly_distribution)
    r_hourly = sir.Sir(p_hourly).get_hourly_prediction()
    st.write(r_hourly)

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

    # st.markdown("The estimated number of currently infected individuals is $16888. "
    #             "This is based on current inputs for Hospitalizations ($69), Hospitalization rate ($2%), "
    #             "Regional population ($3600000), and Hospital market share ($15%)."
    #             "An initial doubling time of $5.0 days and a recovery time of $10 days imply an $R_0 of $2.49 "
    #             "and daily growth rate of $14.87%.")


if st.sidebar.checkbox("Upload Files"):
    f_daily = st.sidebar.file_uploader("Update Daily Arrival Predictions", key="D", type="txt")
    f_hourly = st.sidebar.file_uploader("Update ED Hourly Arrival Predictions", key="H", type="txt")
    r_daily = open_file(f_daily)
    r_hourly = open_file(f_hourly)

st.sidebar.subheader("ED")
ed_mean = float(st.sidebar.text_input("Mean ED LOS (Hours)", value=7.5))
valid_input_number(ed_mean)
ed_std = float(st.sidebar.text_input("STD. ED LOS (Hours)", value=8.2))
valid_input_number(ed_std)
ed_initial = float(st.sidebar.text_input("Current Census (Patients)", value=8, key="E"))
valid_input_number(ed_initial)

# st.markdown("Mean is `ed_mean`")

if st.sidebar.checkbox("Click here to display results", key="A"):
    if ed_mean != 0 and ed_std != 0:
        with st.spinner("Running .. progress shown here"):

            st.subheader("ED")
            if r_daily is not None and r_hourly is not None:
                tlist, mt, mt5, mt95, df = another.ed_run(ed_mean, ed_std, ed_initial, r_daily, r_hourly)
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
            st.markdown("The ")

            line + band
            st.write(df)

            if df is not None:
                tmp_download_link = download_link(df, 'ED_data.csv', 'Click here to download the data report')
                st.markdown(tmp_download_link, unsafe_allow_html=True)
    else:
        st.warning("invalid parameter for ED")

st.sidebar.subheader("Hospital")
h_mean = float(st.sidebar.text_input("Mean H LOS (Days)", value=8))
valid_input_number(h_mean)
h_std = float(st.sidebar.text_input("STD. H LOS (Days)", value=6))
valid_input_number(h_std)
h_initial = float(st.sidebar.text_input("Current Census (Patients)", value=15, key="HOS"))
valid_input_number(h_initial)
p_hos = float(st.sidebar.text_input("% COVID Patients Hospitalized:", value=30)) / 100
valid_input_range(p_hos)

if st.sidebar.checkbox("Click here to display results", key="B"):
    if h_mean != 0 and h_std != 0:  # and r_daily is not None and p_hos != 0:
        with st.spinner("Running .. progress shown here"):
            st.subheader("Hospital")
            tlist, mt, mt5, mt95, df = another.hos_run(h_mean, h_std, h_initial, r_daily, p_hos)
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
            line + band
            st.write(df)

            if df is not None:
                tmp_download_link = download_link(df, 'hospital_data.csv', 'Click here to download the data report')
                st.markdown(tmp_download_link, unsafe_allow_html=True)

    else:
        st.warning("invalid parameter for Hospital")

st.sidebar.subheader("ICU")
icu_mean = float(st.sidebar.text_input("Mean ICU LOS (Days)", value=13))
valid_input_number(icu_mean)
icu_std = float(st.sidebar.text_input("STD. ICU LOS (Days)", value=8))
valid_input_number(icu_std)
icu_initial = float(st.sidebar.text_input("Current Census (Patients)", value=3, key="ICU"))
valid_input_number(icu_initial)
p_icu = float(st.sidebar.text_input("% COVID Patients Need ICU:", value=6)) / 100
valid_input_range(p_icu)

if st.sidebar.checkbox("Click here to display results", key="C"):
    if icu_mean != 0 and icu_std != 0 and r_daily is not None and p_icu != 0:
        with st.spinner("Running .. progress shown here"):
            st.subheader("ICU")
            tlist, mt, mt5, mt95, df = another.icu_run(icu_mean, icu_std, icu_initial, r_daily, p_icu)

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
            line + band
            st.write(df)

            if df is not None:
                tmp_download_link = download_link(df, 'hospital_data.csv', 'Click here to download the data report')
                st.markdown(tmp_download_link, unsafe_allow_html=True)

    else:
        st.warning("invalid parameter for ICU")
