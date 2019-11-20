from flask import Flask, render_template, request, url_for, redirect, jsonify
from werkzeug import secure_filename
from werkzeug.exceptions import BadRequest
import librosa.core as lc
import numpy as np
import os
import json
import base64
import time
import librosa.core as lc
import librosa.display as ld
import librosa.effects as le
from librosa.output import write_wav
from util import get_fft, generate_waveplot, generate_fft_plot, split_hp, generate_spectrogram

app = Flask(__name__, static_folder="../static/dist", template_folder="../static")
app.config['UPLOAD_FOLDER'] = "../uploads"


@app.route("/", methods = ['GET','POST'])
def index():

	if request.method == 'POST':
		curr_time = str(int(time.time()))
		data = request.get_json()
		lowerbound = data['lowerbound']
		upperbound = data['upperbound']
		fft_on = data['fft_on']
		audiofile = data['uploaded_audiofile']
		prefix = "data:audio/wav;base64," # handle other audio file formats
		audiofile = audiofile.replace(prefix,"")
		original_filename = "upload_" + curr_time + ".wav" 

		try:
			audiofile = base64.b64decode(audiofile)
			with open(original_filename,"wb") as f:
				f.write(audiofile)
		except Exception as e:
			return(str(e))

		samples, rate = lc.load(original_filename) # can you get these directly from the base64 encoding sent it without saving it 
		samples, _ = le.trim(samples[int(rate*lowerbound):int(rate*upperbound)], top_db=20)
		harmonic_samples, percussive_samples = split_hp(samples) 

		response = dict()


		response['original_file'] = original_filename
		response['harmonic_file'] = write_wav(path="h_" + curr_time + ".wav", y=harmonic_samples, sr=rate)
		response['percussive_file'] = write_wav(path="p_" + curr_time + ".wav", y=percussive_samples, sr=rate)
		



		# get full working directory for these
		response['original_samples'] = [str(s) for s in samples]      
		response['harmonic_samples'] = [str(s) for s in harmonic_samples]
		response['percussive_samples'] = [str(s) for s in percussive_samples]



		waveplot_encoding = "data:image/png;base64," + str(generate_waveplot(samples, rate)) # this should return an image of the matplotlib plot
		response['waveplot'] = waveplot_encoding

		spectrogram_encoding = "data:image/png;base64," + str(generate_spectrogram(samples, rate, opt=0))
		response['spectrogram'] = spectrogram_encoding

		h_spectrogram_encoding = "data:image/png;base64," + str(generate_spectrogram(harmonic_samples, rate, opt=1))
		response['h_spectrogram'] = h_spectrogram_encoding
		p_spectrogram_encoding = "data:image/png;base64," + str(generate_spectrogram(percussive_samples, rate, opt=2))
		response['p_spectrogram'] = p_spectrogram_encoding

		if fft_on:
			fourier_transform = get_fft(samples, rate)
			fftplot_encoding = "data:image/png;base64," + str(generate_fft_plot(fourier_transform['x'], fourier_transform['y']))
			response['fftplot'] = fftplot_encoding

		return jsonify(response) # dict of lists

	return render_template("index.html")



if __name__ == "__main__":
	app.run(debug=True)





#------- helper func to get fft values ------# 
