import numpy as np
import wave  
import matplotlib.pyplot as plt
import pyaudio

NOTE_MIN = 0       # C4
NOTE_MAX = 200       # A4
FSAMP = 22050       # Sampling frequency in Hz
FRAME_SIZE = 2048   # How many samples per frame?
FRAMES_PER_FFT = 16 # FFT takes average across how many frames?
INPUT_DEVICE = 0
SAMPLES_PER_FFT = FRAME_SIZE*FRAMES_PER_FFT
FREQ_STEP = float(FSAMP)/SAMPLES_PER_FFT

def top_freq(file_path): 
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
	fft = np.fft.fft(wave_data[0])
	df=framerate/(nframes-1)  
	freq=[df*n for n in range(0,nframes)]  
	transformed=np.fft.fft(wave_data[0])  
	d=int(len(transformed)/2)  
	while (freq[d]>4000 or freq[d]<250):  
	    d-=10  
	freq=freq[300:2000]  
	transformed=transformed[300:2000]  
	for i,data in enumerate(transformed):  
	    transformed[i]=abs(data) 

	local_partmax=[]
	for i in range(len(transformed) - 1):
		if transformed[i]>transformed[i-1] and transformed[i]>transformed[i+1]:
			local_partmax.append(transformed[i])
	local_partmax=sorted(local_partmax, reverse=True)  
	loc1=np.where(transformed==local_partmax[0])  

	plt.figure()
	plt.plot(transformed)
	print(freq[loc1[0][0]])
	return freq[loc1[0][0]]

def main():
	average=[]
	for i in range(1, 6):
		average.append(top_freq('../calculator_file/calculator_14_' + str(i) + '.wav'))
	print("===")
	print(sum(average) / len(average))
	#plt.show()


if __name__ == '__main__':
	main()