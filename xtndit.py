#!/usr/bin/python
import argparse
import subprocess
import time
import numpy as np

L2POWFUNC=None

def get_diff(battery_energy, processor_energy):
	return battery_energy - processor_energy

def get_L2_pow_func(battery_energy, processor_energy, L2_refs):
	global L2POWFUNC
	y = np.array(map(get_diff, battery_energy, processor_energy))
	x = np.array(L2_refs)
	z = np.polyfit(x, y, 1)
	L2POWFUNC=str(z[0])+"*x+"+str(z[1])
	return

def listtomap(datalist):
	datamap = dict()
	for item in datalist:
		mapitem = item.split(':')
		#print len(mapitem)
		if len(mapitem) == 2:
			datamap[mapitem[0].strip()] = mapitem[1].strip()
	return datamap

#returns battery energy in joules*10^-6
def get_battery_energy(data):
	battery_data = data.split()
	return (float(battery_data[0]) - float(battery_data[1]))*float(battery_data[2])*0.36/100

def calibrate(time, pid, samples=5):
	counter = 0
	battery_energy = []
	L2_refs = []
	processor_energy = []
	while counter < int(samples):
		data = subprocess.check_output(["./collect_data.sh",str(time), str(pid)])
		data = data.split('\n')
		datamap = listtomap(data)
		#print datamap
		battery_energy.append(get_battery_energy(datamap['Battery']))
		processor_energy.append(float(datamap['CPU']))
		L2_refs.append(float(datamap['L2TOTAL']))
		counter = counter + 1

	get_L2_pow_func(battery_energy, processor_energy, L2_refs)

def estimate(time, pid):
	run_data=subprocess.check_output(["./collect_data.sh", str(time), str(pid)]);
	data = run_data.split('\n')
	datamap = listtomap(data)
	l2pid = datamap['L2PID'] 
	pidbattery = eval(L2POWFUNC, globals(), dict({'x':float(l2pid)}))
	(pidfreq,totalfreq) = datamap['FREQ'].split()
	pidbattery = pidbattery + float(datamap['CPU'])*float(pidfreq)/float(totalfreq)
	print "Predicted Battery time (minutes):"
	totalrate = float(datamap['Battery'].split()[1])*float(time)/(float(datamap['Battery'].split()[0])-float(datamap['Battery'].split()[1]))/60
	print totalrate
	print "Time increases in minutes if the application is closed"
	print totalrate*pidbattery/get_battery_energy(datamap['Battery'])
	#print datamap
	
	

def main():
	parser = argparse.ArgumentParser(description='Extend your battery life')
	parser.add_argument('-e', '--estimate', action='store', help='Number of seconds to be spent on actually collecting pid specific data')
	parser.add_argument('-s', '--samples', action='store', help='Number of samples to be taken to calibrate.')
	parser.add_argument('-w', '--wait', action='store', help='Number of seconds to wait for warming up the application')
	parser.add_argument('-p', '--pid', action='store', help="pid of the process to be analzed")
        args = parser.parse_args()
	if args.wait is not None:
		time.sleep(float(args.wait))
	calibrate(5,args.pid, args.samples)
	estimate(args.estimate, args.pid)
	return 0


if __name__ == '__main__':
	main()
