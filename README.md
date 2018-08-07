# Generate Bach Music

music generation based on Char-RNN neural network



![](docs/first-good-piece-visualized.png)





## Demo

→ [YouTube Video](https://www.youtube.com/watch?v=9aHlzev4pPM) ←





## Dependencies

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
The midi file will be generated inside `output` folder.



### Visualization

To use Tensorboard (a visualization tool in TensorFlow) to [visualize the learning](https://www.tensorflow.org/get_started/summaries_and_tensorboard#tensorboard-visualizing-learning) (the "events" tab) and [the computation graph](https://www.tensorflow.org/versions/r0.8/how_tos/graph_viz/index.html#tensorboard-graph-visualization) (the "graph" tab).

run:
```bash
tensorboard --logdir=your-output-folder/tensorboard_log
```



## Publication

[music generation based on char-rnn neural network](http://t-k-233.tk/Generate-Bach-Music/), published at [Artificial Intelligence VIEW](http://t-k-233.tk/Generate-Bach-Music/%E5%9F%BA%E4%BA%8EChar-RNN%E7%9A%84%E9%9F%B3%E4%B9%90%E7%94%9F%E6%88%90%20%E5%AE%9E%E8%B7%B5%E4%B8%8E%E7%AE%97%E6%B3%95%E4%BD%9C%E6%9B%B2%E5%B0%9D%E8%AF%95.pdf)



## Resource

Here is a useful picture showing the relation between notes:

![](https://raw.githubusercontent.com/Conchylicultor/MusicGenerator/master/data/test/midi_keyboard_correspondance.png)