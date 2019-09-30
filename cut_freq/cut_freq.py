import numpy as np  
import wave  
from matplotlib import pyplot as plt

def transforme(wave_data, framerate):
	df=framerate/(20000-1)  
	freq=[df*n for n in range(0,20000)]  
	transformed=np.fft.fft(wave_data)  
	d=int(len(transformed)/2)  
	while (freq[d]>4000 or freq[d]<250):  
	    d-=10  
	freq=freq[:d]  
	transformed=transformed[:d]  
	for i,data in enumerate(transformed):  
	    transformed[i]=abs(data) 
	transformed = transformed[300:] 
	freq=freq[300:]   
	return transformed, freq

def greb_750_2000_freq(transformed, freq):
	local_partmax=[]
	max_freq_array=[]
	index = 0

	for i in range(len(transformed) - 1):
		if transformed[i]>transformed[i-1] and transformed[i]>transformed[i+1]:
			local_partmax.append(transformed[i])
	local_partmax=sorted(local_partmax, reverse=True)
	local_partmax=local_partmax[:20]

	for i in range(len(local_partmax)):
		loc1=np.where(transformed==local_partmax[i])  
		#print(freq[loc1[0][0]])
		if freq[loc1[0][0]] > 750 and freq[loc1[0][0]] < 2000:
			max_freq_array.append(freq[loc1[0][0]])
	#print("===")
	return max_freq_array

def match_freq(sample_array):
	distance=[]
	index_min=[]
	average_freq = np.load('note_average_ferq.npy')
	for sample_index in range(len(sample_array)):
		for average_index in range(len(average_freq)):
			distance.append(abs(sample_array[sample_index] - average_freq[average_index]))
		index_min.append(np.argmin(distance) + 1)
		distance=[]
	return index_min

def cut_freq(file_path): 
	f=wave.open(file_path,'rb')  
	num=file_path[-5]   
	params=f.getparams()  
	nchannels,samplewidth,framerate,nframes=params[:4]  
	str_data=f.readframes(nframes)  
	f.close()  
	wave_data=np.fromstring(str_data,dtype=np.short)  
	wave_data.shape=-1,1  
	if nchannels==2:  
	    wave_data.shape=-1,2  
	else:  
	    pass  
	wave_data=wave_data.T  
	time=np.arange(0,nframes)*(1.0/framerate)  
	part_wave=[]
	feature_freq=[]
	index = 0
	for i in range(len(wave_data[0])):
		if i < index:
			pass
		elif wave_data[0][i] > 10000:
			for j in range(i-2000, i+18000):
				part_wave.append(wave_data[0][j])
			transformed_wave, freq = transforme(part_wave, framerate)
			# print wave figure
			# plt.figure()
			# plt.plot(freq, transformed_wave)
			# plt.show()
			# print(len(transformed_wave))
			transformed_wave = greb_750_2000_freq(transformed_wave, freq)
			transformed_wave = np.array(transformed_wave, dtype = np.int32)
			feature_freq.append(transformed_wave[0])
			index = i+18000
		part_wave=[]

	index_min = match_freq(feature_freq)
	return index_min

def main():
	file_path = '../calculator_file/calculator_1155678_1.wav'
	print(cut_freq(file_path))
	plt.show()

if __name__ == '__main__':
	main()