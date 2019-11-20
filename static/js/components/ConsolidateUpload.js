import React from 'react'
import axios from 'axios'

class ConsolidateUpload extends React.Component {
	constructor(props) {
		super(props)
		this.state = {
			lowerbound: "",
			upperbound: "",
			fft_on: false,
			audiofile: ""
		}

		this.handleSubmit = this.handleSubmit.bind(this)
		// sends the consolidated (file+opts) form as a single POST request
		this.handleChange = this.handleChange.bind(this)
		// handles input change like normal Reactive elements
		this.handleFileLoad = this.handleFileLoad.bind(this)
		// only loads user file in, but doesn't post it to backend
	}

	handleFileLoad(event) {
		let files = event.target.files
		let reader = new FileReader()
		reader.readAsDataURL(files[0])
		reader.onload = (e) => {
			this.setState({ 
				audiofile: reader.result // what does reader.result return
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
		.then(res => console.log(res))
	//  .then to the plot component with the data returned by the server which should be arrays for plot axes? or a plot image from 
	//	matplotlib/plot.ly instead? will need to ponder upon this
		.catch(error => console.log(error))
	}


	render() {
		return (
			<div>
				<form onSubmit = {this.handleSubmit} encType = 'multipart/form-data'>
					<input type = "file" name = 'audiofile' onChange = {this.handleFileLoad} />
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
			</div>
		)

	}	
	
}

export default ConsolidateUpload