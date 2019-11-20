import React from "react"

//import PlotComponent from "./components/PlotComponent.js"
//import ConsolidateUpload from "./components/ConsolidateUpload.js"
import ReactAudioPlayer from 'react-audio-player';
//import AudioPlayer from "react-h5-audio-player";
import axios from 'axios'
import Image from 'react-render-image'

// need an Audio player component to render after file is uploaded
// file upload component should be separate from the options component

class App extends React.Component {
	constructor() {
		super()
		this.state = {
			lowerbound: "",
			upperbound: "",
			fft_on: false,
			uploaded_audiofile: "",
			isUploaded: false,
			readyToPlot: false,
			response_data: ""
		}
		this.handleSubmit = this.handleSubmit.bind(this)
		this.handleChange = this.handleChange.bind(this)
		this.handleFileLoad = this.handleFileLoad.bind(this)
	}


	handleFileLoad(event) {
		let files = event.target.files
		let reader = new FileReader()
		reader.readAsDataURL(files[0])
		reader.onload = (e) => {
			this.setState({ 
				uploaded_audiofile: reader.result, // what does reader.result return
				isUploaded: true
			 })
			console.log(reader.result) // it's just the result of jsonify data
			console.log("^^ file was uploaded by the user")
		}
	}

	handleChange(event) {		
		const { name, value, type, checked } = event.target
		type === 'checkbox' ? this.setState({ [name]: checked }) : this.setState({ [name]: value })
	}


	handleSubmit(event) {
		event.preventDefault()
		axios.post("http://127.0.0.1:5000/", this.state)
		.then(res => this.setState({ 
			readyToPlot: true,
			response_data: res.data }))
		.then(res => console.log(this.state.response_data))
		.catch(error => console.log(error))
	}


	render () {
		return (

			<div>
				<h3> Welcome to Source Separation!</h3>

				<p>Please upload an audio file and select upper and lower timestamps and options.</p>
				
				<form onSubmit = {this.handleSubmit} encType = 'multipart/form-data'>
					<input type = "file" name = 'uploaded_audiofile' onChange = {this.handleFileLoad} />
					<br />
					Lower timestamp: <input type = 'text' name = 'lowerbound' value = {this.state.lowerbound} onChange = {this.handleChange} />
					<br />
					Upper timestamp: <input type = 'text' name = 'upperbound' value = {this.state.upperbound} onChange = {this.handleChange} />
					<br />
					Display spectrum? <input type = 'checkbox' name = 'fft_on' checked = {this.state.fft_on} onChange = {this.handleChange} />
					<br />
					<button>Submit</button>		
				</form>

				<p>Lower timestamp is <b>{this.state.lowerbound}</b> and upper timestamp is <b>{this.state.upperbound}</b></p>

				<p>You have chosen <b>{this.state.fft_on ? 'TO' : 'NOT TO'}</b> display the frequency spectrum</p>

				<p>We are <b>{this.state.readyToPlot ? 'ready to' : 'not ready to'}</b> plot waveforms</p>

				<br />



















































				{this.state.readyToPlot && <p>Original file uploaded: </p>}

				{this.state.readyToPlot && <ReactAudioPlayer src = {this.state.response_data.original_file} />} 	 

				<br />

				{this.state.readyToPlot && <p>Harmonic components: </p>}

				{this.state.readyToPlot && <ReactAudioPlayer src = {this.state.response_data.harmonic_file} />} 	 

				<br />

				{this.state.readyToPlot && <p>Percussive components: </p>}

				{this.state.readyToPlot && <ReactAudioPlayer src = {this.state.response_data.percussive_file} />} 	 

				<br />


				{this.state.readyToPlot && <img src = {this.state.response_data.waveplot} width="1000" height = "500"/>}

				<br />

				{this.state.readyToPlot && this.state.fft_on && <img src = {this.state.response_data.fftplot} width="1000" height = "500"/>}

				<br />

				{this.state.readyToPlot && <img src = {this.state.response_data.spectrogram} width="1000" height = "500"/>}
				{this.state.readyToPlot && <img src = {this.state.response_data.h_spectrogram} width="1000" height = "500"/>}

				<br />
				{this.state.readyToPlot && <img src = {this.state.response_data.p_spectrogram} width="1000" height = "500"/>}

			</div>

		)
	}
}

// each plot + audio bit has to be its own component

export default App


/*{this.state.readyToPlot && <PlotComponent x_axis = {this.state.plot_vars.wave_x} y_axis = {this.state.plot_vars.wave_y}/>}
				
				<br />

				{this.state.readyToPlot && this.state.fft_on && <PlotComponent x_axis = {this.state.plot_vars.fft_x} y_axis = {this.state.plot_vars.fft_y}/> }

				<br />*/



// sounds need to be inside components


// IT"S GOTTA BE ONE FORM AND ONE COMPONENT AND ONE POST REQUEST TO THE /uploaded ENDPOINT
// just try it no bro, will be easier to deal with from the Flask side





/* just do the upload component separately, as a direct upload of the file, don't try to treat it as a 
form submission
/* send the user options separately as a form

/* 
include an upload component in the App using HTML form upload normal boring stuff
form data sent as a POST request to the server (same page/endpoint?)
the audio file itself can be then be locally read from within the Flask app - i guess not, suppose it needs to be read in from request.files
but to send specifying information about timestamps, cron time to provide each file a uid so that we know exactly what to pass in to librosa.read()
we will need to send a json object from within the react component to some url/endpoint that we can then route to Flask
(HTTP POST from javascript to http:/localhost.com:5000/someurl?)
do we need to use the Flask request object?
will the functions inside the Flask functions routed to by URLs need dict parameters (which are the JSON objects)
HTML forms will need to send POST requests from within React components...?

in the app
have a Form component at the top that's always displayed
and a Plot component that's conditionally rendered for the waveform
Plot component conditionally rendered for the spectrum (FFT) if they elect to see it
Component to play 



*/