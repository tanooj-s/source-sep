import numpy as np
import librosa.core as lc
import librosa.effects as le
import librosa.display as ld
from scipy import fftpack
import matplotlib.pyplot as plt
import datetime
import base64

def get_fft(samples,rate):
	nyquist = int(rate/2)
	yfft = fftpack.fft(x=samples,n=rate)
	max_amp = np.max(np.abs(yfft))
	xfft = np.linspace(0,nyquist,nyquist)
	yfft = np.abs(yfft[:nyquist])/(max_amp) 
	return {'x': xfft.tolist(), 'y': yfft.tolist()}


def split_hp(samples):
	harmonic_samples, percussive_samples = le.hpss(samples)
	return harmonic_samples, percussive_samples


def generate_waveplot(samples,rate):
	plt.figure(figsize=(10,5))
	plt.title('Waveplot')
	plt.xlabel('Time (s)')
	plt.ylabel('Amplitude')
	plt.plot(np.arange(len(samples))/rate, samples)
	filename = "waveplot_" + str(datetime.datetime.now().timestamp()) + ".png"
	plt.savefig(filename)
	with open(filename, 'rb') as f:
		encoding = base64.b64encode(f.read()).decode('utf-8') # might need to add MIME-type prefix to encoding 
	return encoding

def generate_fft_plot(fft_x, fft_y): # only takes in results of get_fft
	plt.figure(figsize=(10,5))
	plt.xlim(20,20000)
	plt.title('Spectrum')
	plt.xlabel('Hz')
	plt.ylabel('Relative Amplitude')
	plt.semilogx(fft_x,fft_y)
	filename = "fftplot_" + str(datetime.datetime.now().timestamp()) + ".png"
	plt.savefig(filename)
	with open(filename, 'rb') as f:
		encoding = base64.b64encode(f.read()).decode('utf-8')
	return encoding


def generate_spectrogram(samples,rate,opt):
	plt.figure(figsize=(10,5))
	if opt == 0:
		plt.title('Spectrogram')
	elif opt == 1:
		plt.title('Harmonic Components Spectrogram')
	elif opt == 2:
		plt.title('Percussive Components Spectrogram')
	ld.specshow(lc.amplitude_to_db(np.abs(lc.stft(samples)),ref=np.max), y_axis='log', x_axis='time')
	filename = "specplot_" + str(datetime.datetime.now().timestamp()) + ".png"
	plt.savefig(filename)
	with open(filename, 'rb') as f:
		encoding = base64.b64encode(f.read()).decode('utf-8')
	return encoding





