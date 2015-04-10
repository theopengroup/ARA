import sys, os
import linecache
import operator


if (len(sys.argv)!=3):
   print "python mergeTrace.py [arrivalTimeFile] [jobSizeCountFile]"
   exit(0)
list1=[]

for line in open(sys.argv[1]):
   list1.append(line.strip().split('\t')[1])


outfileName=str('Trace-'+sys.argv[1]+"-"+sys.argv[2]+'.trace')
outfile = file(outfileName, 'w',0)


i=0
for line in open(sys.argv[2]):
   outfile.write(str(list1[i]+','+line.strip().split(',')[1]+','+line.strip().split(',')[2]+'\n'))
   i+=1
