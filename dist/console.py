import util
import sample
import random
import time


def train_model():
    file = 'train.data'
    util.preprocess_data()

def generate():
    params = util.Params()
    params.output_name = 'new_sample'
    for i in range(61,100):
        random.seed(i)
        params.output_name = '%d' % i
        result = sample.run(20000, i)
        util.decode(result, params)
        print(result)
        print('fin %d' % i)


generate()
