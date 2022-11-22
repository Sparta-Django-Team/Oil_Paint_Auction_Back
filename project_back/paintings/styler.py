import cv2
import numpy as np
import datetime


model_list = [
    '01_eccv16_composition_vii.t7',
    '02_eccv16_la_muse.t7',
    '03_eccv16_starry_night.t7',
    '04_eccv16_the_wave.t7',
    '05_instance_norm_candy.t7',
    '06_instance_norm_feathers.t7',
    '07_instance_norm_la_muse.t7',
    '08_instance_norm_mosaic.t7',
    '09_instance_norm_starry_night.t7',
    '10_instance_norm_the_scream.t7',
    '11_instance_norm_udnie.t7'
]

model_num = int(input("모델넘버 입력:"))

def print_styler(model_num):        # , img_url
    date = datetime.datetime.now()

    net = cv2.dnn.readNetFromTorch(f'../media/models/{model_list[model_num]}')
    img = cv2.imread('../media/imgs/01.jpg')
    # img = cv2.imread('./media/' + str(img_url))

    # pre-processing
    h, w, c = img.shape
    img = cv2.resize(img, dsize=(500, int(h / w * 500)))

    MEAN_VALUE = [103.939, 116.779, 123.680]
    blob = cv2.dnn.blobFromImage(img, mean=MEAN_VALUE)

    # inference
    net.setInput(blob)
    output = net.forward()

    # post-processing
    output = output.squeeze().transpose((1, 2, 0))
    output += MEAN_VALUE

    output = np.clip(output, 0, 255)
    output = output.astype('uint8')

    cv2.imwrite(f'../media/imgs/results/img_{date:%y%m%d}_{date:%H%M%S}.png', output)
    print("---저장완료---")

# test
print_styler(model_num)


"""
01_eccv16_composition_vii.t7
02_eccv16_la_muse.t7
03_eccv16_starry_night.t7
04_eccv16_the_wave.t7
05_instance_norm_candy.t7
06_instance_norm_feathers.t7
07_instance_norm_la_muse.t7
08_instance_norm_mosaic.t7
09_instance_norm_starry_night.t7
10_instance_norm_the_scream.t7
11_instance_norm_udnie.t7
"""
