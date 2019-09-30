import numpy as np  
import wave  
from denoise import denoise
from matplotlib import pyplot as plt  

def top_five_freq(file_path):

	denoise(file_path)

	file_path='denoise_file.wav'  
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

	df=framerate/(nframes-1)  
	freq=[df*n for n in range(0,nframes)]  
	transformed=np.fft.fft(wave_data[0])  
	d=int(len(transformed)/2)  
	while (freq[d]>4000 or freq[d]<250):  
	    d-=10  
	freq=freq[:d]  
	transformed=transformed[:d]  
	for i,data in enumerate(transformed):  
	    transformed[i]=abs(data)   

	local_partmax=[]
	local_max=[]

	for i in range(1, len(transformed), 700):
		for j in range(i, i+700):
			if j >= len(transformed) - 1:
				continue
			if transformed[j]>transformed[j-1] and transformed[j]>transformed[j+1]:
				local_partmax.append(transformed[j])
		local_partmax=sorted(local_partmax)  
		local_max.append(local_partmax[-1])
		local_partmax=[]
	local_max=sorted(local_max)

	max_freq_array=[]
	for i in range(1, 5):
		loc1=np.where(transformed==local_max[-i])  
		if freq[loc1[0][0]] > 750 and freq[loc1[0][0]] < 2000:
			max_freq_array.append(freq[loc1[0][0]])

	return max_freq_array  


def main():
	x=[]
	note_freq=[]
	note_average_ferq=[]
	for i in range(1, 10):
		for j in range(1, 9):
			path = '../calculator_file/calculator_' + str(i) + '_' + str(j) + '.wav'
			freq_array = top_five_freq(path)
			freq_array = np.array(freq_array, dtype = np.int32)
			note_freq.append(freq_array[0])
		x.append(i)
		note_average_ferq.append(sum(note_freq) / len(note_freq))
		plt.text(i-0.3, note_average_ferq[i-1], note_average_ferq[i-1])
		note_freq=[]
	np.save('note_average_ferq', note_average_ferq)
	plt.scatter(x,note_average_ferq,marker='*')  
	plt.show() 
  
if __name__=='__main__':  
    main()