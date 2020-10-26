#!/usr/bin/python3
#Program that takes in a complex binary file (fc32)
#and calculates the received power and outputs a plot
#of average received power
#comment

import numpy as np
import scipy
import os
import matplotlib.pyplot as plt
import math
from decimal import *
import argparse


#Takes in binary file and returns binary data array
def readBin(file_path):
	return np.fromfile(file_path, dtype=np.complex64)

#Takes in binary I/Q data and returns array of linear power values
def binToLinearPower(bin_data):
	return np.abs(bin_data)**2

#Takes in power measurements and computes averages in non-overlapping windows of size N.
def windowedAvg(power_data, N):
	truncate = len(power_data) % N
	mv_avg_power = []
	count = 0
	power = 0
	for i in range(len(power_data) - truncate):
		if count < N:
			power += power_data[i]
			count += 1
		else:
			mv_avg_power.append(power/float(N))
			count = 0
			power = 0
	return mv_avg_power

#Takes in linear power measurements and returns decibel measurements. If power is 0, return NaN
def linearPowerToDecibel(lin_power):
	db_power = []
	for i in range(0,len(lin_power)):
		db_power.append(Decimal("10")*Decimal(lin_power[i]).log10() if lin_power[i] != 0 else Decimal('NaN'))
	return db_power

def toCSV(array,filename):
	np.savetxt(filename,[array], delimiter=',')

def main():
	#get user input
	parser = argparse.ArgumentParser(description='Binary I/Q data file to csv of decibel powers')
	parser.add_argument('-p', '--path', type=str,
	                   help='Directory path to i/q data file')
	parser.add_argument('-w', '--window_size', type=int, default = 20000, required = False,
	                   help='Size of averaging window, default: 20000')
	parser.add_argument('-n', '--name', type=str,  default = 'db_power',
	                   help='Name your CSV file, default: db_power')
	args = parser.parse_args()
	#Decimal precision
	getcontext().prec = 10

	#initialize variables
	file_path = args.path
	N = args.window_size
	file_name = args.name

	#do work
	bin_file = readBin(file_path)
	power = binToLinearPower(bin_file)
	avg_power = windowedAvg(power,N)
	avg_decibel_power = linearPowerToDecibel(avg_power)
	#save to CSV
	toCSV(avg_decibel_power,file_name+".csv")

if __name__ == "__main__":
	main()

#plot of received power
#plt.plot(db_power)
#plt.show()
