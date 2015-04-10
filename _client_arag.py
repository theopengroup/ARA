#! /usr/bin/python
import sys, os
import socket
import sys
import random
import linecache
import operator
import time
import thread

from _burstDetection import *



if len(sys.argv)<=4:
   print 'python client.py [(1)traceFile] [(2)policy] [(3)VM_Mode] [(4)burstyDetectionMode] [(5)lowerThreshold] [(6)upperThreshold]\n'
   print '(2) policy:\n'
   print '1=Rand\t2=JSQ_Qlen\t3=JSQ_CPU\t4=JSQ_Probe1\n'
   print '5=JSQ_Probe2\t6=JSQ_QlenAndProbe\n'
   print '(3) VM_Mode: 1=homoPM 2=hetePM\n'
   print '(4) burstyDetectionMode: 0=OFF\t1=ON\n'
   print '(5) lowerThreshold: from 1 to 8\n'
   print '(6) upperThreshold: from 1 to 8\n'
   exit
   


###############################################################################
# Initializing Parameters                                                     #
###############################################################################
# policy
# 1=Rand 2=JSQ_Qlen 3=JSQ_CPU 4=JSQ_Probe1 5=JSQ_Probe2 6=JSQ_QlenAndProbe
policy=int(sys.argv[2])

# VM_Mode
# 1=homo 2=hete
VM_Mode=int(sys.argv[3])

# k
k=1

################## Under Develop #################
# burstyDetectionMode
burstyDetectionMode=int(sys.argv[4])

# threshold
upperThreshold=8
lowerThreshold=1

#################################################################################

# recentSysInfoNum
recentSysInfoNum=1
recentQlenNum=1

# IP address library
serverPort=5200
#serverPort=5201


serverIp=['XXXXX155']
serverThreadFlag=[False]
if VM_Mode==2:
   serverIp.append('XXXXX156')
   serverThreadFlag.append(False)
   
serverSock=dict()


# VM IP address library
PM1_Ip=['192.168.122.85', '192.168.122.159','192.168.122.224','192.168.122.15']
PM2_Ip=['192.168.122.107','192.168.122.100','192.168.122.68','192.168.122.39']
#PM1_Ip=['192.168.122.231','192.168.122.188','192.168.122.210','192.168.122.109']
#PM2_Ip=['192.168.122.142','192.168.122.244','192.168.122.243','192.168.122.247']
allIp=PM1_Ip+PM2_Ip

vmQlen=dict()
vmQlenHistory=dict()
vmSysInfo=dict()
vmSysInfoHistory=dict()
vmJobCount=dict()
vmProbe1Time=dict()
vmProbe1TimeHistory=dict()

#20150112
vmProbe2Time=dict()
vmProbe2TimeHistory=dict()

vmJobSentFlag=dict()

for ip in PM1_Ip:
   vmQlen[ip]=0.0
   vmQlenHistory[ip]=[]
   vmSysInfo[ip]=0.0
   vmSysInfoHistory[ip]=[]
   vmJobCount[ip]=0.0
   vmProbe1Time[ip]=0.0
   vmProbe1TimeHistory[ip]=[]
   vmProbe2Time[ip]=0.0 #20150112
   vmProbe2TimeHistory[ip]=[]
if VM_Mode==2:
   for ip in PM2_Ip:
      vmQlen[ip]=0.0
      vmQlenHistory[ip]=[]
      vmSysInfo[ip]=0.0
      vmSysInfoHistory[ip]=[]
      vmJobCount[ip]=0.0
      vmProbe1Time[ip]=0.0
      vmProbe1TimeHistory[ip]=[]
      vmProbe2Time[ip]=0.0 #20150112
      vmProbe2TimeHistory[ip]=[]


##################################################################################
# Client                                                                         #
##################################################################################
vmAverageQlen=dict()
vmAverageSysInfo=dict()


##################################################################################
# dict jobResponseTime:                                                          #
# jobID, [0.sendTime, 1.recvTime, 2.recvTime-sendTime, 3.jobSizeOfFib, 4.sendVM] #
##################################################################################
jobResponseTime=dict()             
averageJobResponseTime=0
totalJobResponseTime=0


#20141017
############################################################################################################################################################
# dict vmPerfRecordedByClient:                                                                                                                             #
# vmIP, [0.firstJobSendTime,1.lastJobRecvTime,2.totalJobAmount,3.totalJobNumber,4.totalRespTime,5.respTimePerJobCount,6.mkspPerJobAmount,7.mkspPerJobNum]  # ############################################################################################################################################################
vmPerfRecordedByClient=dict()
#20141103
########################################################
# dict vmArrivalRate:                                  #
# vmIP, [0.arrivalRateInJobAmt, 1.arrivalRateInJobNum] #
########################################################
vmArrivalRate=dict()

#20141024
####################################################################################################################################################################
# dict pmPerfRecordedByClient:                                                                                                                                     #
# pmID, [0.firstJobSendTime, 1.lastJobRecvTime, 2.totalJobAmount, 3.totalJobNumber, 4.totalRespTime, 5.respTimePerJobCount, 6.mkspPerJobAmount, 7.mkspPerJobNum]   #     
####################################################################################################################################################################
pmPerfRecordedByClient=dict()
#  pm1
pmPerfRecordedByClient[0]=[-1,0,0,0,0,0,0,0]
if VM_Mode==2: # pm2
   pmPerfRecordedByClient[1]=[-1,0,0,0,0,0,0,0]



#20141022
##################################################################################
# VM-Summary                                                                     #
# [vmIP],[averageJobResponseTime]                                                #
# [vmIP],[0.averageJobServiceTimePefJobAmount, 1.averageJobServiceTimePefJobNum] #
##################################################################################
vmAverageJobResponseTime=dict()
vmAverageJobServiceTime=dict()





# 20141021
###################################################################################
# overallPerfServRate = (lastJobRecvTime-firstJobRecvTime)/allJobCount            #
###################################################################################
fisrtJobSendTime=0
lastJobRecvTime=0
allJobCount=0


# vmJobCount


# logFiles
folderName=sys.argv[1]+"-"+sys.argv[2]+"-"+sys.argv[3]+"-"
logFileJobResponseTime = file(str(folderName+'logFileJobResponseTime.txt'), 'w',0)
logFileQlen = file(str(folderName+'logFileQlen.txt'),'w',0)
logFileSysInfo = file(str(folderName+'logFileSysInfo.txt'),'w',0)
logFileSummary = file(str(folderName+'logFileSummary.txt'),'w',0)
logFileBursty = file(str(folderName+'logFileBursty.txt'),'w',0)
logFileProbe1 =  file(str(folderName+'logFileProbe1.txt'),'w',0)
logFileProbe2 =  file(str(folderName+'logFileProbe2.txt'),'w',0)
# recvResultCounter
recvResultNum=0

lineNum=0

allJobSent=False


def main():
   global recvResultNum
   global vmQlen
   global vmQlenHistory
   global vmSysInfo
   global vmSysInfoHistory
   global jobResponseTime
   global vmJobCount
   global lineNum
   global vmAverageJobResponseTime 
   global vmAverageJobServiceTime
   global allJobSent
   global fisrtJobSendTime
   global lastJobRecvTime
   global allJobCount
   global k
   ############################
   # Connect to servers #######
   ############################
   print 'Now connect to servers'
   for ip in serverIp:
      print 'Connecting to server '+ip
      serverSock[ip] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      serverSock[ip].connect((ip,serverPort))

   burstDetector=burstDetection() 
   
   #lineNum=0
   lastTime=0
   traceFile=open(sys.argv[1],"r")
   oneTimeWriteToFileFlag = False
   
   t1=time.time()

   #
   firstJobArrivalTime=-1
   firstJobSendTime=-1


   try:
      for line in open(sys.argv[1]):
         # trace=[timeStamp, fibJobSize, fibJobCount]
         (curTime, jobSize, jobCount)=line.strip().split(',')[0:3]
         curTime=float(curTime)
         print 'sleep=', (float(curTime)-lastTime)
         time.sleep(float(curTime)-lastTime)
         lastTime=float(curTime)
         jobSize=int(jobSize)
         jobCount=int(jobCount)

         allJobCount=allJobCount+jobCount

         ###################
         # Sending jobs#####
         ###################
         curSelectedVM=''

         ##########################
         # burstyDetectionMode    #
         ##########################
         if burstyDetectionMode==1:
            if burstDetector.Check_BurstState(curTime)==1:
               print 'curTime=',curTime,'bursty=1,k=',k
               k=upperThreshold
               logFileBursty.write(str(curTime)+"\t1\n")
            else:
               print 'curTime=',curTime,'bursty=0,k=',k
               k=lowerThreshold
               logFileBursty.write(str(curTime)+"\t0\n")

         ##########################################################
         # warming up period, in order to let all VMs have job    #
         ##########################################################
         if VM_Mode==1 and lineNum<(5*len(PM1_Ip)):
            curSelectedVM=PM1_Ip[lineNum%len(PM1_Ip)]
            print '### Warming up for the first 5*len(VM) lines, line=',lineNum
         elif VM_Mode==2 and lineNum<(5*len(allIp)):
            curSelectedVM=allIp[lineNum%len(allIp)]
            print '### Warming up for the first 5*len(VM) lines, line=',lineNum
         else:
            ############################################################################################
            # policy                                                                                   #
            # 1=Rand 2=JSQ_Qlen 3=JSQ_CPU 4=JSQ_Probe1 5=JSQ_Probe2 6=JSQ_QlenAndProbe 7=ARA_JSQ_Qlen  #
            ############################################################################################
            # Rand
            if policy==1:
               curSelectedVM=Rand()

            # JSQ_Qlen
            elif policy==2:
               curSelectedVM=JSQ_Qlen(k,jobSize,jobCount)

            # JSQ_CPU
            elif policy==3:
               curSelectedVM=JSQ_QlenSysInfoProbeTime(3,k,jobSize,jobCount)

            # JSQ_Probe1
            elif policy==4:
               curSelectedVM=JSQ_QlenSysInfoProbeTime(4,k,jobSize,jobCount)

            # JSQ_Probe2
            elif policy==5:
               curSelectedVM=JSQ_QlenSysInfoProbeTime(5,k,jobSize,jobCount)

            # JSQ_QlenAndProbe
            elif policy==6:
               curSelectedVM=JSQ_QlenSysInfoProbeTime(6,k,jobSize,jobCount)        

         lineNum=lineNum+1
  
         print 'curSelectedVM=',curSelectedVM
         ###############################################
         # message = [ IP, jobID-jobSize-jobCount, ] ###
         ###############################################
         argStr=curSelectedVM+','+str(lineNum)+'-'+str(jobSize)+'-'+str(jobCount)+','
         print argStr
         
     
         ###############################################################################################
         # jobResponseTime                                                                             #
         # jobID, [0.sendTime, 1.recvTime, 2.recvTime-sendTime, 3.jobSizeOfFib, 4.sendVM]              #
         ###############################################################################################
         jobResponseTime[str(lineNum)]=[time.time(),0,0,jobCount,curSelectedVM]
         
         vmJobCount[curSelectedVM]+=1 
         vmJobSentFlag[curSelectedVM]=True

         if firstJobSendTime==-1:
            firstJobSendTime=time.time()

         print '###',line
         if curSelectedVM in PM1_Ip:
            print 'Send job to server 1'
            serverSock[serverIp[0]].sendall(argStr)
            #####################################
            # Create a receiving thread #########
            #####################################
            if serverThreadFlag[0]==False:
               thread.start_new_thread(ServerThread, (serverSock[serverIp[0]],))
               serverThreadFlag[0]=True
   
         elif curSelectedVM in PM2_Ip:
            print 'Send job to server 2'
            serverSock[serverIp[1]].sendall(argStr)     
            #####################################
            # Create a receiving thread #########
            #####################################
            if serverThreadFlag[1]==False:
               thread.start_new_thread(ServerThread, (serverSock[serverIp[1]],))
               serverThreadFlag[1]=True
      oneTimeWriteToFileFlag = True 
   except KeyboardInterrupt:
      print "Keyboard stroke"
   finally:
      if oneTimeWriteToFileFlag!=True:
         logFileJobResponseTime.write(str(jobResponseTime))
         logFileJobResponseTime.flush()
         logFileJobResponseTime.close()

         logFileQlen.write("first write is here\n")
         logFileQlen.write(str(vmQlenHistory))
         logFileQlen.flush()
         logFileQlen.close()

         logFileSysInfo.write(str(vmSysInfoHistory))
         logFileSysInfo.flush()
         logFileSysInfo.close()    
 
         logFileProbe1.write(str(vmProbe1TimeHistory))
         logFileProbe1.flush()
         logFileProbe1.close() 

         logFileProbe2.write(str(vmProbe2TimeHistory))
         logFileProbe2.flush()
         logFileProbe2.close()    

   print 'jobResponseTime', jobResponseTime
   print 'vmQlen', vmQlen
   print 'vmQlenHistory', vmQlenHistory
   print 'vmSysInfo', vmSysInfo
   print 'vmSysInfoHistory', vmSysInfoHistory
   print 'vmProbe1TimeHistory', vmProbe1TimeHistory
   print 'vmProbe2TimeHistory', vmProbe2TimeHistory
   print 'vmAverageJobResponseTime',vmAverageJobResponseTime
   print 'vmAverageJobServiceTime', vmAverageJobServiceTime
   print 'vmPerfRecordedByClient',vmPerfRecordedByClient
   print 'pmPerfRecordedByClient',pmPerfRecordedByClient


   allJobSent=True

   #########################################
   # After sent all jobs, wait all results #
   #########################################
   try:
      while recvResultNum != lineNum:
         pass
      #####################################################
      # After all results are received, collect summaries #
      #####################################################
      print 'All results are received, now collecting summaries'
      argStr='askSummary,askSummary,'
      for ip in serverSock:
         serverSock[ip].sendall(argStr)

      #################################
      # received by the ServerThread ##
      #################################
      while len(vmAverageJobResponseTime) != len(vmJobSentFlag) :
         time.sleep(5)         
         print 'recvSummaryNum=', len(vmAverageJobResponseTime)
          

   except KeyboardInterrupt:
      print "Keyboard stroke"


   finally:
      print '-------------recvResultNum=',recvResultNum
      print '-------------traceLineNum=',lineNum
      print '####################### Summary ###################################'
      print '####################### Settings ##################################'
      logFileSummary.write('Trace='+sys.argv[1])
      print('Trace=',sys.argv[1])
      logFileSummary.write( '-------------recvResultNum='+str(recvResultNum)+'\n')
      logFileSummary.write( '-------------traceLineNum='+str(lineNum)+'\n')
      logFileSummary.write( '####################### Summary ###################################'+'\n')
      logFileSummary.write( '####################### Settings ##################################'+'\n')
      if policy==1:
         print 'Policy=Rand'
         logFileSummary.write( 'Policy=Random'+'\n')
      if policy==2:
         print 'Policy=JSQ_Qlen, k=',k
         logFileSummary.write( 'Policy=JSQ_Qlen, k='+str(k)+'\n')
      if policy==3:
         print 'Policy=JSQ_CPU, k=',k
         logFileSummary.write( 'Policy=JSQ_CPU, k='+str(k)+'\n')
      if policy==4:
         print 'Policy=JSQ_Probe1, k=', k
         logFileSummary.write( 'Policy=JSQ_Probe1, k='+str(k)+'\n')
      if policy==5:
         print 'Policy=JSQ_Probe2, k=', k 
         logFileSummary.write( 'Policy=JSQ_Probe2, k='+str(k)+'\n' )
      if policy==6:
         print 'Policy=JSQ_QlenAndProbe, k=', k 
         logFileSummary.write( 'Policy=JSQ_QlenAndProbe, k='+str(k)+'\n' )      



   
      print 'Trace Line=', lineNum
      print '####################### Client Side #################################'
      print '1. TotalJobResponseTime=', time.time()-t1
      print '2. AverageJobResponseTime=',getAverageJobResponseTime()
      print '3. TotalJobSend=',vmJobCount

      print '4.1 [Dev] EachUser-ServRate: TotalJobAmount/TotalMksp(NoInterval)=', float(allJobCount/(lastJobRecvTime-firstJobSendTime))
      print '4.2 [Dev] EachUser-ServRate: TotalJobNum/TotalMksp(NoInterval)=', float(lineNum/(lastJobRecvTime-firstJobSendTime))


      print '# vmIP,[0.firstJobSendTime,1.lastJobRecvTime,2.totalJobAmount,3.totalJobNumber,4.totalRespTime,5.respTimePerJobCount,6.mkspPerJobAmount,7.mkspPerJobNum] #'
      print '5 [Dev] EachVM-ServRate: TotalJobAmount(or TotalJobNum)/TotalMksp(NoInterval)=', str(vmPerfRecordedByClient)
      
      print '6 [Dev] EachPM-ServRate: TotalJobAmount(or TotalJobNum)/TotalMksp(NoInterval)=', str(pmPerfRecordedByClient)

      print '####################### VM Side  ####################################'
      print '1. [Dev] EachVM-AvgJobRespTime=', vmAverageJobResponseTime 

      print '2. [Dev] EachVM-AvgJobServTime=', vmAverageJobServiceTime 

      print '3. [Dev] EachVM-ArrivalRate=', vmArrivalRate

      getVMAverageSysInfo()
      print '4. AverageCPU=', vmAverageSysInfo

      tmpList = vmAverageSysInfo.values()
      AllAvgCPU = sum(tmpList)/float(len(tmpList))      
      print '5. AllAverageCPU=',AllAvgCPU 

      getVMAverageQlen()
      print '6. AverageQlen=', vmAverageQlen
            

      # 20141227 disable #
      print '####################### Client Side #################################'
      #usageInJobAmt=dict()    
      #usageInJobNum=dict()     
      #for vmIP in vmArrivalRate:
      #   usageInJobAmt[vmIP]=float(float(vmArrivalRate[vmIP][0])*float(vmAverageJobServiceTime[vmIP][0]))
      #   usageInJobNum[vmIP]=float(float(vmArrivalRate[vmIP][1])*float(vmAverageJobServiceTime[vmIP][1]))
      
      ##############################################################################################################
      # vmArrivalRate: [vmIP], [0.arrivalRateInJobAmt, 1.arrivalRateInJobNum]                                      #
      # vmAverageJobServiceTime: [vmIP],[0.averageJobServiceTimePefJobAmount, 1.averageJobServiceTimePefJobNum]    #
      ##############################################################################################################


      #print '1.1 [Dev] EachVM-Usage (in jobAmt): p=lambda/u=', usageInJobAmt 
      #print '1.2 [Dec] AvgEachVM-Usage (in jobAmt): p=lambda/u=', str(getAvg(usageInJobAmt)) 
      #print '2.1 [Dev] EachVM-Usage (in jobNum): p=lambda/u=', usageInJobNum 
      #print '2.2 [Dec] AvgEachVM-Usage (in jobNum): p=lambda/u=', str(getAvg(usageInJobNum)) 

      
      




      print '#####################################################################'

            
      logFileSummary.write( 'Trace Line='+ str(lineNum)+'\n')
      logFileSummary.write( '####################### Client Side #################################'+'\n')
      logFileSummary.write( '1. TotalJobResponseTime='+ str(time.time()-t1)+'\n')
      logFileSummary.write( '2. AverageJobResponseTime='+str(getAverageJobResponseTime())+'\n')
      logFileSummary.write( '3. TotalJobSend='+str(vmJobCount)+'\n')
      logFileSummary.write( '####################### VM Side  ####################################'+'\n')
      logFileSummary.write( '4. AverageJobResponseTime='+ str(vmAverageJobResponseTime) +'\n')
      logFileSummary.write( '5. AverageCPU='+ str(vmAverageSysInfo)+'\n')
      logFileSummary.write( '6. AllAverageCPU='+str(AllAvgCPU)+'\n')
      logFileSummary.write( '7. AverageQlen='+ str(vmAverageQlen)+'\n')
      #logFileSummary.write( '8. EachVMServRate: TotalAvgRespTime/TotalJobAmount='+str(vmPerfRecordedByClient)+'\n')
      logFileSummary.write( '#####################################################################'+'\n')
      logFileSummary.flush()   
      logFileSummary.close()
 
      logFileJobResponseTime.write(str(jobResponseTime))
      logFileJobResponseTime.flush()
      logFileJobResponseTime.close()

      logFileQlen.write("second write is here\n")
      logFileQlen.write(str(vmQlenHistory))
      logFileQlen.flush()
      logFileQlen.close()


      logFileSysInfo.write(str(vmSysInfoHistory))
      logFileSysInfo.flush()
      logFileSysInfo.close()  


      logFileBursty.flush() 
      logFileBursty.close()

      logFileProbe1.write(str(vmProbe1TimeHistory))
      logFileProbe1.flush()
      logFileProbe1.close()  

      logFileProbe2.write(str(vmProbe2TimeHistory))
      logFileProbe2.flush()
      logFileProbe2.close()  


def ServerThread(conn):
  global jobResponseTime
  global vmQlenHistory
  global vmSysInfoHistory
  global vmProbe1Time
  global vmProbe1TimeHistory
  global vmProbe2Time
  global vmProbe2TimeHistory
  global recvResultNum
  global lineNum
  global recvSummaryNum
  global allJobSent
  global lastJobRecvTime
  while True:
     print '========================Receive Data========================'
     dataRecv = conn.recv(4096)
     print 'receivedData=', dataRecv
     if not dataRecv:
        print 'No more data'
        break
     else:
        dataRecv = dataRecv.strip().split(',')
        print '========================Receive Data========================'

        #if (len(dataRecv)-1) % 2 != 0:
        #   print 'Error: %s' % dataRecv
        #   break

        numData = len(dataRecv) /2  #sometime multiple data received together, need to split to multiple commands
        print 'numData=', numData
         
        try:
           for i in xrange(numData):
              #########################################################################################################################
              # recvMsg1=[result, ip-jobID-result]                                                                                    #
              # recvMsg2=[status, ip-qlen-sysInfo-probeTime-probe2(servRate)]                                                         #
              # recvMsg3=[summary,ip-vmAverageJobResponseTime-vmAverageJobServicTimePerJobAmount-vmAverageJobServicTimePerNum-lambda] #
              #########################################################################################################################
              tmpData = dataRecv[i*2:i*2+2]
              print '+++++++++',tmpData
              if tmpData[0]=='':
                 continue
              if tmpData[0]=='result':
                 print '\n\n\n=======================[Result] data[',i,']========================',tmpData
                 tmpSubData=tmpData[1].strip().split('-') 
                 #####################################################################################
                 # list: ip, jobID, result                                                           #
                 # tmpSubData[0]=ip, tmpSubData[1]=jobID, tmpSubData[2]=result                       #
                 # Update dict jobResponseTime:                                                      #
                 # jobID, [0.sendTime, 1.recvTime, 2.recvTime-sendTime, 3.jobSizeOfFib, 4.sendVM]    #
                 #####################################################################################
                 jobResponseTime[tmpSubData[1]][1]= time.time() # updating (1)
                 lastJobRecvTime=jobResponseTime[tmpSubData[1]][1] # lastJobRecvTime
                 jobResponseTime[tmpSubData[1]][2]= jobResponseTime[tmpSubData[1]][1]- jobResponseTime[tmpSubData[1]][0]  # updating (2)
                 print tmpSubData[1], jobResponseTime[tmpSubData[1]] # print jobResponseTime(currIP) line
                 logFileJobResponseTime.write(tmpSubData[1] + str(jobResponseTime[tmpSubData[1]]) + '\n')  #log file
                 recvResultNum+=1

                 ##########################################################################################################################################################
                 # 20141017                                                                                                                                               #
                 # update dict vmPerfRecordedByClient:                                                                                                                    #
                 # vmIP,[0.firstJobSendTime,1.lastJobRecvTime,2.totalJobAmount,3.totalJobNumber,4.totalRespTime,5.respTimePerJobCount,6.mkspPerJobAmount,7.mkspPerJobNum] #
                 # If this current received finished job's VM ip is not in the vmPerfRecordedByClient, then this is the first finished job from that VM.                  #                 
                 # We record this first job's send-to-VM time as this VM's first-job-send time (0).                                                                       #
                 # We keep updating the current received finished job's time to the lastJobRecvTime (1).                                                                  #
                 ##########################################################################################################################################################
                 if tmpSubData[0] not in vmPerfRecordedByClient: 
                    vmPerfRecordedByClient[tmpSubData[0]]=[0,0,0,0,0,0,0,0,0] # initialize the list
                    vmPerfRecordedByClient[tmpSubData[0]][0]=jobResponseTime[tmpSubData[1]][0] # 0.firstJobSendTime
                 vmPerfRecordedByClient[tmpSubData[0]][1]=time.time() # 1.lastJobRecvTime
                 vmPerfRecordedByClient[tmpSubData[0]][2]=vmPerfRecordedByClient[tmpSubData[0]][2]+jobResponseTime[tmpSubData[1]][3] # 2.totalJobCount(size)
                 vmPerfRecordedByClient[tmpSubData[0]][3]=vmPerfRecordedByClient[tmpSubData[0]][3]+1 # 3.totalJobNumer
                 vmPerfRecordedByClient[tmpSubData[0]][4]=vmPerfRecordedByClient[tmpSubData[0]][4]+jobResponseTime[tmpSubData[1]][2] # 4.totalRespTime
                 vmPerfRecordedByClient[tmpSubData[0]][5]=float(vmPerfRecordedByClient[tmpSubData[0]][4]/vmPerfRecordedByClient[tmpSubData[0]][2]) # 5.respTimePerJobCount=(4)/(2)
                 vmPerfRecordedByClient[tmpSubData[0]][6]=float(vmPerfRecordedByClient[tmpSubData[0]][2]/(vmPerfRecordedByClient[tmpSubData[0]][1]-vmPerfRecordedByClient[tmpSubData[0]][0])) # 6.mkspPerJobAmmount=(2)/(1-0)
                 vmPerfRecordedByClient[tmpSubData[0]][7]=float(vmPerfRecordedByClient[tmpSubData[0]][3]/(vmPerfRecordedByClient[tmpSubData[0]][1]-vmPerfRecordedByClient[tmpSubData[0]][0])) # 7.mkspPerJobNum=(3)/(1-0)

               
                 ####################################################################################################################################################################
                 # 20141024                                                                                                                                                         #
                 # update dict pmPerfRecordedByClient:                                                                                                                              #
                 # vmIP, [0.firstJobSendTime, 1.lastJobRecvTime, 2.totalJobAmount, 3.totalJobNumber, 4.totalRespTime, 5.respTimePerJobCount, 6.mkspPerJobAmount, 7.mkspPerJobNum]   #                                                                                                       
                 # If this current received finished job's VM ip is not in the pmPerfRecordedByClient, then this is the first finished job from that VM.                            #
                 # We record this first job's send-to-VM time as this VM's first-job-send time (0).                                                                                 #
                 # We keep updating the current received finished job's time to the lastJobRecvTime (1).                                                                            #
                 ####################################################################################################################################################################
                 if tmpSubData[0] in PM1_Ip: # tmpSubData[0] is vmIP
                    curPM=0
                 else:
                    curPM=1

                 # tmpSubData[0]=ip, tmpSubData[1]=jobID, tmpSubData[2]=result 

                 # 0.firstJobSendTime
                 # first job of each PM, update only once
                 if pmPerfRecordedByClient[curPM][0]==-1:
                    pmPerfRecordedByClient[curPM][0]=jobResponseTime[tmpSubData[1]][0] #jobID
                
                 # 1.lastJobRecvTime
                 pmPerfRecordedByClient[curPM][1]=vmPerfRecordedByClient[tmpSubData[0]][1] #ip

                 # 2.totalJobCount(size)
                 pmPerfRecordedByClient[curPM][2]=pmPerfRecordedByClient[curPM][2]+jobResponseTime[tmpSubData[1]][3]

                 # 3.totalJobNumer
                 pmPerfRecordedByClient[curPM][3]=pmPerfRecordedByClient[curPM][3]+1

                 # 4.totalRespTime
                 pmPerfRecordedByClient[curPM][4]=pmPerfRecordedByClient[curPM][4]+jobResponseTime[tmpSubData[1]][2]

                 # 5.respTimePerJobCount=(4)/(2)
                 pmPerfRecordedByClient[curPM][5]=float(pmPerfRecordedByClient[curPM][4]/pmPerfRecordedByClient[curPM][2]) 

                 # 6.mkspPerJobAmount=(2)/(1-0)
                 pmPerfRecordedByClient[curPM][6]=float(pmPerfRecordedByClient[curPM][2]/(pmPerfRecordedByClient[curPM][1]-pmPerfRecordedByClient[curPM][0])) 

                 # 7.mkspPerJobNum=(3)/(1-0)
                 pmPerfRecordedByClient[curPM][7]=float(pmPerfRecordedByClient[curPM][3]/(pmPerfRecordedByClient[curPM][1]-pmPerfRecordedByClient[curPM][0])) 

              # 20150112
              ##################################################################################################################
              # recvMsg2=[status, 0.ip-1.qlen-2.sysInfo-3.probe1-4.probe2]                                                     #
              ##################################################################################################################
              if tmpData[0]=='status':
                 if (allJobSent==True & recvResultNum==lineNum):
                    pass
                 else:
                    print '\n\n\n========================[Status] data[',i,']========================',tmpData
                    tmpSubData=tmpData[1].strip().split('-')
                    vmQlen[tmpSubData[0]]=float(tmpSubData[1])
                    vmQlenHistory[tmpSubData[0]].append(float(tmpSubData[1]))
                    vmSysInfo[tmpSubData[0]]=float(tmpSubData[2])
                    vmSysInfoHistory[tmpSubData[0]].append(float(tmpSubData[2]))
                    vmProbe1Time[tmpSubData[0]]=float(tmpSubData[3])
                    vmProbe1TimeHistory[tmpSubData[0]].append(float(tmpSubData[3]))
                    ################
                    # probe 2      #
                    # ##############
                    print '###########recvProbe2=',float(tmpSubData[4])
                    vmProbe2Time[tmpSubData[0]]=float(tmpSubData[4])
                    vmProbe2TimeHistory[tmpSubData[0]].append(float(tmpSubData[4]))
                    print '----------recvResultNum=',recvResultNum
                    print '----------sentJobNum=', lineNum

              ######################################################################################################################################################
              # recvMsg3=[summary,0.ip-1.vmAverageJobResponseTime-2.vmAverageJobServicTimePerJobAmount-3.vmAverageJobServicTimePerNum-4.lambdaAmt-5.lambdaNum]     #
              ######################################################################################################################################################
              #['summary', '0=192.168.122.15-1=10.7593183517-2=0.0859572800965-3=6.84792998102-4=6.94457076857-5=0.0871703443754']
              if tmpData[0]=='summary':
                 print '\n\n\n========================[Summary] data[',i,']========================',tmpData
                 tmpSubData=tmpData[1].strip().split('-')
                 # 0.ip
                 vmAverageJobResponseTime[tmpSubData[0]]=tmpSubData[1] # 1.vmAverageJobResponseTime
                 vmAverageJobServiceTime[tmpSubData[0]]=[tmpSubData[2],tmpSubData[3]] # 2.vmAverageJobServicTimePerJobAmount-3.vmAverageJobServicTimePerNum
                 # vmAverageJobServiceTime: [vmIP],[0.averageJobServiceTimePefJobAmount, 1.averageJobServiceTimePefJobNum] 
                
                 vmArrivalRate[tmpSubData[0]]=[ tmpSubData[4] , tmpSubData[5] ] #lambdaAmt, lambdaNum
                                  
        except KeyboardInterrupt:
           print 'ServerThread Terminate'

# 1 Rand
def Rand():
   return random.choice(vmQlen.keys())



# 2
# JSQ_Qlen
def JSQ_Qlen(k,jobSize,jobCount):
   global vmQlenHistory
   global recentQlenNum   

   recentQlen=dict()

   curSum=0
   
   for ip in vmQlenHistory:
      curListLen=len(vmQlenHistory[ip])

      # no Qlen record, then assign avgRecentQlen=0
      if curListLen==0:
         recentQlen[ip]=0.00

      # Qlen record is less than window size
      elif curListLen<recentQlenNum:
         for i in vmQlenHistory[ip]:
            curSum=curSum+float(i)
         recentQlen[ip]=curSum / float(curListLen)
         curSum=0
      
      # Qlen record is larger than window size
      else:
         for i in range(curListLen-1, curListLen-1-recentQlenNum,-1):
            curSum=curSum+float(vmQlenHistory[ip][i]) 
         recentQlen[ip]=curSum / float(recentQlenNum)
         curSum=0

   
   sortedRecentQlen = sorted( recentQlen.iteritems(), key=operator.itemgetter(1)   )
   print sortedRecentQlen
   numOfSameSmallestItem=0
   for item in sortedRecentQlen:
      if item[1] == sortedRecentQlen[0][1]:
         numOfSameSmallestItem=numOfSameSmallestItem+1
      else:
         break
   if k>=numOfSameSmallestItem:
      return sortedRecentQlen[int(random.sample(range(k), 1)[0])][0]
   else:
      return sortedRecentQlen[int(random.sample(range(numOfSameSmallestItem), 1)[0])][0] 
   #20150108
   #if k>=numOfSameSmallestItem:
   #   return sortedRecentQlen[random.randint(0,k-1)][0]
   #else:
   #   return sortedRecentQlen[random.randint(0,numOfSameSmallestItem-1)][0] 


######################################################################
# 3...                                                               #
# JSQ_QlenSysInfoProbeTime                                           #
# modeID                                                             #
# 3=CPU                                                              #
# 4=Probe1                                                           #
# 5=Probe2                                                           #
# 6=Qlen+Probe1                                                      #
######################################################################
def JSQ_QlenSysInfoProbeTime(modeID, k,jobSize,jobCount):
   ################
   # Qlen         #
   ################
   global vmQlenHistory
   global recentQlenNum   

   recentQlen=dict()
   curSum=0


   for ip in vmQlenHistory:
      curListLen=len(vmQlenHistory[ip])

      # no Qlen record, then assign avgRecentQlen=0
      if curListLen==0:
         recentQlen[ip]=0.00

      # Qlen record is less than window size
      elif curListLen<recentQlenNum:
         for i in vmQlenHistory[ip]:
            curSum=curSum+float(i)
         recentQlen[ip]=curSum / float(curListLen)
         curSum=0
      
      # Qlen record is larger than window size
      else:
         for i in range(curListLen-1, curListLen-1-recentQlenNum,-1):
            curSum=curSum+float(vmQlenHistory[ip][i]) 
         recentQlen[ip]=curSum / float(recentQlenNum)
         curSum=0
      
   ################
   # CPU          #
   ################
   global vmSysInfoHistory
   global recentSysInfoNum   

   recentSysInfo=dict()
   curSum=0

   
   for ip in vmSysInfoHistory:
      curListLen=len(vmSysInfoHistory[ip])

      # no SysInfo record, then assign avgRecentQlen=0
      if curListLen==0:
         recentSysInfo[ip]=0.00

      # SysInfo record is less than window size
      elif curListLen<recentSysInfoNum:
         for i in vmSysInfoHistory[ip]:
            curSum=curSum+float(i)
         recentSysInfo[ip]=curSum / float(curListLen)
         curSum=0
      else:
         for i in range(curListLen-1, curListLen-1-recentSysInfoNum,-1):
            curSum=curSum+float(vmSysInfoHistory[ip][i]) 
         recentSysInfo[ip]=curSum / float(recentSysInfoNum)
         curSum=0

   #####################################
   # Probe1-microbenchmark from VM     #
   # Probe2-vmPerfRecordedByClient     #
   #####################################
   global vmProbe1Time
   global vmProbe1TimeHistory
   global vmProbe2Time
   global vmProbe2TimeHistory


   ###############
   # Sort        #
   ###############
   recentQlenSysInfoProbeTime=dict()

   for i in recentQlen:
      if modeID==2: #Qlen
         recentQlenSysInfoProbeTime[i]=recentQlen[i]

      if modeID==3: #CPU
         recentQlenSysInfoProbeTime[i]=recentSysInfo[i]  
       
      if modeID==4: #Probe1, microbenchmark
         recentQlenSysInfoProbeTime[i]=vmProbe1Time[i]

      if modeID==5: #probe2, serv rate monitor, probe2 is avgJobServTime
         #Probe2: vmIP, [0.firstJobSendTime, 1.lastJobRecvTime, 2.totalJobCount(Size), 3.totalJobNumber, 4.totalRespTime, 5.respTimePerJobCount, 6.mkspPerJobCount]  
         #recentQlenSysInfoProbeTime[i]=vmPerfRecordedByClient[i][5] #all perf

         print 'vmProbe2Time[',i,']',vmProbe2Time[i]
         print 'vmProbe2Time',vmProbe2Time
         print 'vmProbe2TimeHistory',vmProbe2TimeHistory

         if vmProbe2Time[i]!=0: # if received probe2 value of the ith vm
            #recentQlenSysInfoProbeTime[i]=float(vmProbe2Time[i]) #20150112, probe2 is avgServTime
            recentQlenSysInfoProbeTime[i]=(recentQlen[i]+int(jobCount))*float(vmProbe2Time[i]) #20150116
         else:
            print '### VM[',i,'] has receive any probe2 feedbacks, set its expFinTime to infinite'
            recentQlenSysInfoProbeTime[i]=float("inf")
            #recentQlenSysInfoProbeTime[i]=recentQlen[i] # initializing with qlen

         print 'recentQlenSysInfoProbeTime=',recentQlenSysInfoProbeTime


      if modeID==6:#Qlen+Probe1
         recentQlenSysInfoProbeTime[i]=(recentQlen[i]+int(jobCount))*vmProbe1Time[i]
      

      #recentQlenSysInfoProbeTime[i]=(recentQlen[i]+int(jobCount))*vmProbe1Time[i]*recentSysInfo[i]*vmPerfRecordedByClient[i][3]
      # (q(t)+size(j(i)))/u(t)
      # u(t)=1/(probeTime*CPU%*avgRespTimeOfJobUnit)
   
  

   # list sortedRecentQlenSysInfoProbeTime, item is tuple, e.g., "[(ip1,0),(ip2,1),(ip3,0)]":
   #sortedRecentQlenSysInfoProbeTime = sorted( recentQlenSysInfoProbeTime.iteritems(), key=operator.itemgetter(1)   )
   #print sortedRecentQlenSysInfoProbeTime
   #return sortedRecentQlenSysInfoProbeTime[random.randint(0,k-1)][0]  


   sortedRecentQlenSysInfoProbeTime = sorted( recentQlenSysInfoProbeTime.iteritems(), key=operator.itemgetter(1)   )
   numOfSameSmallestItem=0
   for item in sortedRecentQlenSysInfoProbeTime:
      if item[1] == sortedRecentQlenSysInfoProbeTime[0][1]:
         numOfSameSmallestItem=numOfSameSmallestItem+1
      else:
         break
   if k>=numOfSameSmallestItem:
      return sortedRecentQlenSysInfoProbeTime[random.randint(0,k-1)][0]
   else:
      return sortedRecentQlenSysInfoProbeTime[random.randint(0,numOfSameSmallestItem-1)][0] 




def getAverageJobResponseTime():
   global jobResponseTime
   curSum=0
   listLen=len(jobResponseTime)
   for jobID in jobResponseTime:
      if jobResponseTime[jobID][2]==0:
         listLen=listLen-1
      else:
         curSum=curSum+jobResponseTime[jobID][2]
   return curSum/float(listLen)

def getVMAverageSysInfo():
   global vmSysInfoHistory
   global vmAverageSysInfo
   for ip in vmSysInfoHistory:
      start=findStart(vmSysInfoHistory[ip])
      end=findEnd(vmSysInfoHistory[ip])
      sum=sumRange(vmSysInfoHistory[ip],start,end)
      vmAverageSysInfo[ip]=sum/float(end-start+1)



def findStart(x):
   for i in range(len(x)):
      if x[i]==0:
         i+=1
         continue
      else:
         break
   return i

def findEnd(x):
   for i in range(len(x)-1,0,-1):
      if x[i]==0:
         continue
      else:
         break
   return i

def sumRange(x, s, e):
   sum=0
   for i in range(s,e+1,1):
      sum+=x[i]
   return sum

def getVMAverageQlen():
   global vmQlenHistory
   global vmAverageQlen
   curSum=0
   for ip in vmQlenHistory:
      curSum=0
      for k in vmQlenHistory[ip]:
         curSum=curSum+float(k)
      vmAverageQlen[ip]=curSum/float(len(vmQlenHistory[ip]))
     

#20141113
def getAvg(inputDict):
   curSum=0
   for key in inputDict:
      curSum+=float(inputDict[key])
   return curSum/float(len(inputDict))


if __name__=='__main__':
   main()
