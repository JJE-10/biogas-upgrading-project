import pandas as pd 
import pathlib
import numpy as np
from functools import lru_cache
from scipy import stats

MMBTU_TO_MJ   = 1055.06    # 1 MMBtu = 1,055.06 MJ 
""" Conversion factor for MMBtu to MJ i.e 1 MMBtu = 1,055.06 MJ """

MJ_PER_KG_CH4 = 55.6       # 1 kg CH4 = 55.6 MJ
""" An assumption of 1 kg CH4 = 55.6 MJ, which is obtained from El Abbadi et al., preprint . """

# Loading flow data in m3/d from ad_data.csv 
df = pd.read_csv(r'C:\Users\johns\OneDrive\Documents\JJE\RS\biogas-upgrading-project\clean-data\ad_data.csv')
flow_data = df['flow_m3_per_day'].values
#print(flow_data)

# Calculating biogas generation in kgCH4/hr
""" Calculates the biogas generation in kgCH4/hr based on flow data. 
The flow data is in m3/d. The biogas_gen equation used here is from El Abbadi et al., preprint."""
def cal_biogas_gen(flow_data):
   biogas_gen = flow_data*0.00148
   return biogas_gen

biogas_gen = cal_biogas_gen(flow_data)
#print(biogas_gen)


""" To calculate RNG cost which is cited from Parker et al., 2017, RNG flow needs to be calculated in MMBtu/hr.
With the upgrading technology having an efficiency of 90%, the RNG flow can be calculated 
as rng_flow = 0.9*biogas production.
 """

biogas_prod = biogas_gen * 1/MMBTU_TO_MJ * MJ_PER_KG_CH4 #this biogas_prod is in mmBtu/h which is the same as biogas_gen in kgCH4/h
"""using the biogas generation in kgCH4/hr, the assumption of 1 kg CH4 = 55.6 MJ and the conversion factor of 1 MMBtu = 1,055.06 MJ."""
#print(biogas_prod)

rng_flow = 0.9*biogas_prod #this is the rng flowrate in mmBtu/h after upgrading
#print(rng_flow)

"""Assuming a membrane technology and a downtime of 3%(Patterson et al., 2011), the membrane technology 
operates for  8497.2h per year."""

#Calculating rng_flow1 in mmBtu/yr
rng_flow1 = 8497.2*rng_flow
#print(rng_flow1)

"""Calculating the capital cost for upgrading biogas for pipeline injection alongside it's annual o&m cost
using cost relation from Parker etal.,2017"""

# Capital cost of upgrading biogas for pipeline injection is in $
def biogas_upgrade_pipe(rng_flow):
   biogas_pipe_upgrade = 1370000*rng_flow**0.56
   return biogas_pipe_upgrade
rng_cost = biogas_upgrade_pipe(rng_flow)
print("Capital cost($) = ", rng_cost)

# Annual o&m cost for upgrading biogas for pipeline injection is in $
def annual_o_m_cost(rng_cost):
   o_m_cost = 101625*rng_flow**0.81
   return o_m_cost
o_m_cost = annual_o_m_cost(rng_cost)
print("Annual O&M cost($) = ",o_m_cost)

"""To calculate levelized cost of producing rng in $/mmBtu, an annualized capital and o&m cost in $/mmBtu is required """
"""A Capital Recovery Factor(CRF) is needed in annualizing the capital cost. This equation is given by, """
"""CRF = WACC/1-(1+WACC)^-t (El Abbadi et al.,2022), where: t = Infrastructure Lifetime (years), 
WACC is the Weighted Average Cost of Capital (WACC). A 10% WACC is assumed. 
Assuming membrane technology has a 10year lifetime
A unit capital cost in $/(mmBtu/yr) is also needed to annualize the capital cost """


# Calculting CRF 
def crf_cal(t,wacc):
   crf = wacc/(1-(1+wacc)**-t)
t = 10
wacc = 0.1
crf = wacc/(1-(1+wacc)**-t)
#print("CRF = ",crf)

# Calculating unit capital cost (uncc)
uncc = rng_cost/rng_flow1
print("Unit Capital Cost($/mmBtu/yr) = ",uncc)


