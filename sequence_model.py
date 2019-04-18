import glob
import os
from collections import OrderedDict
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw


class SequenceModel:
    original_anno = [[-1, -1] for _ in range(10)]
    anno_radius = 3
    anno_color = [(255, 0, 0),
                  (255, 255, 0),
                  (0, 255, 0),
                  (0, 255, 255),
                  (0, 0, 255),

                  (255, 0, 255),
                  (255, 255, 255),
                  (255, 0, 0),
                  (255, 255, 0)
                  ]

    def __init__(self):
        self.working_dir = None
        self.annotation_file = None

        self.img_format = 'left_color_????.png'

        self.seq_list = OrderedDict()

    def clear_seq_list(self):
        self.seq_list.clear()

    @staticmethod
    def get_id_from_filename(filename):
        return int(filename[-8: -4])

    def load_working_dir(self, dir_name):
        if not os.path.exists(dir_name):
            raise FileExistsError('working_dir %s not found' % dir_name)
        try:
            self.save_annotation_file()
        except FileExistsError:
            pass
        self.clear_seq_list()
        self.working_dir = dir_name
        self.annotation_file = os.path.join(self.working_dir, 'annotation.txt')

        img_files = glob.glob(os.path.join(dir_name, self.img_format))
        seq_ids = [self.get_id_from_filename(file) for file in img_files]
        seq_ids.sort()

        # seq_ids = [seq_ids[i] for i in range(0, len(seq_ids), 5)]

        annos = self.load_annotation_file()

        for seq_id in seq_ids:
            if seq_id in annos:
                anno = annos[seq_id]
            else:
                anno = None
            self.seq_list[seq_id] = anno
        return

    def load_annotation_file(self):
        anno = OrderedDict()
        if self.annotation_file is None or not os.path.exists(self.annotation_file):
            return anno
        with open(self.annotation_file) as f:
            for line in f.readlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    items = line.split()
                    _id = int(items[0])
                    _anno_coords = []
                    for i in range(1, 19, 2):
                        _anno_coords.append([float(items[i]), float(items[i + 1])])
                    if _id in anno:
                        raise AttributeError('annotation file error')
                    anno[_id] = _anno_coords
        return anno

    def save_annotation_file(self, filename=None):
        if filename is None:
            if self.working_dir is None:
                return
            filename = self.annotation_file

        if filename is None:
            raise FileExistsError('saving annotation error for %s' % filename)
        with open(filename, 'w') as f:
            for _id, _anno in self.seq_list.items():
                if _anno is None:
                    continue
                f.write('%d\t' % _id)
                for i in range(9):
                    f.write('%1.2f\t%1.2f\t' % (_anno[i][0], _anno[i][1]))
                f.write('\n')
        return

    def update_anno(self, seq_id, point_id, u, v):
        if seq_id not in self.seq_list:
            raise KeyError
        if self.seq_list[seq_id] is None:
            self.seq_list[seq_id] = self.original_anno.copy()
        self.seq_list[seq_id][point_id] = [u, v]

    @lru_cache(10)
    def load_imgs(self, seq_id):
        if seq_id not in self.seq_list:
            return [None]
        img_files = [os.path.join(self.working_dir, self.img_format.replace('????', '%04d' % seq_id))]
        imgs = []
        for file in img_files:
            if not os.path.exists(file):
                imgs.append(None)
            else:
                img = Image.open(file)
                img = img.resize((640, 480), Image.BILINEAR)
                img_array = np.asarray(img, np.uint8)
                imgs.append(img_array)
        return imgs

    def load_imgs_with_anno(self, seq_id):
        imgs = self.load_imgs(seq_id).copy()
        if self.seq_list[seq_id] is None:
            return imgs
        if imgs[0] is not None:
            img = Image.fromarray(imgs[0])
            draw = ImageDraw.Draw(img)
            for i in range(9):
                anno = self.seq_list[seq_id][i]
                u = int(anno[0])
                v = int(anno[1])
                if u < 0 or v < 0:
                    continue
                draw.ellipse((u-self.anno_radius, v-self.anno_radius, u+self.anno_radius, v+self.anno_radius),
                             fill=self.anno_color[i])
            del draw
            imgs[0] = np.asarray(img, np.uint8)
        return imgs
