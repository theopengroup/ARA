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






def main():
   traceFile=open(sys.argv[1],"r")
   burstDetector=burstDetection() 
   
   
   for line in open(sys.argv[1]): 
      curTime=float(line.strip().split(',')[0])
      if burstDetector.Check_BurstState(curTime)==1:  
         curK=1
      else:
         curK=0
      print curK


if __name__=='__main__':
   main()
