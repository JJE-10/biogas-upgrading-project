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
df = pd.read_csv(r'C:\Users\jjohnson316\OneDrive - University of Iowa\Research\codes\clean-data\ad_data.csv')
flow_data = df['flow_m3_per_day'].values
#print(flow_data)

# Calculating biogas generation in kgCH4/hr
""" Calculates the biogas generation in kgCH4/hr based on flow data. 
The flow data is in m3/d. The biogas_gen equation used here is from El Abbadi et al., preprint."""
def cal_biogas_gen(flow_data):
   biogas_gen = flow_data*0.00148
   return biogas_gen

biogas_gen = cal_biogas_gen(flow_data)
print(biogas_gen)


""" To calculate RNG cost which is cited from Parker et al., 2017, RNG flow needs to be calculated in MMBtu/hr.
With the upgrading technology having an efficiency of 90%, the RNG flow can be calculated 
as rng-flow = 0.9*biogas production.
 using the biogas generation in kgCH4/hr, the assumption of 1 kg CH4 = 55.6 MJ and the conversion factor of 1 MMBtu = 1,055.06 MJ."""

biogas_prod = biogas_gen * 1/MMBTU_TO_MJ * MJ_PER_KG_CH4
print(rng_flow)

def biogas_upgrade_pipe(rng_flow):
   biogas_pipe_upgrade = 1370000*rng_flow**0.56
   return biogas_pipe_upgrade
rng_cost = biogas_upgrade_pipe(rng_flow)
print(rng_cost)

def annual_o_m_cost(rng_cost):
   o_m_cost = 101625*rng_flow**0.81
   return o_m_cost
o_m_cost = annual_o_m_cost(rng_cost)
print(o_m_cost)