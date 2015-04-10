
#####------------------- system parameter ------------------------------------------------
#####-------------------------------------------------------------------------------------
INF	=			999999999	#####Infinity number
STA_INTERVAL	=		1		#####statistics interval


#####------------------- random initial seed & stream ------------------------------------
#####-------------------------------------------------------------------------------------
INIT_SEED	=		123
INIT_STREAM	=		0


#####------------------- simulation environment configuration ----------------------------
#####-------------------------------------------------------------------------------------
NUM_JOB	=			1000000		#####number of jobs in one scheduler

MAX_NUM_SCHEDULER	=	32		#####max number of shceduler
NUM_SCHEDULER		=	1		#####number of scheduler

MAX_NUM_SITE		=	64		#####max number of site
NUM_SITE		=	16		#####number of site

MAX_NUM_CPU	=		256		#####max number of cpu in one site
NUM_CPU		=		64		#####number of cpu in one site


#####------------------- system utilization setting --------------------------------------
#####-------------------------------------------------------------------------------------

#####                     ( AVG_JOB_RUNTIME * AVG_JOB_SIZE ) * ( AVG_JOB_ARRRATE * NUM_SCHEDULER )
##### AVG_SYSTEM_LOAD = ---------------------------------------------------------------------------------- <= 1.0
#####                                             ( NUM_SITE * NUM_CPU )

AVG_SYSTEM_LOAD		=	0.5		#####average system utilization


#####------------------- job size setting ------------------------------------------------
#####-------------------------------------------------------------------------------------
JOB_SIZE_TYPE		=	0		#####distribution of job size (num of CPU) for one scheduler
											#####0 - BINOMIAL Distribution

MAX_JOB_SIZE		=	NUM_CPU		#####max num of CPU used by one job
AVG_JOB_SIZE		=	NUM_CPU		#####average num of CPU used by one job
MIN_JOB_SIZE		=	1		#####min num of CPU used by one job


#####------------------- job execution time setting --------------------------------------
#####-------------------------------------------------------------------------------------
JOB_RUNTIME_TYPE	=	0		#####distribution of job runtime
							#####0 - EXPONENTIAL Distribution

AVG_JOB_RUNTIME	=		40.0		#####average job runtime


#####------------------- job arrival setting ---------------------------------------------
#####-------------------------------------------------------------------------------------
JOB_ARRTIME_TYPE	=	0		#####distribution of inter-arrival time of jobs for one scheduler
							#####0 - JOB_ARRTIME_BURST
							#####1 - JOB_ARRTIME_EXPONENTIAL
							#####2 - REAL_TRACE
AVG_JOB_ARRRATE		=	(AVG_SYSTEM_LOAD * NUM_SITE * NUM_CPU) / (AVG_JOB_RUNTIME * AVG_JOB_SIZE * NUM_SCHEDULER)
AVG_JOB_ARRTIME		=	(AVG_JOB_RUNTIME * AVG_JOB_SIZE * NUM_SCHEDULER) / (AVG_SYSTEM_LOAD * NUM_SITE * NUM_CPU)
							#####average inter-arrival time of jobs for one scheduler


#####------------------- site queue setting ----------------------------------------------
#####-------------------------------------------------------------------------------------
SITE_QUEUE_TYPE	=		0		#####local site queueing type
							#####0 - SITE_QUEUE_FIFO
							#####(1) - SITE_QUEUE_BACKFILL

SITE_RANKING_TYPE	=	1		#####local site ranking type
							#####0 - SITE_RANKING_RANDOM
							#####1 - SITE_RANKING_QLEN
							#####2 - SITE_RANKING_ESTIMATE_QTIME
							#####3 - SITE_RANKING_ACTUAL_QTIME
JOB_SUBMISSION_DELAY	 =	1.0		#####remote job submission delay from scheduler to site
RESHUFFLE_CONTROL	=	1		#####reshuffle number control for burst level
							#####0 - offline - static reshuffle number for all burst level
							#####1 - online  - static reshuffle number for different burst level
							#####(2) - online  - dynamic reshuffle number for different burst level (Reinforcement)
#####------------------- for RESHUFFLE_CONTROL = 0 ---------------------
RESHUFFLE		=	16		#####number of top ranked site after being reshuffled
#####------------------- for RESHUFFLE_CONTROL = 1 ---------------------
RESHUFFLE_H	=	14		#####number of top reshuffled for high-burst
RESHUFFLE_L	=		1		#####number of top reshuffled for non-burst

#####------------------- burst detection in trace ----------------------------------------
#####-------------------------------------------------------------------------------------
BURST_DETECT_TYPE=		0		#####burst state detect method
							#####0 - optimum
							#####1 - detection algorithm

JOB_BATCH		=	20		#####min num of job in one batch

BURST_DELAY_SWITCH=	0		#####0 - burst delay off
							#####1 - burst delay on
#####------------------- for BURST_DELAY_SWITCH = 1 --------------------
MIN_BURST_DELAY		=	1		#####min num of delay batch
MIN_BURST_DURATION	=	20		#####min burst duration (sec) to judge narrow burst




