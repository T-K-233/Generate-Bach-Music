import argparse
import codecs
import json
import logging
import os
import shutil
import sys

import numpy as np
from model import *
from six import iteritems

class Hyperparameters:
    data_file = ".\\train.data"
    encoding = 'utf-8'
    output_dir = ".\\output\\"
    n_save = 1				   # how many times to save the model during each epoch.
    max_to_keep = 3			    # how many recent models to keep
    hidden_size = 256			# size of RNN hidden state vector
    embedding_size = 0			# size of character embeddings
    num_layers = 3			    # number of layers in the RNN
    num_unrollings = 20			# number of unrolling steps.
    model = 'lstm'			    # which model to use (rnn, lstm or gru).
    num_epochs = 200			# number of epochs
    batch_size = 40			    # minibatch size
    train_frac = 0.9			# fraction of data used for training.
    valid_frac = 0.05			# fraction of data used for validation.
                                 # test_frac is computed as (1 - train_frac - valid_frac).
    dropout = 0.4			    # dropout rate, default to 0 (no dropout).
    input_dropout = 0.0			# ('dropout rate on input layer, default to 0 (no dropout), and no dropout if using one-hot representation.
    max_grad_norm = 5			# clip global grad norm
    learning_rate = 3e-3		# initial learning rate
    decay_rate = 0.95			# decay rate
    init_dir = ''
    init_model = ''
    log_to_file = debug = test = False
    progress_freq = 100			# frequency for progress report in training and evalution.
    verbose = 1			        # whether to show progress report in training and evalution.

def run():

    args = Hyperparameters()

    # Specifying location to store model, best model and tensorboard log.
    args.save_model = os.path.join(args.output_dir, 'save_model/model')
    args.save_best_model = os.path.join(args.output_dir, 'best_model/model')
    args.tb_log_dir = os.path.join(args.output_dir, 'tensorboard_log/')
    args.vocab_file = ''

    # Create necessary directories.
    if args.init_dir:
        args.output_dir = args.init_dir
    else:
        if os.path.exists(args.output_dir):
            shutil.rmtree(args.output_dir)
        for paths in [args.save_model, args.save_best_model,
                      args.tb_log_dir]:
            os.makedirs(os.path.dirname(paths))

    # Specify logging config.
    if args.log_to_file:
        args.log_file = os.path.join(args.output_dir, 'experiment_log.txt')
    else:
        args.log_file = 'stdout'

    # Set logging file.
    if args.log_file == 'stdout':
        logging.basicConfig(stream=sys.stdout,
                            format='%(asctime)s %(levelname)s:%(message)s', 
                            level=logging.INFO,
                            datefmt='%I:%M:%S')
    else:
        logging.basicConfig(filename=args.log_file,
                            format='%(asctime)s %(levelname)s:%(message)s', 
                            level=logging.INFO,
                            datefmt='%I:%M:%S')

    print('=' * 60)
    print('All final and intermediate outputs will be stored in %s/' % args.output_dir)
    print('All information will be logged to %s' % args.log_file)
    print('=' * 60 + '\n')
    

    # Prepare parameters.
    if args.init_dir:
        with open(os.path.join(args.init_dir, 'result.json'), 'r') as f:
            result = json.load(f)
        params = result['params']
        args.init_model = result['latest_model']
        best_model = result['best_model']
        best_valid_ppl = result['best_valid_ppl']
        if 'encoding' in result:
            args.encoding = result['encoding']
        else:
            args.encoding = 'utf-8'
        args.vocab_file = os.path.join(args.init_dir, 'vocab.json')
    else:
        params = {'batch_size': args.batch_size,
                  'num_unrollings': args.num_unrollings,
                  'hidden_size': args.hidden_size,
                  'max_grad_norm': args.max_grad_norm,
                  'embedding_size': args.embedding_size,
                  'num_layers': args.num_layers,
                  'learning_rate': args.learning_rate,
                  'model': args.model,
                  'dropout': args.dropout,
                  'input_dropout': args.input_dropout}
        best_model = ''
    logging.info('Parameters are:\n%s\n', json.dumps(params, sort_keys=True, indent=4))

    # Read and split data.
    logging.info('Reading data from: %s', args.data_file)
    with codecs.open(args.data_file, 'r', encoding=args.encoding) as f:
        text = f.read()


    logging.info('Creating train, valid, test split')
    train_size = int(args.train_frac * len(text))
    valid_size = int(args.valid_frac * len(text))
    test_size = len(text) - train_size - valid_size
    train_text = text[:train_size]
    valid_text = text[train_size:train_size + valid_size]
    test_text = text[train_size + valid_size:]

    if args.vocab_file:
        vocab_index_dict, index_vocab_dict, vocab_size = load_vocab(
          args.vocab_file, args.encoding)
    else:
        logging.info('Creating vocabulary')
        vocab_index_dict, index_vocab_dict, vocab_size = create_vocab(text)
        vocab_file = os.path.join(args.output_dir, 'vocab.json')
        save_vocab(vocab_index_dict, vocab_file, args.encoding)
        logging.info('Vocabulary is saved in %s', vocab_file)
        args.vocab_file = vocab_file

    params['vocab_size'] = vocab_size
    logging.info('Vocab size: %d', vocab_size)

    # Create batch generators.
    batch_size = params['batch_size']
    num_unrollings = params['num_unrollings']
    train_batches = BatchGenerator(train_text, batch_size, num_unrollings, vocab_size, 
                                   vocab_index_dict, index_vocab_dict)
    # valid_batches = BatchGenerator(valid_text, 1, 1, vocab_size,
    #                                vocab_index_dict, index_vocab_dict)
    valid_batches = BatchGenerator(valid_text, batch_size, num_unrollings, vocab_size,
                                   vocab_index_dict, index_vocab_dict)

    test_batches = BatchGenerator(test_text, 1, 1, vocab_size,
                                  vocab_index_dict, index_vocab_dict)
        
    # Create graphs
    logging.info('Creating graph')
    graph = tf.Graph()
    with graph.as_default():
        with tf.name_scope('training'):
            train_model = CharRNN(is_training=True, use_batch=True, **params)
        tf.get_variable_scope().reuse_variables()
        with tf.name_scope('validation'):
            valid_model = CharRNN(is_training=False, use_batch=True, **params)
        with tf.name_scope('evaluation'):
            test_model = CharRNN(is_training=False, use_batch=False, **params)
            saver = tf.train.Saver(name='checkpoint_saver', max_to_keep=args.max_to_keep)
            best_model_saver = tf.train.Saver(name='best_model_saver')

    logging.info('Model size (number of parameters): %s\n', train_model.model_size)
    logging.info('Start training\n')

    result = {}
    result['params'] = params
    result['vocab_file'] = args.vocab_file
    result['encoding'] = args.encoding

    try:
        # Use try and finally to make sure that intermediate
        # results are saved correctly so that training can
        # be continued later after interruption.
        with tf.Session(graph=graph) as session:
            graph_info = session.graph

            train_writer = tf.summary.FileWriter(args.tb_log_dir + 'train/', graph_info)
            valid_writer = tf.summary.FileWriter(args.tb_log_dir + 'valid/', graph_info)

            # load a saved model or start from random initialization.
            if args.init_model:
                saver.restore(session, args.init_model)
            else:
                tf.global_variables_initializer().run()
            for i in range(args.num_epochs):
                for j in range(args.n_save):
                    logging.info(
                        '=' * 19 + ' Epoch %d: %d/%d' + '=' * 19 + '\n', i+1, j+1, args.n_save)
                    logging.info('Training on training set')
                    # training step
                    ppl, train_summary_str, global_step = train_model.run_epoch(
                        session,
                        train_size,
                        train_batches,
                        is_training=True,
                        verbose=args.verbose,
                        freq=args.progress_freq,
                        divide_by_n=args.n_save)
                    # record the summary
                    train_writer.add_summary(train_summary_str, global_step)
                    train_writer.flush()
                    # save model
                    saved_path = saver.save(session, args.save_model,
                                            global_step=train_model.global_step)
                    logging.info('Latest model saved in %s\n', saved_path)
                    logging.info('Evaluate on validation set')

                    # valid_ppl, valid_summary_str, _ = valid_model.run_epoch(
                    valid_ppl, valid_summary_str, _ = valid_model.run_epoch(
                        session,
                        valid_size,
                        valid_batches, 
                        is_training=False,
                        verbose=args.verbose,
                        freq=args.progress_freq)

                    # save and update best model
                    if (not best_model) or (valid_ppl < best_valid_ppl):
                        best_model = best_model_saver.save(
                            session,
                            args.save_best_model,
                            global_step=train_model.global_step)
                        best_valid_ppl = valid_ppl
                    valid_writer.add_summary(valid_summary_str, global_step)
                    valid_writer.flush()
                    logging.info('Best model is saved in %s', best_model)
                    logging.info('Best validation ppl is %f\n', best_valid_ppl)
                    result['latest_model'] = saved_path
                    result['best_model'] = best_model
                    # Convert to float because numpy.float is not json serializable.
                    result['best_valid_ppl'] = float(best_valid_ppl)
                    result_path = os.path.join(args.output_dir, 'result.json')
                    if os.path.exists(result_path):
                        os.remove(result_path)
                    with open(result_path, 'w') as f:
                        json.dump(result, f, indent=2, sort_keys=True)

            logging.info('Latest model is saved in %s', saved_path)
            logging.info('Best model is saved in %s', best_model)
            logging.info('Best validation ppl is %f\n', best_valid_ppl)
            logging.info('Evaluate the best model on test set')
            saver.restore(session, best_model)
            test_ppl, _, _ = test_model.run_epoch(session, test_size, test_batches,
                                                   is_training=False,
                                                   verbose=args.verbose,
                                                   freq=args.progress_freq)
            result['test_ppl'] = float(test_ppl)
    finally:
        result_path = os.path.join(args.output_dir, 'result.json')
        if os.path.exists(result_path):
            os.remove(result_path)
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=2, sort_keys=True)


def create_vocab(text):
    unique_chars = list(set(text))
    vocab_size = len(unique_chars)
    vocab_index_dict = {}
    index_vocab_dict = {}
    for i, char in enumerate(unique_chars):
        vocab_index_dict[char] = i
        index_vocab_dict[i] = char
    return vocab_index_dict, index_vocab_dict, vocab_size


def load_vocab(vocab_file, encoding):
    with codecs.open(vocab_file, 'r', encoding=encoding) as f:
        vocab_index_dict = json.load(f)
    index_vocab_dict = {}
    vocab_size = 0
    for char, index in iteritems(vocab_index_dict):
        index_vocab_dict[index] = char
        vocab_size += 1
    return vocab_index_dict, index_vocab_dict, vocab_size


def save_vocab(vocab_index_dict, vocab_file, encoding):
    with codecs.open(vocab_file, 'w', encoding=encoding) as f:
        json.dump(vocab_index_dict, f, indent=2, sort_keys=True)
        
if __name__ == '__main__':
    run()
