import React from "react"
import {Line} from "react-chartjs-2"





class PlotComponent extends React.Component {

	constructor(props) {
		super(props)
		this.state = {
			labels: this.props.x_axis,
			datasets: [
				{
					data: this.props.y_axis, // need  x axis for fourier plot
					fill: false,
		      		lineTension: 0.1,
			      	backgroundColor: 'rgba(75,12,192,0.4)',
			      	borderColor: 'rgba(75,12,192,1)',
			      	borderCapStyle: 'butt',
			      	borderDash: [],
			      	borderDashOffset: 0.0,
			      	borderJoinStyle: 'miter',
			      	pointBorderColor: 'rgba(75,62,192,1)',
			      	pointBackgroundColor: '#fff',
			      	pointBorderWidth: 1,
			      	pointRadius: 0.1,
			      	pointHitRadius: 10
		

				}
			]
		}
	}

	render() {
		console.log(this.props.x_axis)
		console.log(this.props.y_axis)
		return (
			<div>
				<h4> X-axis items {this.props.x_axis.length} </h4>
				<h4> Y-axis items {this.props.y_axis.length} </h4>

				<Line data = { this.state } width = {100} height = {50} options = {{ responsive: true, maintainAspectRatio: false }}/> 
			</div>


		)
	}
}

// instead of this.state do this.props to access values from parent component
// inst

export default PlotComponent