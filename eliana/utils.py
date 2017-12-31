"""
.. module:: utils
    :synopsis: utility functions module

.. moduleauthor:: Raymel Francisco <franciscoraymel@gmail.com>
.. created:: Dec 26, 2017
"""
import os
import pandas as pd
from PIL import Image
from glob import glob
from skimage import io, color
from scipy.misc import imresize
import numpy as np

import collections

from eliana import config
from eliana.lib.mlp import MLP


def image_single_loader(img_path):
    img = io.imread(img_path)
    img = color.gray2rgb(img)

    w_base = 300
    w_percent = (w_base / float(img.shape[0]))
    h = int((float(img.shape[1]) * float(w_percent)))

    img = imresize(img, (w_base, h))

    return img


# @log('Loading images...')
def image_batch_loader(dir_, limit=None):

    # logger_.info('Test images dir: ' + dir_)
    print('Test images dir: ' + dir_)

    dir_glob = sorted(glob(os.path.join(dir_, '*.jpg')))

    for img_path in dir_glob[:limit]:

        img = image_single_loader(img_path)
        yield img, img_path


def interpolate(value, place=0.01):
    return float(format(value * place, '.3f'))


def show(img):
    Image.fromarray(img).show()


# @log('Initializing training...')
def train(trainer, inputs):

    df = pd.read_pickle(trainer['dataset'])

    mlp = MLP()
    mlp.load_model(path=None)

    inputs = df[inputs]
    outputs = df[['Emotion Value']].as_matrix().ravel()

    # logger_.info('Training fitness: ' + str(mlp.train(inputs, outputs)))
    mlp.train(inputs, outputs)
    mlp.save_model(path=trainer['model'])


def build_training_data(
    trainer, emotion_combinations=['happiness', 'sadness', 'fear']
):
    # emotion filtering
    emotions = {}
    for em in emotion_combinations:
        emotions[em] = config.emotions_map[em]

    # dataset building
    data = []
    for emotion_str, emotion_val in emotions.items():
        dir_images = os.path.join(trainer['raw_images_root'], emotion_str)

        for i, (img, img_path) in enumerate(
            image_batch_loader(dir_=dir_images, limit=None)
        ):
            datum = [img_path.split('/')[-1]]
            for _, func in trainer['features'].items():

                feature = func(img)

                # if multiple features in one category
                if isinstance(feature, collections.Sequence):
                    for item in feature:
                        datum.append(item)
                else:
                    datum.append(feature)

            datum.extend([emotion_str, emotion_val])

            data.append(datum)

    # dataset saving
    df = pd.DataFrame(
        data,
        columns=trainer['columns']
    )
    config.logger_.debug('Dataset:\n' + str(df))
    df.to_pickle(trainer['dataset'])


# def build_training_data(
#     dir_images,
#     dataset,
#     tag,
#     columns,
#     append=False,
#     mode='oia'
# ):

#     # prepare object annotator
#     annotator = Annotator(
#         model=annotator_params['model'],
#         ckpt=annotator_params['ckpt'],
#         labels=annotator_params['labels'],
#         classes=annotator_params['classes']
#     )

#     # data building
#     data = []
#     for i, (img, img_path) in enumerate(
#         image_batch_loader(dir_=dir_images, limit=None)
#     ):

#         print(img_path)
#         objects = annotator.annotate(img)
#         objects.sort(key=lambda obj: obj[1].shape[0] * obj[1].shape[1])

#         # print(objects)
#         # for obj in objects:
#         #     show(obj[1])

#         palette_1, palette_2, palette_3 = Palette.dominant_colors(img)

#         palette_1 = interpolate(palette_1, place=0.000000001)
#         palette_2 = interpolate(palette_2, place=0.000000001)
#         palette_3 = interpolate(palette_3, place=0.000000001)

#         color = Color.scaled_colorfulness(img)
#         color = interpolate(color)

#         texture = Texture.texture(img)
#         texture = interpolate(texture, place=0.1)

#         if mode == 'overall':
#             data.append(
#                 [
#                     img_path.split('/')[-1],
#                     palette_1,
#                     palette_2,
#                     palette_3,
#                     color,
#                     texture,
#                     tag,
#                     emotions_map[tag],
#                     objects
#                 ]
#             )
#         elif mode == 'oia':
#             data.append(
#                 [
#                     img_path.split('/')[-1],
#                     palette_1,
#                     palette_2,
#                     palette_3,
#                     color,
#                     texture,
#                     0. if not objects else objects[0][2],
#                     tag,
#                     emotions_map[tag]
#                 ]
#             )

#     if append:
#         df = pd.read_pickle(dataset)
#         df2 = pd.DataFrame(
#             data,
#             columns=columns
#         )
#         df = df.append(df2, ignore_index=True)
#     else:
#         df = pd.DataFrame(
#             data,
#             columns=columns
#         )
#     logger_.debug('Dataset:\n' + str(df))
#     df.to_pickle(dataset)
