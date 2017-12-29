"""
.. module:: eliana
    :synopsis: main module for eliana package

.. moduleauthor:: Raymel Francisco <franciscoraymel@gmail.com>
.. created:: Nov 24, 2017
"""
from eliana.imports import *

import cv2
from imutils import build_montages
from skimage import io


class Eliana:

    def __init__(self, model_path):

        self.mlp = MLP()
        self.mlp.load_model(path=model_path)

    def run_overall(self, img):

        palette_1, palette_2, palette_3 = Palette.dominant_colors(img)

        palette_1 = interpolate(palette_1, place=0.000000001)
        palette_2 = interpolate(palette_2, place=0.000000001)
        palette_3 = interpolate(palette_3, place=0.000000001)

        color = Color.scaled_colorfulness(img)
        color = interpolate(color)

        texture = Texture.texture(img)
        texture = interpolate(texture, place=0.1)

        return self.mlp.run(input_=[
            palette_1,
            palette_2,
            palette_3,
            color,
            texture]
        )

    def run_object(self, objects):
        pass


enna = Eliana(trainer_overall['model'])

dir_images = os.path.join(
    os.getcwd(),
    trainer_overall['test_images'],
    'test'
)

to_montage = []

for i, (img, img_path) in enumerate(
    image_batch_loader(dir_=dir_images, limit=None)
):
    print(img_path)

    result = enna.run_overall(img)

    print('Run:', result)
    cv2.putText(
        img,
        emotions_list[result[0]],
        (40, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.4,
        (0, 255, 0),
        3
    )

    to_montage.append(img)

montage = build_montages(to_montage, (180, 180), (6, 6))[0]
show(montage)
