"""
.. module:: eliana
    :synopsis: main module for eliana package

.. moduleauthor:: Raymel Francisco <franciscoraymel@gmail.com>
.. created:: Nov 24, 2017
"""
from eliana.imports import *
from eliana import config
from eliana.lib.mlp import MLP
from eliana.utils import *

import multiprocessing as mp


class Eliana:

    def __init__(
            self,
            trainer,
            parallel=False,
            batch=False,
            montage=False,
            single_path='',
            score=False
    ):
        self.trainer = trainer
        self.mlp = MLP()
        self.mlp.load_model(path=self.trainer['model'])

        self.parallel = parallel

        if self.parallel:
            self.pool = mp.Pool()

        self.batch = batch
        self.montage = montage

        if not self.batch:
            self.single_path = single_path

        self.score = score

    def run(self, img, img_path):

        input_ = []
        for key, func in self.trainer['features'].items():

            if key == 'top_colors':
                if self.parallel:
                    feature = self.pool.apply_async(
                        func,
                        [img, img_path]
                    ).get()

                else:
                    feature = func(img, img_path)

            elif key == 'top_object':
                # annotator module uses unpickable objects
                #   which can't be pooled
                feature = func(img)

            else:
                if self.parallel:
                    feature = self.pool.apply_async(
                        func,
                        [img]
                    ).get()

                else:
                    feature = func(img)

            # if multiple features in one category
            if isinstance(feature, collections.Sequence):
                for item in feature:
                    input_.append(item)
            else:
                input_.append(feature)

        return input_, self.mlp.run(input_=input_).tolist()

    def batch_process(self):

        if self.montage:
            to_montage = []

        emotion_combinations = ['happiness', 'sadness', 'fear']
        emotions = {}
        for em in emotion_combinations:
            emotions[em] = config.emotions_map[em]

        input_ = []
        output = []
        for emotion_str, emotion_val in emotions.items():

            dir_images = os.path.join(
                trainer['raw_images_testset'],
                emotion_str
            )

            for i, (img, img_path) in enumerate(
                image_batch_loader(dir_=dir_images, limit=None)
            ):
                print(img_path)

                features, result = self.run(img, img_path)

                print('Result:', config.emotions_list[result[0]])
                print('Expected:', emotion_str)

                if self.score:
                    input_.append(features)
                    output.append(config.emotions_map[emotion_str])

                if self.montage:
                    # embed the predicted result
                    put_text(
                        img=img,
                        text=config.emotions_list[result[0]],
                        offset=(40, 40),
                        color=(0, 255, 0)
                    )
                    if config.emotions_list[result[0]] == emotion_str:
                        # green if predicted correctly
                        color_ = (0, 255, 0)
                    else:
                        # red if incorrect
                        color_ = (255, 0, 0)

                    # embed the expected result
                    put_text(
                        img=img,
                        text=emotion_str,
                        offset=(40, 75),
                        color=color_
                    )

                    to_montage.append(img)

        if self.montage:
            montage_ = montage(to_montage)
            show(montage_)

        if self.parallel:
            # release multiprocessing pool
            self.pool.close()

        if self.score:
            print('Score:', self.mlp.model.score(input_, output))

    def single_process(self):

        print(self.single_path)

        emotion_str = self.single_path.split('/')[-2]

        img = image_single_loader(self.single_path)
        features, result = self.run(img, self.single_path)

        print('Result:', config.emotions_list[result[0]])
        print('Expected:', emotion_str)

        if self.montage:
            # embed the predicted result
            put_text(
                img=img,
                text=config.emotions_list[result[0]],
                offset=(40, 40),
                color=(0, 255, 0)
            )
            if config.emotions_list[result[0]] == emotion_str:
                # green if predicted correctly
                color_ = (0, 255, 0)
            else:
                # red if incorrect
                color_ = (255, 0, 0)

            # embed the expected result
            put_text(
                img=img,
                text=emotion_str,
                offset=(40, 70),
                color=color_
            )

            show(img)

        if self.score:
            print('Score:', self.mlp.model.score([features], [result]))


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model',
        action='store',
        dest='model',
        default='oea',
        help='Two eliana models available: oea and oea_less.'
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        default=False,
        dest='parallel',
        help='Enable parallel processing for faster results.'
    )
    parser.add_argument(
        '--batch',
        action='store_true',
        default=False,
        dest='batch',
        help='Enable batch processing.'
    )
    parser.add_argument(
        '--montage',
        action='store_true',
        default=False,
        dest='montage',
        help='Embed result on the image.'
    )
    parser.add_argument(
        '--single_path',
        dest='single_path',
        default=os.path.join(
            os.getcwd(),
            'training',
            'data',
            'testset',
            'happiness',
            'img17.jpg'
        ),
        help='Single image path if batch is disabled.'
    )
    parser.add_argument(
        '--score',
        action='store_true',
        dest='score',
        default=False,
        help='Add model accuracy score to output.'
    )

    args = parser.parse_args()

    if args.model == 'oea':
        trainer = config.trainer_oea

    elif args.model == 'oea_less':
        trainer = config.trainer_oea_less

    enna = Eliana(
        trainer=trainer,
        parallel=args.parallel,
        batch=args.batch,
        montage=args.montage,
        single_path=args.single_path,
        score=args.score
    )

    if args.batch:
        enna.batch_process()
    else:
        enna.single_process()
