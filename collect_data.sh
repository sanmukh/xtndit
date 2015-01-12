#!/bin/bash

set -m

TIME=$1
PID=$2

rate_discharge()
{
LTIME=$1

START=`cat /proc/acpi/battery/BAT0/state | grep "remaining capacity" | awk '{print $3}'`
sleep $LTIME
END=`cat /proc/acpi/battery/BAT0/state | grep "remaining capacity" | awk '{print $3}'`
#assuming voltage is constant and is equal to the value of the end of data collection
VOLTAGE=`cat /proc/acpi/battery/BAT0/state | grep "present voltage" | awk '{print $3}'`

echo "Battery:" $START $END $VOLTAGE
}


cpu_power()
{
LTIME=$1
POWER=`sudo ./power_gadget/power_gadget -e 1000 -d $LTIME | grep "Total Processor" | grep Joule | awk '{print $3}' | sed s/[a-zA-Z\_\(0\)=]//g`

echo "CPU:" $POWER
}


cpu_freq()
{
LTIME=$1
LPID=$2
#Look at linux filesys documentation for format of stat files
START_TOTAL=`cat /proc/stat | grep cpu\ | awk '{print $2+$3+$4}'`
START_PROC=`cat /proc/$LPID/stat | awk '{print $14+$15+$16+$17}'`
sleep $LTIME
END_TOTAL=`cat /proc/stat | grep cpu\ | awk '{print $2+$3+$4}'`
END_PROC=`cat /proc/$LPID/stat | awk '{print $14+$15+$16+$17}'`

TOTAL=$(($END_TOTAL-$START_TOTAL))
PROC=$(($END_PROC-$START_PROC))

echo "FREQ:" $PROC $TOTAL
}


L2_hits()
{
LTIME=$1
LPID=$2
perf stat -e LLC-loads,LLC-stores -p $LPID 2> perf.tmp &
PERFID=$!
sleep $LTIME
kill -INT $PERFID
L2HITS=`cat perf.tmp | grep LLC | sed s/,//g | awk 'BEGIN{temp=0}{temp=temp+$1;}END{print temp}'`
echo "L2PID:" $L2HITS
}

L2_hits_total()
{
LTIME=$1
perf stat -e LLC-loads,LLC-stores -a 2> perft.tmp &
PERFID=$!
sleep $LTIME
kill -INT $PERFID
L2HITS=`cat perft.tmp | grep LLC | sed s/,//g | awk 'BEGIN{temp=0}{temp=temp+$1;}END{print temp}'`
echo "L2TOTAL:" $L2HITS
}

rate_discharge $TIME &
cpu_power $TIME &
cpu_freq $TIME $PID &
L2_hits $TIME $PID &
L2_hits_total $TIME &

while [ 1 ]; do fg &> /dev/null; [ $? == 1 ] && break; done

