import util
import sample


def train_model():
    file = 'train.data'
    util.preprocess_data()


def generate():
    result = sample.run(100000)
    util.decode(result, util.Params())
    # print(result)


generate()
