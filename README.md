# Generate Bach's Music

An application using crazydonkey200's [tensorflow-char-rnn](https://github.com/crazydonkey200/tensorflow-char-rnn)



![](https://raw.githubusercontent.com/T-K-233/Generate-Bach-Music/master/demo-result/midi.png)

<iframe width="560" height="315" src="https://www.youtube.com/embed/kmbmLfTZc2w" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>



## Installation

### Dependencies
- Python 3
- TensorFlow >= 1.2

Follow the instructions on [TensorFlow official website](https://www.tensorflow.org/) to install TensorFlow. 



## Usage
### Training

Open the `dist` folder and move all the source midi files into the `midi` folder

To train with default settings:
```bash
python train.py
```

All the output of this experiment will be saved in `./output` folder. 

The experiment log will be printed to stdout by default. 

The output folder layout: 
```
dist
    ├── train.data			# Re-formatted data text for training.
    ├── dependencies		# Folder containing the tools needed for midi-csv conversions.
        ├── Csvmidi.exe
        ├── Midicsv.exe
    ├── trail1&2         	# Previous experiments
    ├── output              # Folder containing saved model
    ├── conosle.py			# The interface (not really)
    ├── model.py			# The Char-RNN model
    ├── sample.py			# Scripts for sampling
    ├── train.py			# Scripts for training
    ├── util.py				# Scripts for reformatting data
```

Note: `train.py` assume the data file is using utf-8 encoding by default.




### Sampling
To generate midi file from the best model of an experiment:
```bash
python console.py
```
The midi file will be generated under `output` folder.



## Visualization
To use Tensorboard (a visualization tool in TensorFlow) to [visualize the learning](https://www.tensorflow.org/get_started/summaries_and_tensorboard#tensorboard-visualizing-learning) (the "events" tab) and [the computation graph](https://www.tensorflow.org/versions/r0.8/how_tos/graph_viz/index.html#tensorboard-graph-visualization) (the "graph" tab).

run
```bash
tensorboard --logdir=your-output-folder/tensorboard_log
```



### P.S.

A useful picture:

![](https://raw.githubusercontent.com/Conchylicultor/MusicGenerator/master/data/test/midi_keyboard_correspondance.png)