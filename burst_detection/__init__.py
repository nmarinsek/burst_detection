
#This module creates definitions for implementing Kleinberg's burst detection analysis on batched data.

import pandas as pd
import numpy as np
import sympy.functions.combinatorial.factorials as c


#define the transition cost tau: cost of switching states
#there's a cost to move up states, no cost to move down
#based on definition on pg. 8
#inputs
#   i1: current state
#   i2: next state
#   gam: gamma, penalty for moving up a state
#   n: number of timepoints
def tau(i1,i2,gamma,n):
    if i1>=i2:
        return 0
    else: 
        return (i2-i1) * gamma * np.log(n)
    
#define the fit cost: goodness of fit to the expected outputs of each state
#based on equation on bottom of pg. 14
#    d: number of events in each time period (1xn)
#    r: number of target events in each time period (1xn)
#    p: expected proportions of each state (1xk)
def fit(d,r,p):
    return -np.log(np.float(c.binomial(d,r)) * (p**r) * (1-p)**(d-r))


#define the burst detection function for a two-state automaton
#inputs:
#   r: number of target events in each time period (1xn)
#   d: number of events in each time period (1xn)
#   n: number of timepoints
#   s: multiplicative distance between states
#   gamma: difficulty to move up a state
#   smooth_win: width of smoothing window (use odd numbers)
#output:
#   q: optimal state sequence (1xn)
def burst_detection(r,d,n,s,gamma,smooth_win):
    
    k = 2 #two states
    
    #smooth the data if the smoothing window is greater than 1
    if smooth_win > 1:
        temp_p = r/d #calculate the proportions over time and smooth
        temp_p = temp_p.rolling(window=smooth_win, center=True).mean()
        #update r to reflect the smoothed proportions
        r = temp_p*d
        real_n = sum(~np.isnan(r))  #update the number of timepoints
    else: 
        real_n = n
          
    #calculate the expected proportions for states 0 and 1
    p = {}
    p[0] = np.nansum(r) / float(np.nansum(d))   #overall proportion of events, baseline state
    p[1] = p[0] * s                             #proportion of events during active state
    if p[1] > 1:                                #p1 can't be bigger than 1
        p[1] = 0.99999

    #initialize matrices to hold the costs and optimal state sequence
    cost = np.full([n,k],np.nan)
    q = np.full([n,1],np.nan)

    #use the Viterbi algorithm to find the optimal state sequence
    for t in range(int((smooth_win-1)/2),(int((smooth_win-1)/2))+real_n):

        #calculate the cost to transition to each state
        for j in range(k): 

            #for the first timepoint, calculate the fit cost only
            if t == int((smooth_win-1)/2):
                cost[t,j] = fit(d[t],r[t],p[j])

            #for all other timepoints, calculate the fit and transition cost
            else:
                cost[t,j] = tau(q[t-1],j,gamma,real_n) + fit(d[t],r[t],p[j])

        #add the state with the minimum cost to the optimal state sequence
        q[t] = np.where(cost[t,:] == min(cost[t,:]))

    return q, d, r, p

#define a function to enumerate the bursts
#input: 
#   q: optimal state sequence
#output:
#   bursts: dataframe with beginning and end of each burst
def enumerate_bursts(q, label):
    bursts = pd.DataFrame(columns=['label','begin','end','weight'])
    b = 0
    burst = False
    for t in range(1,len(q)):

        if (burst==False) & (q[t] > q[t-1]):
            bursts.loc[b,'begin'] = t
            burst = True

        if (burst==True) & (q[t] < q[t-1]):
            bursts.loc[b,'end'] = t
            burst = False
            b = b+1

    #if the burst is still going, set end to last timepoint
    if burst == True:
        bursts.loc[b,'end']=t

    bursts.loc[:,'label'] = label
            
    return bursts

#define a function that finds the weights associated with each burst
#find the difference in the cost functions for p0 and p1 in each burst 
#inputs:
#   bursts: dataframe containing the beginning and end of each burst
#   r: number of target events in each time period
#   d: number of events in each time period
#   p: expected proportion for each state
#output:
#   bursts: dataframe containing the weights of each burst, in order
def burst_weights(bursts, r, d, p):
    
    #loop through bursts
    for b in range(len(bursts)):

        cost_diff_sum = 0

        for t in range(bursts.loc[b,'begin'], bursts.loc[b,'end']):

            cost_diff_sum = cost_diff_sum + (fit(d[t],r[t],p[0]) - fit(d[t],r[t],p[1]))

        bursts.loc[b,'weight'] = cost_diff_sum
        
    return bursts.sort_values(by='weight', ascending=False)

