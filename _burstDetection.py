#! /usr/bin/python
from _init import *
from _rngs import *



class burstDetection:
   def __init__(self):
      self.tmp_num_job = 0
      self.job_batch = JOB_BATCH
      self.current_index = 0
      self.old_index = 0
      self.double_index = 0
      self.batch_rate_af = 0
      self.total_rate = 0
      self.burst_state = 0
      self.old_burst_state = 0
      self.burst_delay = 0
      self.burst_delay_switch = BURST_DELAY_SWITCH
      self.burst_start = 0
      self.num_batch = 0
      self.low_rate_check = 0
      self.last_arrival = 0 
      self.last_batch_time = 0
      self.mid_batch_time = 0
      self.iats =[] #new double[job_batch]
      for i in range (0,self.job_batch):
         self.iats.append(0)
      self.double_iats = []#new double[2*job_batch]
      for i in range (0,2*self.job_batch):
         self.double_iats.append(0)
         
         
         
   
   def Check_BurstState(self, real_arrival):
       if (self.tmp_num_job < self.job_batch) and (real_arrival > self.last_arrival):
          self.double_iats[self.job_batch + self.tmp_num_job] = real_arrival - self.last_arrival
          self.iats[self.tmp_num_job] = real_arrival - self.last_arrival
          self.tmp_num_job +=1    #+: accumulate jobs for each batch

          if (self.tmp_num_job == self.job_batch / 2):
             self.mid_batch_time = real_arrival

          if (self.tmp_num_job == self.job_batch):
          
            self.num_batch +=1

            self.current_index = est_index_dispersion(self.iats, self.job_batch, self.job_batch / 2)
            self.batch_rate_af = float(self.job_batch / 2.0 / (real_arrival - self.mid_batch_time))
            self.total_rate = float(self.job_batch*self.num_batch/real_arrival)

            #2.1
            if (self.num_batch != 1):   #no judge for the first job batch
            
               self.double_index = est_index_dispersion(self.double_iats, 2 * self.job_batch, self.job_batch / 2) #?
               #2.1.1--------------------------- non-burst state -----------------------------------------
               if (self.burst_state == 0):  #non-burst
               
                  #assert(self.low_rate_check == 0);
                  if(self.low_rate_check != 0):
                     exit()

                  if (self.batch_rate_af > 3 * self.total_rate):
                    if ((self.double_index/self.current_index) > 4 or (self.double_index/self.old_index) > 3 or (self.current_index/self.old_index) > 4 or (self.old_index/self.current_index) > 4):
                    
                       self.burst_state = 1
                       self.burst_start = real_arrival
                       self.burst_delay = 0
                       #turn to burst
               
               #2.1.2--------------------------- burst state ---------------------------------------------
               elif (self.burst_state == 1): #burst
               
                  if (self.burst_delay == 0):#check burst end
                  
                     if (self.batch_rate_af < 5 * self.total_rate):
                     
                        if ((self.double_index/self.current_index) > 3 or (self.double_index/self.old_index) > 4 or (self.current_index/self.old_index) > 4 or (self.old_index/self.current_index) > 4):
                        
                          self.low_rate_check = 0
                                    
                          if ((self.last_batch_time - self.burst_start) < MIN_BURST_DURATION):          #min duration time
                          
                             if (self.burst_delay_switch == 0):                              #0 - burst delay off
                                self.burst_state = 0
                             elif (self.burst_delay_switch == 1):                              #1 - burst delay on
                                self.burst_delay = MIN_BURST_DELAY                                 #delay MIN_BURST_DELAY self.job_batch
                             else:
                             
                                printf("\nburst_delay_switch error\n")
                                exit(0)
                             
                          
                          else:
                             self.burst_state = 0
                        
                        else: #sequential low rate check
                        
                           if (self.low_rate_check == 0):
                              self.low_rate_check +=1
                           elif (self.low_rate_check == 1):                         #two sequential low rate batch turn to burst_state=0
                           
                              self.low_rate_check = 0
                              self.burst_state = 0
                           
                           else:
                           
                              printf("\nself.low_rate_check error\n")
                              exit(0)
                           
                        
                     
                     
                     else:
                        self.low_rate_check = 0
                  
                  elif (self.burst_delay > 0):     #delay
                  
                     if (self.batch_rate_af > 3 * self.total_rate): #check next burst during delay
                     
                        if ((self.double_index/self.current_index) > 4 or (self.double_index/self.old_index) > 3 or (self.current_index/self.old_index) > 4 or (self.old_index/self.current_index) > 4):
                        
                           self.burst_state = 1
                           self.burst_start = real_arrival
                           self.burst_delay = 0
                           #not change burst status(next burst arrive)
                        else: 
                           
                           self.burst_delay -=1
                           if (self.burst_delay == 0):
                              self.burst_state = 0
                            #delay--
                     
                     else:
                        
                        self.burst_delay -=1
                        if (self.burst_delay == 0):
                           self.burst_state = 0
                            #delay--
                  
                  else:
                     printf("burst_delay error\n")
               
               #2.1.3
               else:
                  printf("burst_state error\n")
               
            for i in range(0, self.job_batch):
            #for (int i = 0; i < self.job_batch; i++)
               self.double_iats[i] = self.double_iats[self.job_batch + i]
                     
            self.old_index = self.current_index
            self.last_batch_time = real_arrival
            self.tmp_num_job = 0
             

       self.last_arrival = real_arrival

       return self.burst_state

