import numpy as np
import datetime
import pandas as pd

class parameter:
    def __init__(self,current_hospitalized,doubling_time,hospitalized_rate,
                 infectious_days,market_share,n_days,population,recovered,
                 mitigation_date,relative_contact_rate,arriving_rate,hourly_distribution = None):
        # the properties not provided by parameters haven't been used for now
        self.current_date = datetime.date.today()
        self.current_hospitalized = current_hospitalized
        self.date_first_hospitalized = None
        self.doubling_time = doubling_time
        self.hospitalized_rate = hospitalized_rate * 1.0 / 100.0
        self.icu = None
        self.infectious_days = infectious_days
        self.market_share = market_share * 1.0 /100.0
        self.max_y_axis = None
        self.mitigation_date = mitigation_date
        self.n_days = n_days
        self.population = population
        self.region = None
        self.relative_contact_rate = relative_contact_rate * 1.0 / 100.0
        self.recovered = recovered
        self.ventilated = None
        self.use_log_scale = False
        self.arriving_rate = arriving_rate * 1.0 / 100.0
        #self.ifED = ifED
        self.hourly_distribution = hourly_distribution # in percentage


class Sir:
    def __init__(self, p):
        self.rp = p.population;
        self.ms = p.market_share;
        self.ph = p.hospitalized_rate; #pencentage hospitalized
        self.ch = p.current_hospitalized;
        self.dt = p.doubling_time;
        self.sd = p.relative_contact_rate; #social distancing
        self.dp = p.n_days; #days projected
        self.id = p.infectious_days;
        self.recovered = p.recovered;
        self.mitigation_date = p.mitigation_date;
        self.current_date = p.current_date;
        self.relative_contact_rate = p.relative_contact_rate;
        self.arriving_rate = p.arriving_rate;
        #self.ifED = p.ifED
        self.hourly_distribution = p.hourly_distribution

        # get the initial infeceted number from ch,ms,and ph
        self.init_infected = self.ch / self.ms /self.ph;
        # get init_ susceptible and recovered then
        self.init_recovered = self.recovered;  # recovered seems that has to be entered in parameter
        self.init_susceptible = self.rp - self.init_infected - self.recovered;


        # define beta,sigma and gamma
        self.gamma = 1.0 / self.id;
        intrinsic_growth_rate = self.get_growth_rate(self.dt)
        self.beta = self.get_beta(intrinsic_growth_rate, self.gamma, self.init_susceptible, 0.0)
        self.beta_mitigated = self.get_beta(intrinsic_growth_rate, self.gamma, self.init_susceptible, self.relative_contact_rate)
        #ignore policy for now
        raw = []
        raw = self.get_SIR_arrays(self.init_susceptible,self.init_infected,self.init_recovered,self.dp,self.mitigation_date)
        self.sir = raw
        I_difference = np.diff(raw[1])
        self.disposition = I_difference * self.ms * self.arriving_rate

    def get_prediction(self):
        #if (self.ifED == True): return self.get_hourly_prediction()
        return self.disposition

    def get_hourly_prediction(self):
        hourly = []
        for i in self.disposition:
            one_day = i.astype(int) * np.array(self.hourly_distribution)/100.0
            for j in one_day:
                hourly.append(j)
        return hourly


    def get_SIR_model(self):
        return self.sir

    def get_beta(self,
            intrinsic_growth_rate: float,
            gamma: float,
            susceptible: float,
            relative_contact_rate: float
    ) -> float:
        return (
                (intrinsic_growth_rate + gamma)
                / susceptible
                * (1.0 - relative_contact_rate)
        )

    def get_growth_rate(self,doubling_time):
        """Calculates average daily growth rate from doubling time."""
        if doubling_time is None or doubling_time == 0.0:
            return 0.0
        return (2.0 ** (1.0 / doubling_time) - 1.0)

    def get_SIR_arrays(self,init_S,init_I,init_R,days,mitigation_date):
        current_date = self.current_date;

        raw = [] # the array to be returned with arrays of S,I,R in it
        array_S = np.empty(days+1)
        array_I = np.empty(days+1)
        array_R = np.empty(days+1)

        raw.append(array_S)
        raw.append(array_I)
        raw.append(array_R)

        array_S[0] = init_S
        array_I[0] = init_I
        array_R[0] = init_R

        # the init_day has index 0, and first day after it has 1, then 2...
        for i in range(1,days+1):
            # if the date is moved to mitigation policy, then change beta
            if current_date == mitigation_date:
                self.beta = self.beta_mitigated;
            array_S[i] = array_S[i-1] - self.beta * array_S[i-1] * array_I[i-1] * 1.0
            array_I[i] = array_I[i-1] + self.beta * array_S[i-1] * array_I[i-1] * 1.0  - self.gamma * array_I[i-1]
            array_R[i] = array_R[i-1] + self.gamma * array_I[i-1]
            current_date = current_date + datetime.timedelta(days = 1)
        return raw

if __name__ == '__main__':
    # p = parameter(current_hospitalized=50, doubling_time=5, hospitalized_rate=10,
    #               infectious_days=10, market_share=30, n_days=20, population=100000, recovered=200,
    #               mitigation_date=datetime.date(2020, 10, 8), relative_contact_rate=20, arriving_rate=60)
    #
    # my_sir = Sir(p);
    # result = my_sir.get_prediction()
    # print(result)

    p = parameter(current_hospitalized=50, doubling_time=5, hospitalized_rate=10,
                  infectious_days=10, market_share=30, n_days=20, population=100000, recovered=200,
                  mitigation_date=datetime.date(2020, 10, 8), relative_contact_rate=20, arriving_rate=60,
                  hourly_distribution = [10,20,30,40])

    my_sir = Sir(p);
    result = my_sir.get_hourly_prediction()
    print(result)

