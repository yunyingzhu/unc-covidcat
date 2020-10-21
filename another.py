import pandas as pd
from numpy import log, square, sqrt, random, mean, inf, loadtxt, array
from numba import jit
from math import ceil, erf, floor
from prettytable import PrettyTable
from scipy.integrate import quad
from scipy.stats import norm, binom, poisson, lognorm
import matplotlib.pyplot as plt
from datetime import datetime
import streamlit
# import first

global lognorm


@jit
def lognorm(x, mu, sigma):
    a = (log(x) - mu) / sqrt(2 * sigma ** 2)
    p = 0.5 + 0.5 * erf(a)
    return p


global lognormc


@jit
def lognormc(x, mu, sigma):
    return 1 - lognorm(x, mu, sigma)


global f


@jit
def f(s, t, mu, stddev, Arrival_rate):
    hourofday = floor((t - s) % 24)
    p = flambda(t - s, Arrival_rate) * (1 - lognorm(s, mu, stddev))
    return p


global flambda


@jit
def flambda(x, Arrival_rate):
    p = floor(x)
    return Arrival_rate[p]


global rs


def rs(x, mu, stddev, length_of_stay_mean):
    temp_int, temp_err = quad(lognormc, 0, x, args=(mu, stddev), limit=500)
    return temp_int / length_of_stay_mean


@jit
def maxc(datalist):
    temp = max(datalist)
    if temp <= 0:
        return round(0, 2)
    else:
        return round(temp, 2)


@streamlit.cache(suppress_st_warning=True)
def hos_run(Hospital_length_of_stay_mean, Hospital_length_of_stay_std, Hospital_initial_condition, rate,
            Percentage_hospitalized):
    mu = log(square(Hospital_length_of_stay_mean) / sqrt(
        square(Hospital_length_of_stay_mean) + square(Hospital_length_of_stay_mean)))
    stddev = sqrt(log(1 + square(Hospital_length_of_stay_mean) / square(Hospital_length_of_stay_mean)))
    ArrivalRate = array(rate, dtype=float)
    ArrivalRate = ArrivalRate * Percentage_hospitalized
    TotalTimeLength = ArrivalRate.size
    initial_condition = Hospital_initial_condition

    t = 1
    tlist = []
    tlist = range(1, TotalTimeLength + 1)
    mt = []
    mt5 = []
    mt95 = []
    pt25 = []
    pt50 = []
    pt75 = []
    pt100 = []
    pt125 = []
    pt150 = []
    pt175 = []
    error = []
    st = []
    stl = []

    while t <= TotalTimeLength:
        print(t)
        ans, err = quad(f, 0, t, args=(t, mu, stddev, ArrivalRate))
        total_probability = 0
        probability_still_in_system = 1 - rs(t, mu, stddev, Hospital_length_of_stay_mean)
        # Calculate the mean
        mt_temp = initial_condition * probability_still_in_system + ans
        mt.append(mt_temp)

        temptotal = 0
        flag = [False, False]
        tempcdf = 0

        while tempcdf <= 0.99:
            i = 0
            if t <= 20:
                while i <= temptotal and i <= initial_condition:
                    if i <= initial_condition:
                        tempcdf = tempcdf + binom.pmf(i, initial_condition, probability_still_in_system) \
                                  * poisson.pmf((temptotal - i), ans)
                    i = i + 1
            else:
                tempcdf = poisson.cdf(temptotal, ans)

            if tempcdf >= 0.05 and flag[0] == False:
                if temptotal - 1 > 0:
                    tempq = temptotal - 1
                else:
                    tempq = 0
                mt5.append(tempq)
                flag[0] = True
            if tempcdf >= 0.95 and flag[1] == False:
                mt95.append(temptotal)
                flag[1] = True
            if temptotal == 25:
                pt25.append(1 - tempcdf)
            if temptotal == 50:
                pt50.append(1 - tempcdf)
            if temptotal == 75:
                pt75.append(1 - tempcdf)
            if temptotal == 100:
                pt100.append(1 - tempcdf)
            if temptotal == 125:
                pt125.append(1 - tempcdf)
            if temptotal == 150:
                pt150.append(1 - tempcdf)
            if temptotal == 175:
                pt175.append(1 - tempcdf)
            temptotal = temptotal + 1
        temptotal = temptotal - 1
        if temptotal < 25:
            pt25.append(float(0))
        if temptotal < 50:
            pt50.append(float(0))
        if temptotal < 75:
            pt75.append(float(0))
        if temptotal < 100:
            pt100.append(float(0))
        if temptotal < 125:
            pt125.append(float(0))
        if temptotal < 150:
            pt150.append(float(0))
        if temptotal < 175:
            pt175.append(float(0))
        t = t + 1

    data = {
        "# Patients": ["25pts", "50pts", "75pts", "100pts", "125pts", "150pts", "175pts"],
        "10 Days": [maxc(pt25[0:10]), maxc(pt50[0:10]), maxc(pt75[0:10]), maxc(pt100[0:10]), maxc(pt125[0:10]),
                    maxc(pt150[0:10]), maxc(pt175[0:10])],
        "20 Days": [maxc(pt25[0:20]), maxc(pt50[0:20]), maxc(pt75[0:20]), maxc(pt100[0:20]), maxc(pt125[0:20]),
                    maxc(pt150[0:20]), maxc(pt175[0:20])],
        "30 Days": [maxc(pt25[0:30]), maxc(pt50[0:30]), maxc(pt75[0:30]), maxc(pt100[0:30]), maxc(pt125[0:30]),
                    maxc(pt150[0:30]), maxc(pt175[0:30])],
        "40 Days": [maxc(pt25[0:40]), maxc(pt50[0:40]), maxc(pt75[0:40]), maxc(pt100[0:40]), maxc(pt125[0:40]),
                    maxc(pt150[0:40]), maxc(pt175[0:40])],
        "50 Days": [maxc(pt25[0:50]), maxc(pt50[0:50]), maxc(pt75[0:50]), maxc(pt100[0:50]), maxc(pt125[0:50]),
                    maxc(pt150[0:50]), maxc(pt175[0:50])],
        "60 Days": [maxc(pt25[0:60]), maxc(pt50[0:60]), maxc(pt75[0:60]), maxc(pt100[0:60]), maxc(pt125[0:60]),
                    maxc(pt150[0:60]), maxc(pt175[0:60])],
        "70 Days": [maxc(pt25[0:70]), maxc(pt50[0:70]), maxc(pt75[0:70]), maxc(pt100[0:70]), maxc(pt125[0:70]),
                    maxc(pt150[0:70]), maxc(pt175[0:70])],
        "80 Days": [maxc(pt25[0:80]), maxc(pt50[0:80]), maxc(pt75[0:80]), maxc(pt100[0:80]), maxc(pt125[0:80]),
                    maxc(pt150[0:80]), maxc(pt175[0:80])],
        "90 Days": [maxc(pt25[0:90]), maxc(pt50[0:90]), maxc(pt75[0:90]), maxc(pt100[0:90]), maxc(pt125[0:90]),
                    maxc(pt150[0:90]), maxc(pt175[0:90])]
    }

    df = pd.DataFrame(data)
    return tlist, mt, mt5, mt95, df


@streamlit.cache(suppress_st_warning=True)
def icu_run(ICU_length_of_stay_mean, ICU_length_of_stay_std, ICU_initial_condition, rate, Percentage_icu):
    mu = log(square(ICU_length_of_stay_mean) / sqrt(
        square(ICU_length_of_stay_mean) + square(ICU_length_of_stay_mean)))
    stddev = sqrt(
        log(1 + square(ICU_length_of_stay_mean) / square(ICU_length_of_stay_mean)))
    ArrivalRate = array(rate, dtype=float)
    ArrivalRate = ArrivalRate * Percentage_icu
    TotalTimeLength = ArrivalRate.size
    initial_condition = ICU_initial_condition

    step = 1
    t = 1
    tlist = []
    tlist = range(1, TotalTimeLength + 1)
    zeros = [0 for i in tlist]
    mt = []
    mt5 = []
    mt95 = []
    pt15 = []
    pt20 = []
    pt25 = []
    pt30 = []
    pt35 = []
    pt40 = []
    pt45 = []
    error = []
    st = []
    stl = []

    # my_bar = streamlit.progress(0)
    while t <= TotalTimeLength:
        percent_complete = t / TotalTimeLength
        # my_bar.progress(percent_complete)

        ans, err = quad(f, 0, t, args=(t, mu, stddev, ArrivalRate), limit=500)
        total_probability = 0
        probability_still_in_system = 1 - rs(t, mu, stddev, ICU_length_of_stay_mean)
        mttemp = initial_condition * probability_still_in_system + ans
        mt.append(mttemp)
        temptotal = 0
        flag = [False, False]
        tempcdf = 0
        while tempcdf <= 0.99:
            i = 0
            if t <= 40:
                while i <= temptotal and i <= initial_condition:
                    if i <= initial_condition:
                        tempcdf = tempcdf + binom.pmf(i, initial_condition,
                                                      probability_still_in_system) * poisson.pmf(
                            (temptotal - i), ans)
                    i = i + 1
            else:
                tempcdf = poisson.cdf(temptotal, ans)
            if tempcdf >= 0.05 and flag[0] == False:
                if temptotal - 1 > 0:
                    tempq = temptotal - 1
                else:
                    tempq = 0
                mt5.append(tempq)
                flag[0] = True
            if tempcdf >= 0.95 and flag[1] == False:
                mt95.append(temptotal)
                flag[1] = True
            if temptotal == 15:
                pt15.append(1 - tempcdf)
            if temptotal == 20:
                pt20.append(1 - tempcdf)
            if temptotal == 25:
                pt25.append(1 - tempcdf)
            if temptotal == 30:
                pt30.append(1 - tempcdf)
            if temptotal == 35:
                pt35.append(1 - tempcdf)
            if temptotal == 40:
                pt40.append(1 - tempcdf)
            if temptotal == 45:
                pt45.append(1 - tempcdf)
            temptotal = temptotal + 1
        temptotal = temptotal - 1
        if temptotal < 15:
            pt15.append(float(0))
        if temptotal < 20:
            pt20.append(float(0))
        if temptotal < 25:
            pt25.append(float(0))
        if temptotal < 30:
            pt30.append(float(0))
        if temptotal < 35:
            pt35.append(float(0))
        if temptotal < 40:
            pt40.append(float(0))
        if temptotal < 45:
            pt45.append(float(0))
        t = t + step

    data = {
        "# Patients": ["15pts", "20pts", "25pts", "30pts", "35pts", "40pts", "45pts"],
        "10 Days": [maxc(pt15[0:10]), maxc(pt20[0:10]), maxc(pt25[0:10]), maxc(pt30[0:10]), maxc(pt35[0:10]),
                    maxc(pt40[0:10]), maxc(pt45[0:10])],
        "20 Days": [maxc(pt15[0:20]), maxc(pt20[0:20]), maxc(pt25[0:20]), maxc(pt30[0:20]), maxc(pt35[0:20]),
                    maxc(pt40[0:20]), maxc(pt45[0:20])],
        "30 Days": [maxc(pt15[0:30]), maxc(pt20[0:30]), maxc(pt25[0:30]), maxc(pt30[0:30]), maxc(pt35[0:30]),
                    maxc(pt40[0:30]), maxc(pt45[0:30])],
        "40 Days": [maxc(pt15[0:40]), maxc(pt20[0:40]), maxc(pt25[0:40]), maxc(pt30[0:40]), maxc(pt35[0:40]),
                    maxc(pt40[0:40]), maxc(pt45[0:40])],
        "50 Days": [maxc(pt15[0:50]), maxc(pt20[0:50]), maxc(pt25[0:50]), maxc(pt30[0:50]), maxc(pt35[0:50]),
                    maxc(pt40[0:50]), maxc(pt45[0:50])],
        "60 Days": [maxc(pt15[0:60]), maxc(pt20[0:60]), maxc(pt25[0:60]), maxc(pt30[0:60]), maxc(pt35[0:60]),
                    maxc(pt40[0:60]), maxc(pt45[0:60])],
        "70 Days": [maxc(pt15[0:70]), maxc(pt20[0:70]), maxc(pt25[0:70]), maxc(pt30[0:70]), maxc(pt35[0:70]),
                    maxc(pt40[0:70]), maxc(pt45[0:70])],
        "80 Days": [maxc(pt15[0:80]), maxc(pt20[0:80]), maxc(pt25[0:80]), maxc(pt30[0:80]), maxc(pt35[0:80]),
                    maxc(pt40[0:80]), maxc(pt45[0:80])],
        "90 Days": [maxc(pt15[0:90]), maxc(pt20[0:90]), maxc(pt25[0:90]), maxc(pt30[0:90]), maxc(pt35[0:90]),
                    maxc(pt40[0:90]), maxc(pt45[0:90])]
    }

    df = pd.DataFrame(data)
    return tlist, mt, mt5, mt95, df


@streamlit.cache(suppress_st_warning=True)
def ed_run(ED_length_of_stay_mean, ED_length_of_stay_std, ED_initial_condition, Daily_arrival_rate, Hourly_pattern):
    mu = log(square(ED_length_of_stay_mean) / sqrt(
        square(ED_length_of_stay_mean) + square(ED_length_of_stay_mean)))
    stddev = sqrt(
        log(1 + square(ED_length_of_stay_mean) / square(ED_length_of_stay_mean)))

    ArrivalRate = []
    for j in range(len(Daily_arrival_rate)):
        for k in range(24):
            ArrivalRate.append(float(Daily_arrival_rate[j]) * float(Hourly_pattern[k]))
    ArrivalRate = array(ArrivalRate, dtype=float)
    TotalTimeLength = ArrivalRate.size
    initial_condition = ED_initial_condition

    step = 1
    t = 1
    tlist = []
    tlist = range(1, TotalTimeLength + 1)
    mt = []
    mt5 = []
    mt95 = []
    pt10 = []
    pt15 = []
    pt20 = []
    pt25 = []
    pt30 = []
    pt35 = []
    pt40 = []
    error = []
    st = []
    stl = []

    # my_bar = streamlit.progress(0)

    while t <= TotalTimeLength:
        print(t)
        percent_complete = t / TotalTimeLength
        # my_bar.progress(percent_complete)
        ans, err = quad(f, 0, t, args=(t, mu, stddev, ArrivalRate), limit=500)
        total_probability = 0
        probability_still_in_system = 1 - rs(t, mu, stddev, ED_length_of_stay_mean)
        # Calculate the mean
        mttemp = initial_condition * probability_still_in_system + ans
        mt.append(mttemp)
        # Calculate the numerical distribution:
        temptotal = 0
        flag = [False, False]
        tempcdf = 0
        while tempcdf <= 0.99:
            i = 0
            if t <= 48:
                while i <= temptotal and i <= initial_condition:
                    if i <= initial_condition:
                        tempcdf = tempcdf + binom.pmf(i, initial_condition,
                                                      probability_still_in_system) * poisson.pmf(
                            (temptotal - i), ans)
                    i = i + 1
            else:
                tempcdf = poisson.cdf(temptotal, ans)
            if tempcdf >= 0.05 and flag[0] == False:
                if temptotal - 1 > 0:
                    tempq = temptotal - 1
                else:
                    tempq = 0
                mt5.append(tempq)
                flag[0] = True
            if tempcdf >= 0.95 and flag[1] == False:
                mt95.append(temptotal)
                flag[1] = True
            if temptotal == 10:
                pt10.append(1 - tempcdf)
            if temptotal == 15:
                pt15.append(1 - tempcdf)
            if temptotal == 20:
                pt20.append(1 - tempcdf)
            if temptotal == 25:
                pt25.append(1 - tempcdf)
            if temptotal == 30:
                pt30.append(1 - tempcdf)
            if temptotal == 35:
                pt35.append(1 - tempcdf)
            if temptotal == 40:
                pt40.append(1 - tempcdf)
            temptotal = temptotal + 1
        temptotal = temptotal - 1
        if temptotal < 10:
            pt10.append(float(0))
        if temptotal < 15:
            pt15.append(float(0))
        if temptotal < 20:
            pt20.append(float(0))
        if temptotal < 25:
            pt25.append(float(0))
        if temptotal < 30:
            pt30.append(float(0))
        if temptotal < 35:
            pt35.append(float(0))
        if temptotal < 40:
            pt40.append(float(0))
        t = t + step

    data = {
        "# Patients": ["10pts", "15pts", "20pts", "25pts", "30pts", "35pts", "40pts"],
        "10 Days": [maxc(pt10[0:240]), maxc(pt15[0:240]), maxc(pt20[0:240]), maxc(pt25[0:240]), maxc(pt30[0:240]),
                    maxc(pt35[0:240]), maxc(pt40[0:240])],
        "20 Days": [maxc(pt10[0:480]), maxc(pt15[0:480]), maxc(pt20[0:480]), maxc(pt25[0:480]), maxc(pt30[0:480]),
                    maxc(pt35[0:480]), maxc(pt40[0:480])],
        "30 Days": [maxc(pt10[0:720]), maxc(pt15[0:720]), maxc(pt20[0:720]), maxc(pt25[0:720]), maxc(pt30[0:720]),
                    maxc(pt35[0:720]), maxc(pt40[0:720])],
        "40 Days": [maxc(pt10[0:960]), maxc(pt15[0:960]), maxc(pt20[0:960]), maxc(pt25[0:960]), maxc(pt30[0:960]),
                    maxc(pt35[0:960]), maxc(pt40[0:960])],
        "50 Days": [maxc(pt10[0:1200]), maxc(pt15[0:1200]), maxc(pt20[0:1200]), maxc(pt25[0:1200]), maxc(pt30[0:1200]),
                    maxc(pt35[0:1200]), maxc(pt40[0:1200])],
        "60 Days": [maxc(pt10[0:1440]), maxc(pt15[0:1440]), maxc(pt20[0:1440]), maxc(pt25[0:1440]), maxc(pt30[0:1440]),
                    maxc(pt35[0:1440]), maxc(pt40[0:1440])],
        "70 Days": [maxc(pt10[0:1680]), maxc(pt15[0:1680]), maxc(pt20[0:1680]), maxc(pt25[0:1680]), maxc(pt30[0:1680]),
                    maxc(pt35[0:1680]), maxc(pt40[0:1680])],
        "80 Days": [maxc(pt10[0:1920]), maxc(pt15[0:1920]), maxc(pt20[0:1920]), maxc(pt25[0:1920]), maxc(pt30[0:1920]),
                    maxc(pt35[0:1920]), maxc(pt40[0:1920])],
        "90 Days": [maxc(pt10[0:2160]), maxc(pt15[0:2160]), maxc(pt20[0:2160]), maxc(pt25[0:2160]), maxc(pt30[0:2160]),
                    maxc(pt35[0:2160]), maxc(pt40[0:2160])]
    }

    df = pd.DataFrame(data)
    return tlist, mt, mt5, mt95, df


