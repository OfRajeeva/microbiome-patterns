#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 17:23:10 2017

@author: robertmarsland
"""
import pandas as pd
import numpy as np
from community_simulator.usertools import MakeConsumerDynamics,MakeResourceDynamics,MakeMatrices,MakeInitialState
from community_simulator import Community
import pickle

#folder = '/project/biophys/microbial_crm/data/'
folder = '../data/'

mp = {'sampling':'Binary', #Sampling method
    'SA': 180, #Number of species in each family
    'MA': 90, #Number of resources of each type
    'Sgen': 0, #Number of generalist species
    'muc': 10, #Mean sum of consumption rates in Gaussian model
    'q': 0, #Preference strength (0 for generalist and 1 for specialist)
    'c0':0, #Background consumption rate in binary model
    'c1':1., #Specific consumption rate in binary model
    'fs':0.45, #Fraction of secretion flux with same resource type
    'fw':0.45, #Fraction of secretion flux to 'waste' resource
    'sparsity':0.05, #Variability in secretion fluxes among resources (must be less than 1)
    'regulation':'independent',
    'supply':'external',
    'response':'type I'
    }
#Construct dynamics
def dNdt(N,R,params):
    return MakeConsumerDynamics(mp)(N,R,params)
def dRdt(N,R,params):
    return MakeResourceDynamics(mp)(N,R,params)
dynamics = [dNdt,dRdt]
#Construct matrices
c,D = MakeMatrices(mp)

## Set up shared parameters
EMP_protocol = {'R0_food':200, #unperturbed fixed point for supplied food
                'n_wells':300, #Number of independent wells
                'S':150, #Number of species per well
                'food':0 #index of food source
                }
EMP_protocol.update(mp)
#Make initial state
N0,R0 = MakeInitialState(EMP_protocol)
Stot = len(N0)
nwells = len(N0.T)
init_state=[N0,R0]
#Make parameter list
m0 = 0.5+0.01*np.random.randn(len(c))
N = {}
metadata = {}

### Crossfeeding, one external resource
exp = 'One resource EMP'
params_EMP=[{'c':c,
            'm':m0+10*np.random.rand(),
            'w':1,
            'D':D,
            'g':1,
            'l':0.8,
            'R0':R0.values[:,k],
            'tau':1
            } for k in range(len(N0.T))]
EMP = Community(init_state,dynamics,params_EMP)
metadata = pd.DataFrame(np.asarray([np.mean(item['m']) for item in params_EMP]),index=N0.T.index,columns=['m'])
EMP.SteadyState()
EMP.N.to_csv(folder+'_'.join(['N']+exp.split(' '))+'.csv')
metadata.to_csv(folder+'_'.join(['m']+exp.split(' '))+'.csv')

### Crossfeeding, all external resources
exp = 'All resources EMP'
params_EMP=[{'c':c,
            'm':m0+10*np.random.rand(),
            'w':1,
            'D':D,
            'g':1,
            'l':0.8,
            'R0':np.ones(len(R0))*EMP_protocol['R0_food']/len(R0),
            'tau':1
            } for k in range(len(N0.T))]
EMP = Community(init_state,dynamics,params_EMP)
metadata = pd.DataFrame(np.asarray([np.mean(item['m']) for item in params_EMP]),index=N0.T.index,columns=['m'])
EMP.SteadyState()
EMP.N.to_csv(folder+'_'.join(['N']+exp.split(' '))+'.csv')
metadata.to_csv(folder+'_'.join(['m']+exp.split(' '))+'.csv')

## Dispersal-Limited
exp = 'Dispersal limited'
N0,R0 = MakeInitialState(EMP_protocol)
select = np.zeros(np.shape(N0))
for k in range(len(N0.T)):
    idx = np.random.choice(range(len(N0)),replace=False,size=np.random.randint(len(N0)))
    select[idx,k] = 1
N0 = N0*select
Stot = len(N0)
nwells = len(N0.T)
init_state=[N0,R0]
params_EMP=[{'c':c,
            'm':m0,
            'w':1,
            'D':D,
            'g':1,
            'l':0.8,
            'R0':R0.values[:,k],
            'tau':1
            } for k in range(len(N0.T))]
EMP = Community(init_state,dynamics,params_EMP)
metadata = pd.DataFrame(np.asarray([np.mean(item['m']) for item in params_EMP]),index=N0.T.index,columns=['m'])
EMP.SteadyState()
EMP.N.to_csv(folder+'_'.join(['N']+exp.split(' '))+'.csv')
metadata.to_csv(folder+'_'.join(['m']+exp.split(' '))+'.csv')
