#!/usr/bin/python

from PIL import Image
import numpy
import cv2
import sys
import os
import argparse
import Queue
import time
import json
import os
from tqdm import tqdm

import threading
import multiprocessing


def safe_print(content):
    print "{0}\n".format(content),


def get_area_for_calculation(image_width, image_height, ircut_moving_direction,
                             padding_percent=0.05, area_thickness=0.2):
    ''' returns 2 x (x, y, w, h) for area calautaion '''
    up_padding_percent = padding_percent
    left_padding = image_width * padding_percent
    left_padding_A = left_padding
    up_padding_A = image_width * up_padding_percent
    if ircut_moving_direction is 'vertical':
        area_width = image_width * (1 - padding_percent * 2)
        area_height = image_height * area_thickness

        area_width_A = area_width
        area_height_A = area_height

        left_padding_B = left_padding
        up_padding_B = image_height - (image_height * padding_percent + area_height)
        area_width_B = area_width
        area_height_B = area_height

    elif ircut_moving_direction is 'horizontal':
        area_width = image_width * area_thickness
        area_height = image_height * (1 - padding_percent * 2)

        area_width_A = image_width * area_thickness
        area_height_A = image_height * (1 - up_padding_percent * 2)

        left_padding_B = image_width - (image_width * padding_percent + area_width)
        up_padding_B = image_width * up_padding_percent
        area_width_B = image_width * area_thickness
        area_height_B = image_height * (1 - up_padding_percent * 2)

    areaA = (
        int(round(left_padding_A)), int(round(up_padding_A)),
        int(round(area_width_A)), int(round(area_height_A))
    )
    areaB = (
        int(round(left_padding_B)), int(round(up_padding_B)),
        int(round(area_width_B)), int(round(area_height_B))
    )

    return (areaA, areaB)


class PixelCounter(object):
    ''' loop through each pixel and average rgb '''
    def __init__(self, image, areas):
        self.image = image
        self.opencvImage = cv2.cvtColor(numpy.array(self.image),
                                        cv2.COLOR_RGB2GRAY)

        self.areas = areas

    def brightnessDifference(self):
        areaA_total = 0
        areaB_total = 0
        row_span = 16
        col_span = 16

        area = self.areas[0]
        x, y, w, h = area[0], area[1], area[2], area[3]

        for row in xrange(y, y+h, row_span):
            for col in xrange(x, x+w, col_span):
                areaA_total = areaA_total + self.opencvImage[row][col]

        area = self.areas[1]
        x, y, w, h = area[0], area[1], area[2], area[3]

        for row in xrange(y, y+h, row_span):
            for col in xrange(x, x+w, col_span):
                areaB_total = areaB_total + self.opencvImage[row][col]

        areaA_average = areaA_total / ((w / col_span) * (h / row_span))
        areaB_average = areaB_total / ((w / col_span) * (h / row_span))

        return (abs(areaA_average - areaB_average))

    def averagePixels(self):
        r, g, b = 0, 0, 0
        count = 0
        for x in xrange(self.image.size[0]):
            for y in xrange(self.image.size[1]):
                tempr, tempg, tempb = self.image[x, y]
                r += tempr
                g += tempg
                b += tempb
                count += 1

        # calculate averages
        return (r/count), (g/count), (b/count), count


def compute_batch(tid, jpegs, queue):
    for jpeg in jpegs:
        image = Image.open(jpeg)
        image_width, image_height = image.size
        area = get_area_for_calculation(image_width, image_height,
                                        ircut_moving_direction)
        pc = PixelCounter(image, area)
        diff = pc.brightnessDifference()
        result = {'jpeg': "file://{}/".format(os.getcwd()) + jpeg, 'diff': diff}
        queue.put(result)

#         output = "file: {}, diff: {}".format(jpeg, diff)
#         safe_print(output)


def serialize(result, filename):
    json.dump(result, file(filename, "w"), indent=4, separators=(',', ': '))


def parse_argument():
    parser = argparse.ArgumentParser(description="IRCut stuck detect")
    parser.add_argument("-f", "--folder", help="JPEGs folder", type=str, default="jpeg")
    parser.add_argument("-d", "--direction", type=str, help="IRCut moving direction. 'v' for vertical, 'h' for horizontal", choices=["v", "h"], default='h')
    parser.add_argument("-o", "--output", type=str, help="Output file", default="output.json")
    parser.add_argument("-t", "--threads", type=int, help="Number of threads for processing. 0 for auto", choices=range(0, 9), default=0)
    return parser

def initialize():
    filelist = []
    path = os.path.abspath("./" + folder)
    for filename in os.listdir(folder):
        if filename.endswith(".jpeg") or filename.endswith(".jpg"):
            filelist.append(path + "/" + filename)

    threads = []
    num_files = len(filelist)
    file_step = num_files / cpus
    start = 0
    queue = Queue.Queue()
    for cpu in xrange(0, cpus):
        sublist = filelist[start:start+file_step]
        t = threading.Thread(target=compute_batch, args=(cpu, sublist, queue))
        t.daemon = True
        t.start()
        threads.append(t)
        start = start+file_step

    return (threads, queue, num_files)


if __name__ == '__main__':

    parser = parse_argument()
    args = parser.parse_args()
    folder = args.folder
    ircut_moving_direction = 'horizontal' if args.direction is 'h' else 'vertical'
    outputfile = args.output
    if os.path.isfile(outputfile) is True:
        sys.stdout.write("{} exists, do you wanna continue? (y/N) ".format(outputfile))
        sys.stdout.flush()
        ans = raw_input().lower()
        if not ans in ("yes", "y", "yep", "ok", "sure"):
            sys.exit(1)

    if args.threads == 0:
        cpus = multiprocessing.cpu_count()
    else:
        cpus = int(args.threads)

    threads, queue, num_files = initialize()

    try:
        processed = []
        bar = tqdm(total=num_files)

        while True:

            subprocessed = []
            while not queue.empty():
                subprocessed.append(queue.get())

            time.sleep(1)
            bar.update(len(subprocessed))
            processed += subprocessed

            all_active = True
            for t in threads:
                if not t.isAlive():
                    all_active = False

            if not all_active:
                while not queue.empty():
                    subprocessed.append(queue.get())
                processed += subprocessed
                break


    except KeyboardInterrupt:
        serialize(processed, outputfile)
        sys.exit(1)

    serialize(processed, outputfile)
