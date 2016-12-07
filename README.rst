===========
BURST DETECTION
===========

This package implements Kleinberg’s burst detection algorithm for batched data, as described in the paper “Bursty and Hierarchical Structure in Streams” (2002). 

Burst detection identifies time periods in which a target event is uncharacteristically frequent, or "bursty."  You can use burst detection to detect bursts in a continuous stream of events (such as receiving emails) or in discrete batches of events (such as poster titles submissions to an annual conference). This package identifies bursts in discrete batched data. Scripts have already been written to identify bursts in continuous data (see: "pybursts" in Python or "bursts" in R).  


INSTALLATION
=========

Download and install the package with pip::

   pip install burst_detection


USAGE
=========

You’ll want to read Kleinberg’s paper, “Bursty and Hierarchical Structure in Streams,” to gain solid understandings of the theory behind burst detection and how to use the following functions appropriately. 

burst_detection:
~~~~~~~~~~~~~~~~
This function returns the optimal state sequence, q, of a two-state automaton for a sequence of observed target probabilities. The optimal state sequence q consists of an array of 0s and 1s (with length n), where 0 signifies that the system is in a baseline state and 1 signifies that the system is in a bursty state at time t. Burst detection is sensitive to noise, so you have the option of smoothing the time course of the target probabilities to reduce the effects of noise.

INPUTS:
   - r: number of target events in each time period (nx1)
   - d: number of events in each time period (nx1)
   - n: number of timepoints
   - s: multiplicative distance between states
   - gamma: difficulty associated with moving up a state
   - smooth_win: width of smoothing window to temporally smooth target probabilities (use odd numbers; set smooth_win=1 to skip smoothing)

OUTPUTS:
   - q: optimal state sequence (nx1)
   - d: number of events in each time period (nx1)
   - r: number of target events in each time period (nx1)
   - p: probabilities associated with each state (kx1)

USAGE:
::
   q, d, r, p = burst_detection(r, d, n, s=2, gamma=1, smooth_win=3)

enumerate_bursts:
~~~~~~~~~~~~~~~~~
This function creates a list of all the bursts in an optimal state sequence q. 

INPUT: 
   - q: optimal state sequence (nx1)

OUTPUT:
   - bursts: a pandas dataframe containing the time points that each burst began and ended

USAGE:
::
   bursts = enumerate_bursts(q)

burst_weights:
~~~~~~~~~~~~~~
This function computes the weight associated with each burst. 

INPUTS:
   - bursts: a pandas dataframe containing the time points that each burst began and ended
   - r: number of target events in each time period (nx1)
   - d: number of events in each time period (nx1)
   - p: expected proportion for each state (kx1)

OUTPUT:
   - bursts: a pandas dataframe containing the weights of each burst, in order

USAGE:
::
   weighted_bursts = burst_weights(bursts, r, d, p)


EXAMPLE
=========
::

   import burst_detection as bd
   import numpy as np

   #number of target events at each time point
   r = np.array([0, 2, 1, 6, 7, 2, 8, 7, 2, 1], dtype=float)
   #total number of events at each time point
   d = np.array([9, 11, 12, 10, 10, 8, 12, 10, 13, 11], dtype=float)
   #number of time points
   n = len(r)

   #find the optimal state sequence (q)
   q, d, r, p = bd.burst_detection(r,d,n,s=2,gamma=1,smooth_win=1)

   #enumerate bursts based on the optimal state sequence
   bursts = bd.enumerate_bursts(q, 'burstLabel')

   #find weight of bursts
   weighted_bursts = bd.burst_weights(bursts,r,d,p)

   print 'observed probabilities: '
   print str(r/d)

   print 'optimal state sequence: '
   print str(q.T)

   print 'baseline probability: ' + str(p[0])

   print 'bursty probability: ' + str(p[1])

   print 'weighted bursts:'
   print weighted_bursts

OUTPUT:
::
   observed probabilities: 
   [ 0.00  0.18  0.08  0.60  0.70  0.25 0.67  0.70  0.15  0.09]

   optimal state sequence: 
   [[ 0.  0.  0.  0.  1.  0.  1.  1.  0.  0.]]

   baseline probability: 0.339

   bursty probability: 0.679
   
   weighted bursts:
   +---+------------+-------+------+----------+
   |   | label      | begin | end  | weight   |
   +---+------------+-------+------+----------+
   | 1 | burstLabel | 6     | 8    | 5.34226  |
   +---+------------+-------+------+----------+
   | 0 | burstLabel | 4     | 5    | 2.68563  |
   +---+------------+-------+------+----------+

