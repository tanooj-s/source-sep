const webpack = require('webpack');
const config = {
    entry:  __dirname + '/js/index.js',
    output: {
        path: __dirname + '/dist',
        filename: 'bundle.js',
    },
    resolve: {
        extensions: ['.js', '.jsx', '.css']
    },
    module: {
  		rules: [{
					test: /\.(js|jsx)?$/,
  					exclude: /node_modules/,
  					loader: 'babel-loader'
  				},
  				{
					test: /(\.css)$/,
					include: /node_modules/,
  					loader: 'css-loader'
  				},


		]
	}
};
module.exports = config;