Experiment 1: Determine initial scalability profile.
Of an application A deployed on a machine M, with N cores. 
Input from user:
Initial configurations of various resources and other parameters of the application
Session file,  Maximum number of cores (N)  till which multi-core scalability is desired, step size s of increasing # of cores. 
Scalability Tolerance factor ɑ:  0 < ɑ < 1 


Output from the experiment:
MaxTput (n)  for each n = 1, s, 2s, … N

//Lot more measurements should have been collected
MaxCPU(n) for each n = 1, s, 2s, … N



Interpretation Output:
n_s = Min {n | MaxTput(n)/MaxTput(1) < ɑ n }
// must have checks to conform that scalability is reduced forall n >= n_s
Output n_s as the max core till which ‘scalability’ is seen. 

Experiment 2: Run scalability bottleneck identification and diagnostics

Check CPU util ⍴_CPU (n) at n >= n_s. If all consistently < β   (β ~ 0.9 or so), CPU is not the bottleneck.  Follow process of identifying non-CPU bottleneck

Non-CPU Bottleneck Identification Process 
At ‘-n_S’ cores
For some software resource ‘r’ in R, hypothesis that the baseline setting of ‘r’ is the bottleneck
Carry out a series of load tests where the other baseline settings are the same, but quantity of R is increased (double)

If the maximum throughput increased compared to the baseline, we confirm ‘r’ is the bottleneck, else repeat the step 6 for next software resource in ‘R’

CPU Bottleneck Identification Process 
Do series of load tests and profiling from ‘S’ cores to ‘X’ cores 
Capture the profiling data by using perf tool (context switches, LLC-cache misses, LLC load misses, ….) 

Observe which data point has a high varying threshold and may be that is the cause of the bottleneck.
