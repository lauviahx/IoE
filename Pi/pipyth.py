import numpy as np
import alsaaudio as aa
import wave
from struct import unpack
import pygame.midi
import audioop
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import glob
from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse

#creating global variables
spectrum  = [1,1,1,3,3,3,2,2]
matrix    = [0]*16
power     = []
weighting = [8,32,32,32]+[64]*12
checker = 0;
loops = [0]*37
#Reading all sound files in a folder
string = glob.glob('/home/pi/Public/project/sounds/5/*.wav')
for i in range(37):
    path = string[i]
    loops[i] = wave.open(path,'r')

    
#Getting sample rate, number of channels and amount of chunks (picking first file, because all of the files have the same attributes
sample_rate = loops[0].getframerate()
no_channels = loops[0].getnchannels()
chunk       = 1024 # Use a multiple of 8

#Setting up audio output (number of channels, sound card, sample rate etc...)
output = aa.PCM(aa.PCM_PLAYBACK, aa.PCM_NORMAL)
output.setchannels(no_channels)
output.setrate(sample_rate)
output.setformat(aa.PCM_FORMAT_S16_LE)
output.setperiodsize(chunk)

#setting up RGB metrices
options = RGBMatrixOptions()
options.rows = 32
options.chain_length = 3
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'
matrixL = RGBMatrix(options = options)
black = graphics.Color(0,0,0)
green = graphics.Color(0,0,0)


playing = [0]*37
vals = [0]
nOfK = 0

plusminus = 0
increment = 0
#this function lights up metrices. First "for" goes 16 times for each bar and 6 times for each column in a bar
def bars(matrix):
    if nOfK !=0:
        for i in range(16):
            colorChanger(matrix[0])
            for a in range(6):
                graphics.DrawLine(matrixL,(0+a)+6*i,32,(0+a)+6*i,0,black)
                graphics.DrawLine(matrixL,(0+a)+6*i,32,(0+a)+6*i,32-matrix[i],green)
    else:
        for i in range(96):
                graphics.DrawLine(matrixL,0+i,32,0+i,0,black)
#Changing colour when lowest bar hits certain aplitude level
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
        green = graphics.Color(6,0,255)
    else:
        increment -= 1
        green = graphics.Color(194,54,255)
    if beat > 25:
        green = graphics.Color(117,250,239)
def piff(val):
   return int(2*chunk*val/sample_rate)

#This function does all the "hard calculations". Converts bytes of sound chunks to numbers and then does FFT. Result is sent to the metrices and to the client side
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
       matrix[0]= int(np.mean(power[piff(0)    :piff(50):1]))
       matrix[1]= int(np.mean(power[piff(50)  :piff(100):1]))
       matrix[2]= int(np.mean(power[piff(100)  :piff(150):1]))
       matrix[3]= int(np.mean(power[piff(150)  :piff(250):1]))
       matrix[4]= int(np.mean(power[piff(250) :piff(500):1]))
       matrix[5]= int(np.mean(power[piff(500) :piff(800):1]))
       matrix[6]= int(np.mean(power[piff(800) :piff(1500):1]))
       matrix[7]= int(np.mean(power[piff(1500):piff(2200):1]))
       matrix[8]= int(np.mean(power[piff(4000):piff(5000):1]))
       matrix[9]= int(np.mean(power[piff(5000):piff(6000):1]))
       matrix[10]= int(np.mean(power[piff(6000):piff(8000):1]))
       matrix[11]= int(np.mean(power[piff(8000):piff(10000):1]))
       matrix[12]= int(np.mean(power[piff(10000):piff(12000):1]))
       matrix[13]= int(np.mean(power[piff(12000):piff(14000):1]))
       matrix[14]= int(np.mean(power[piff(14000):piff(16000):1]))
       matrix[15]= int(np.mean(power[piff(16000):piff(20000):1]))

       # Tidy up column values for the LED matrix0

       matrix=np.divide(np.multiply(matrix,weighting),1000000)
       # Set floor at 0 and ceiling at 8 for LED matrix
       matrix=matrix.clip(0,30)
       send(matrix)
       bars(matrix)
       return matrix

    #This function adds together chunks of audio and sends it to the output. Looks complicated only because to be able to add two chunks together, they need to be the same lenght. Most of this code is error handling and checking which chunk is shorter and if it is, reset the sound file to the beginning 
def soundTrigger():
    if nOfK == 1:
        data = loops[vals[0]].readframes(chunk)
        if data == b'':
            loops[vals[0]].rewind()
            data = loops[vals[0]].readframes(chunk)
        output.write(data)
    elif nOfK == 2:
        data1 = [loops[vals[0]].readframes(chunk),loops[vals[1]].readframes(chunk)]
        while True:
            try:
                data = audioop.add(data1[0],data1[1],2)
                break
            except audioop.error:
                if len(data1[0])<len(data1[1]):
                    loops[vals[0]].rewind()
                    data1[0] = loops[vals[0]].readframes(chunk)
                    data = audioop.add(data1[0],data1[1],2)
                elif len(data1[1])<len(data1[0]):
                    loops[vals[1]].rewind()
                    data1[1] = loops[vals[1]].readframes(chunk)
                    data = audioop.add(data1[0],data1[1],2)
                break

        output.write(data)
    elif nOfK == 3:
        data1 = [loops[vals[0]].readframes(chunk),loops[vals[1]].readframes(chunk),loops[vals[2]].readframes(chunk)]
        while True:
            try:
                data = audioop.add(data1[0],data1[1],2)
                data = audioop.add(data,data1[2],2)
                break
            except audioop.error:
                if len(data1[0])<len(data1[1]):
                    loops[vals[0]].rewind()
                    data1[0] = loops[vals[0]].readframes(chunk)
                    data = audioop.add(data1[0],data1[1],2)

                elif len(data1[1])<len(data1[0]):
                    loops[vals[1]].rewind()
                    data1[1] = loops[vals[1]].readframes(chunk)
                    data = audioop.add(data1[0],data1[1],2)
                try:
                    data = audioop.add(data,data1[2],2)
                except audioop.error:
                    loops[vals[2]].rewind()
                    data1[2] = loops[vals[2]].readframes(chunk)
                    data = audioop.add(data,data1[2],2)
                break
        output.write(data)
    elif nOfK == 4:
        data1 = [loops[vals[0]].readframes(chunk),loops[vals[1]].readframes(chunk),loops[vals[2]].readframes(chunk),loops[vals[3]].readframes(chunk)]
        while True:
            try:
                data = audioop.add(data1[0],data1[1],2)
                data = audioop.add(data,data1[2],2)
                data = audioop.add(data,data1[3],2)
                break
            except audioop.error:
                if len(data1[0])<len(data1[1]):
                    loops[vals[0]].rewind()
                    data1[0] = loops[vals[0]].readframes(chunk)
                    data = audioop.add(data1[0],data1[1],2)

                elif len(data1[1])<len(data1[0]):
                    loops[vals[1]].rewind()
                    data1[1] = loops[vals[1]].readframes(chunk)
                    data = audioop.add(data1[0],data1[1],2)
                try:
                    data = audioop.add(data,data1[2],2)
                except audioop.error:
                    loops[vals[2]].rewind()
                    data1[2] = loops[vals[2]].readframes(chunk)
                    try:
                        data = audioop.add(data,data1[3],2)
                    except audioop.error:
                        loops[vals[3]].rewind()
                        data1[3] = loops[vals[3]].readframes(chunk)
                        data = audioop.add(data,data1[3],2)
                break
        output.write(data)
    return data


#Reading input from midi keyboard and sorting out the signal
def readInput(input_device):
    if input_device.poll():
        event = input_device.read(1)
        onOff = event[0][0][0]
        key = event[0][0][1]
        if onOff is 144:
            global nOfK
            playing[key-48] = 1
            nOfK+=1
            vals.append(key-48)
            vals.sort(reverse=True)
        if onOff is 128:
            loops[key-48].rewind()
            playing[key-48] = 0
            vals.remove(key-48)
            vals.sort(reverse=True)
            nOfK-=1
#This function sends analysed data from our sounds to the client side using OSC
def send(value):
    value =value.tolist()
    #value.insert(0,"bars")
    msg = oscbuildparse.OSCMessage("/test/me", None, value)
    osc_send(msg, "aclientname")
    osc_process()
data = loops[0].readframes(chunk)
# Loop while audio data present
pygame.midi.init()
osc_startup()

# Make client channels to send packets.
osc_udp_client("192.168.0.7", 7500, "aclientname")

my_input = pygame.midi.Input(3)
while True:
    if __name__ == '__main__':
        readInput(my_input) #read input from keyboard
    if nOfK >0 and nOfK <=4: #if user holds 1-4 keys, play sounds and analyse them
        mData = soundTrigger()
        matrix=calculate_levels(mData, chunk,sample_rate)
    else: bars(matrix) #if not, reset the metrix to default
