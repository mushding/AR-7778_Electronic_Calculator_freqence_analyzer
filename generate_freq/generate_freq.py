import numpy as np  
import wave  
from denoise import denoise
from matplotlib import pyplot as plt  

denoise()

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
plt.subplot(211)  
plt.plot(time,wave_data[0],'r-')  
plt.xlabel('Time/s')  
plt.ylabel('Ampltitude')  
plt.title('Num '+num+' time/ampltitude')  

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
plt.subplot(212)  
plt.plot(freq,transformed,'b-')  
plt.xlabel('Freq/Hz')  
plt.ylabel('Ampltitude')  
plt.title('Num '+num+' freq/ampltitude')  

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

for i in range(1, 6):
	loc1=np.where(transformed==local_max[-i])  
	max_freq=freq[loc1[0][0]]  
	print (int(max_freq))

plt.show()