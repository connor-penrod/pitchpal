# PitchPal 
### What is it?
PitchPal is a voice-activated presentation helper. Using fuzzy matching algorithms and Speech-to-Text technology, it automatically changes your slides for you as you speak. You'll no longer need to worry about switching slides manually yourself, or trust another person to switch in the proper place.

Simply add a copy of your speech/pitch (or just the parts where you want it to switch) and add the slides you want it to present, and PitchPal will handle the rest.

Currently PitchPal only supports .GIF image format.

### Installation
PitchPal is compatible with Ubuntu 16.xx

PitchPal requires Python 3 and Pip to be installed on your computer.

To install, navigate to the root 'pitchpal' directory and run

  `sudo ./install.sh`

---

### Running
To run PitchPal, navigate to the root 'pitchpal' directory and run

  `sudo ./start.sh`

---

### Adding Slides and Pitches
To add slides, navigate to `pitchpal/pythonlib/images` and put the desired slides in there. PitchPal presents them in alphanumeric order.

To change the pitch manuscript, navigate to `pitchpal/pythonlib` and edit the `manuscript.txt` file. PitchPal pairs each line (text ending with a newline) to correspond to each slide in order.

For example, the text:

`
Five score years ago, a great American, in whose symbolic shadow we stand signed the Emancipation Proclamation
This momentous decree came as a great beacon light of hope to millions of Negro slaves who had been seared in the flames of withering injustice
`

Would tell PitchPal

`
Slide 1 -> Five score years ago, a great American, in whose symbolic shadow we stand signed the Emancipation Proclamation
`

`
Change to Slide 2
`

`
Slide 2 -> This momentous decree came as a great beacon light of hope to millions of Negro slaves who had been seared in the flames of withering injustice
`

`
Change to slide 3
`

---

### Slideshow Configuration & Settings
PitchPal is configured via a `settings.conf` file located in the root directory.
