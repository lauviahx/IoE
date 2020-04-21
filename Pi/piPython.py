import numpy as np
import alsaaudio as aa
import wave
from struct import unpack
import time
import sys
import random
import pygame.midi
import audioop
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image
spectrum  = [1,1,1,3,3,3,2,2]
matrix    = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
power     = []
weighting = [32,32,32,32,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64]
checker = 0;
loops = [0,0,0,0,0]
for i in range(4):
    string = '/home/pi/Public/project/frizzybeatz/f{}.wav'.format(i)
    loops[i] = wave.open(string,'r')
print(loops)
wavfile = wave.open('/home/pi/Public/project/frizzybeatz/f0.wav','r')
sample_rate = wavfile.getframerate()
no_channels = wavfile.getnchannels()
chunk       = 1024 # Use a multiple of 8
output = aa.PCM(aa.PCM_PLAYBACK, aa.PCM_NORMAL)
output.setchannels(no_channels)
output.setrate(sample_rate)
output.setformat(aa.PCM_FORMAT_S16_LE)
output.setperiodsize(chunk)
options = RGBMatrixOptions()
options.rows = 32
options.chain_length = 3
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'
matrixL = RGBMatrix(options = options)
black = graphics.Color(0,0,0)
green = graphics.Color(0,0,0)
increment = 0
plusminus = 0
def bars(matrix):
    for i in range(24):
        colorChanger(matrix[0])
        for a in range(4):
            graphics.DrawLine(matrixL,(0+a)+4*i,32,(0+a)+4*i,0,black)
            graphics.DrawLine(matrixL,(0+a)+4*i,32,(0+a)+4*i,32-matrix[i],green)
def colorChanger(beat):
    global plusminus
    global green
    global increment
    if increment==255:
        plusminus = 1
    elif increment==0:
        plusminus = 0
    if plusminus == 0:
        increment += 1
        green = graphics.Color(increment/2,increment/2,increment/2)
    else:
        increment -= 1
        green = graphics.Color(increment/2,50,255)
    if beat > 25:
        green = graphics.Color(255,0,0)
def piff(val):
   return int(2*chunk*val/sample_rate)
def calculate_levels(data, chunk,sample_rate):
       global matrix
       # Convert raw data (ASCII string) to numpy array
       data = unpack("%dh"%(len(data)/2),data)
       data = np.array(data, dtype='h')
       # Apply FFT - real data
       fourier=np.fft.rfft(data)
       # Remove last element in array to make it the same size as chunk
       fourier=np.delete(fourier,len(fourier)-1)
       # Find average 'amplitude' for specific frequency ranges in Hz
       power = np.abs(fourier)
       for x in range(24):
           spec = 120*x*2
           matrix[x]= int(np.mean(power[piff(spec)    :piff((spec*2)+120):1]))
       # Tidy up column values for the LED matrix0
       matrix=np.divide(np.multiply(matrix,weighting),1000000)
       # Set floor at 0 and ceiling at 8 for LED matrix
       matrix=matrix.clip(0,30)
       bars(matrix)
       return matrix
def readInput(input_device):
    if input_device.poll():
        event = input_device.read(1)
        data = loops[0].readframes(chunk)
        print (data)
data = loops[0].readframes(chunk)
# Loop while audio data present
pygame.midi.init()
#my_input = pygame.midi.Input(3) #only in my case the id is 2
while data!=b'':
    data = audioop.add(loops[0].readframes(chunk),loops[1].readframes(chunk),2)
    data = audioop.add(data,loops[3].readframes(chunk),2)
    matrix=calculate_levels(data, chunk,sample_rate)
    #if __name__ == '__main__':
        #readInput(my_input)
    output.write(data)