import codecs
import json
import os
import re

import random
from model import *
from train import load_vocab


SAMPLE_RATE = 10

temp_folder = ".\\temp\\"

class Hyperparameters:
    init_dir = ".\\trial2\\"
    model_path = ''
    temperature = 0.7           # Temperature for sampling from softmax: ''higher temperature, more random; 'lower temperature, more greedy.
    max_prob = False
    start_text = "~ "
    length = 10000
    seed = random.randint(0, 100)
    evaluate = debug = False
    
def run(length=None):
    args = Hyperparameters()
    if length:
        args.length = length
    # Prepare parameters.
    with open(os.path.join(args.init_dir, 'result.json'), 'r') as f:
        result = json.load(f)
    params = result['params']

    if args.model_path:    
        best_model = args.model_path
    else:
        best_model = result['best_model']

    best_valid_ppl = result['best_valid_ppl']
    if 'encoding' in result:
        args.encoding = result['encoding']
    else:
        args.encoding = 'utf-8'
    args.vocab_file = os.path.join(args.init_dir, 'vocab.json')
    vocab_index_dict, index_vocab_dict, vocab_size = load_vocab(args.vocab_file, args.encoding)

    # Create graphs
    logging.info('Creating graph')
    graph = tf.Graph()
    with graph.as_default():
        with tf.name_scope('evaluation'):
            test_model = CharRNN(is_training=False, use_batch=False, **params)
            saver = tf.train.Saver(name='checkpoint_saver')

    if args.evaluate:
        example_batches = BatchGenerator(args.example_text, 1, 1, vocab_size,
                                         vocab_index_dict, index_vocab_dict)
        with tf.Session(graph=graph) as session:
            saver.restore(session, best_model)
            ppl = test_model.run_epoch(session, len(args.example_text),
                                        example_batches,
                                        is_training=False)[0]
            print('Example text is: %s' % args.example_text)
            print('Perplexity is: %s' % ppl)
    else:
        if args.seed >= 0:
            np.random.seed(args.seed)
        # Sampling a sequence 
        with tf.Session(graph=graph) as session:
            saver.restore(session, best_model)
            sample = test_model.sample_seq(session, args.length, args.start_text,
                                            vocab_index_dict, index_vocab_dict,
                                            temperature=args.temperature,
                                            max_prob=args.max_prob)
            # print('Sampled text is:\n%s' % sample)
    return sample

if __name__ == '__main__':
    sample = run()
    print(sample)
