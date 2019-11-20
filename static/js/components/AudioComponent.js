import React from "react"
import { PlayButton, Timer } from 'react-soundplayer/components'
import { withCustomAudio } from 'react-soundplayer/addons'

// audio source
const streamUrl = 'https://example.org/path/to/file.mp3'

// some track meta information
const trackTitle = 'Great song by random artist'

const SoundPlayer = withCustomAudio(props => {
  const { trackTitle } = props

  return (
	    <div>
	      <PlayButton {...this.props} />
	      <h2>{trackTitle}</h2>
	      <Timer {...this.props} />
	    </div>
 	)
})

export default SoundPlayer