import pandas as pd 
import pathlib
import numpy as np
from functools import lru_cache
from scipy import stats

# Global Variables

MMBTU_TO_MJ = 1055.06 # 1mmBtu = 1055.06MJ
HHV1 = 55.6 # MJ/KgCH4 (El Abbadi, Preprint)
cf = 8497.2 # Capacity Factor(cf). Assuming membrane technology, this is its capacity factor in hours
t = 10 # lifetime of membrane technology in years
wacc = 0.1 # WACC is the Weighted Average Cost of Capital (WACC). A 10% WACC is assumed.
P = 1 # Pressure(P) atm
T = 298 # Temperature(T) K
R = 0.0821 # Ideal gas constant(R) L.atm/mol.K
M = 16 # Molar mass(M) of CH4 g/mol

# Dictionaries
membrane = {
    "cf": 8497.2, # Capacity Factor(cf)
    "t": 10, # lifetime of membrane technology in years
    "energy_consumption": 0.3, # kWh/m3(Makaruk etal., 2010)
    "efficiency": 0.9 
}



# Loading flow data in m3/d from ad_data.csv 
#df = pd.read_csv(r'C:\Users\jjohnson316\OneDrive - University of Iowa\Research\codes\clean-data\ad_data.csv')
df = pd.read_csv(r'C:\Users\johns\OneDrive\Documents\JJE\RS\biogas-upgrading-project\clean-data\ad_data.csv')
# C:\Users\johns\OneDrive\Documents\JJE\RS\biogas-upgrading-project\clean-data
# flow_data = df['flow_m3_per_day'].values
flow_data = df['flow_m3_per_day'].values[0]
#print(flow_data)


def cal_biogas_flow(flow_data): # Calculates biogas flowrate in KgCH4/h
    biogas_flow = flow_data*0.00148
    return biogas_flow

def cal_biogas_flow1(biogas_flow,MMBTU_TO_MJ,HHV1): # Calculates biogas flowrate in mmBtu/h
    biogas_flow1 = biogas_flow * (1/MMBTU_TO_MJ) * HHV1
    return biogas_flow1

def cal_rng_flow(biogas_flow1): # Calculates RNG flowrate in mmBtu/h
    """Calculates RNG flowrate in mmBtu/h"""
    rng_flow = 0.9*biogas_flow1
    return rng_flow

def cal_rng_flow1(cf,rng_flow): # Calculates RNG flowrate in mmBtu/yr
    rng_flow1 = cf * rng_flow
    return rng_flow1

def cal_biogas_upgrade_pipe_cost(rng_flow): # Calculates the capital and O&M cost of upgrading biogas for pipeline injection
    rng_cost = 1370000*rng_flow**0.56
    o_m_cost = 101625*rng_flow**0.81
    return rng_cost, o_m_cost

biogas_flow = cal_biogas_flow(flow_data)
print("Biogas flowrate(KgCH4/h) = ", biogas_flow)

biogas_flow1 = cal_biogas_flow1(biogas_flow,MMBTU_TO_MJ,HHV1)
print("Biogas flowrate(mmBtu/h) = ", biogas_flow1)

rng_flow = cal_rng_flow(biogas_flow1)
print("RNG flowrate(mmBtu/h) = ", rng_flow)

rng_flow1 = cal_rng_flow1(cf,rng_flow)
print("RNG flowrate(mmBtu/yr) = ", rng_flow1)

rng_cost, o_m_cost = cal_biogas_upgrade_pipe_cost(rng_flow)
print("Capex($) = ", rng_cost)
print("Annual O&M Cost($) = ", o_m_cost)

"""To calculate levelized cost of producing rng in $/mmBtu, an annualized capital and o&m cost in $/mmBtu is required
      A Capital Recovery Factor(CRF) is needed in annualizing the capital cost. This equation is given by,
         CRF = WACC/1-(1+WACC)^-t (El Abbadi et al.,2022) 
            A unit capital cost in $/(mmBtu/yr) is also needed to annualize the capital cost """

def cal_crf(t,wacc): # Calculates CRF for membrane technology
    crf = wacc/(1-(1+wacc)**-t)
    return crf

def cal_unit_capex(rng_cost,rng_flow1): # Calculates unit capital cost in $/(mmBtu/yr)
    uncc = rng_cost/rng_flow1
    return uncc

def cal_annualized_capex(crf,uncc): # Calculates annualized capital cost in $/mmBtu
    acc = crf*uncc
    return acc

def cal_annualized_o_m(o_m_cost,rng_flow1): # Calculates annualized O&M cost in $/mmBtu
    aomc = o_m_cost/rng_flow1
    return aomc

crf = cal_crf(t,wacc)
print("CRF for membrane technology = ",crf)

uncc = cal_unit_capex(rng_cost,rng_flow1)
print("Unit Capital Cost for membrane technology($/mmBtu/yr) = ",uncc)

acc = cal_annualized_capex(crf,uncc)
print("Annualized Capital Cost for membrane technology($/mmBtu) = ", acc)

aomc = cal_annualized_o_m(o_m_cost,rng_flow1)
print("Annualized O&M Cost for membrane technology($/mmBtu) = ", aomc)  


"""Energy consumption of technologies"""

def cal_density(P,M,R,T): # Calculates density(p) of methane at 298K and 1 atm
    p = (P*M)/(R*T)
    return p

def cal_HHV(HHV1,p): # Calculates HHV of methane in MJ/m3
    HHV2 = HHV1*p
    return HHV2

def cal_biogas_flow2(HHV2,HHV1,biogas_flow): # Calculates biogas flow in m3/h
    biogas_flow2 = (1/HHV2)*HHV1*biogas_flow
    return biogas_flow2


p = cal_density(P,M,R,T)
print("Density of CH4(kg/m3) = ",p)