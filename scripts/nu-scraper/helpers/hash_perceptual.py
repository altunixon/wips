#!/usr/bin/env python
# -*- coding: utf-8 -*-

# http://www.hackerfactor.com/blog/?/archives/432-Looks-Like-It.html
# http://www.hackerfactor.com/blog/index.php?/archives/529-Kind-of-Like-That.html
import os, json
from PIL import Image
import numpy
import scipy.fftpack
from scipy.misc import toimage
from helpers.misc import print_log

# UTILITIES
def hexxer(binary_string):
    if isinstance(binary_string, str):
        return str(hex(int(binary_string, 2)))[2:][::-1].upper()
    elif isinstance(binary_string, list):
        return str(hex(int(''.join(binary_string), 2)))[2:][::-1].upper()
    else:
        return str(hex(int(binary_string)))[2:][::-1].upper()

def hamming_distance(s1, s2, **options):
    output_percent = options.pop('percent', False)
    if s1 is not None and s2 is not None:
        if len(s1) == len(s2):
            diff = sum(ch1 != ch2 \
                for ch1, ch2 \
                in izip(list(s1), list(s2))
            )
            if not output_percent:
                return diff
            else:
                hundred_per = len(s1)
                return int(
                    ( (hundred_per - diff) / hundred_per ) * 100
                )
        else:
            return 666
    else:
        return 999

# MULTIPLE TYPE OF HASH, READ IMAGE EACH TIME
class image_hash():
    def __init__(self, image_path, **options):
        self.imgpath   = image_path
        self.img_asize = (8, 8)
        self.img_dsize = (9, 8)
        self.out_hex   = options.pop('hex', False)

    def get_image_data(self, resample=(8,8), **options):
        aspil_image = options.pop('pil', False)
        try:
            with Image.open(self.imgpath) as imgopen:
                imgdata = imgopen.resize(
                    resample, Image.ANTIALIAS
                ).convert('L')
            if aspil_image:
                return imgdata
            else:
                return list(imgdata.getdata())
        except Exception as excp:
            print(excp)
            return None

    # Compare Pixel Average
    def ahash(self, **options):
        output_hex = options.pop('hex', self.out_hex)
        pixel_data = self.get_image_data(self.img_asize, pil=False)
        if pixel_data is not None and len(pixel_data) > 0:
            pixel_avg  = sum(pixel_data)/len(pixel_data)
            pixel_bits = "".join(
                ['1' if (px >= pixel_avg) else '0' for px in pixel_data]
            )
            if not output_hex:
                return pixel_bits
            else:
                return hexxer(pixel_bits)
        else:
            return None
    # Compare Gradient of pixel to the one next to it, from left to right
    def dhash(self, **options):
        output_hex = options.pop('hex', self.out_hex)
        pixel_data = self.get_image_data(self.img_dsize, pil=False)
        if pixel_data is not None and len(pixel_data) > 0:
            resize_width, resize_height = self.img_dsize
            pixel_bits = []
            # Looping through each pixel row
            for row in range(resize_height):
                row_start_index = row
                # Because it was compared rightward, last pixel on the right is ignored, as such resize_width - 1
                for col in range(resize_width - 1):
                    left_pixel_index = row_start_index + col
                    if pixel_data[left_pixel_index] \
                    > pixel_data[left_pixel_index + 1]:
                        pixel_bits.append('1')
                    else:
                        pixel_bits.append('0')
            if not output_hex:
                return ''.join(pixel_bits)
            else:
                return hexxer(pixel_bits)
        else:
            return None
    # Perceptual
    def phash(self, hash_size=8, highfreq_factor=4, **options):
        simple_dct = options.pop('simple', False)
        output_hex = options.pop('hex', self.out_hex)
        image_size = hash_size * highfreq_factor
        image_data = self.get_image_data((image_size, image_size), pil=True)
        if image_data is not None:
            pixel_data = numpy.asarray(image_data)
            if not simple_dct:
                dct = scipy.fftpack.dct(scipy.fftpack.dct(pixel_data, axis=0), axis=1)
                dct_lowfreq = dct[:hash_size, :hash_size]
                dct_median  = numpy.median(dct_lowfreq)
                image_dct   = dct_lowfreq > dct_median
            else:
                dct = scipy.fftpack.dct(pixel_data)
                dct_lowfreq = dct[:hash_size, 1:hash_size+1]
                dct_average = dct_lowfreq.mean()
                image_dct   = dct_lowfreq > dct_average
            pixel_bits = ['1' if b else '0' for b in image_dct.flatten()]
            if not output_hex:
                return ''.join(pixel_bits)
            else:
                return hexxer(pixel_bits)
        else:
            return None

# LAZY IMPLEMENTATION
def phash_numpy(numpy_array, hash_size=8, **options):
    simple_dct = options.pop('simple', False)
    output_hex = options.pop('hex', False)
    if not simple_dct:
        dct = scipy.fftpack.dct(scipy.fftpack.dct(numpy_array, axis=0), axis=1)
        dct_lowfreq = dct[:hash_size, :hash_size]
        dct_median  = numpy.median(dct_lowfreq)
        dct_calc    = dct_lowfreq > dct_median
    else:
        dct = scipy.fftpack.dct(numpy_array)
        dct_lowfreq = dct[:hash_size, 1:hash_size+1]
        dct_average = dct_lowfreq.mean()
        dct_calc    = dct_lowfreq > dct_average
    pixel_bits = ['1' if b else '0' for b in dct_calc.flatten()]
    if not output_hex:
        return ''.join(pixel_bits)
    else:
        return hexxer(pixel_bits)

def dhash_flat(flat_array, hash_dimensions=(9,8), **options):
    output_hex = options.pop('hex', False)
    hash_cols, hash_rows = hash_dimensions[0], hash_dimensions[1]
    gradient_bits = []
    for row in range(hash_rows):
        row_start_index = row
        # Because it was compared rightward, last pixel on the right is ignored, as such resize_width - 1
        for col in range(hash_cols - 1):
            left_bit_index = row_start_index + col
            if flat_array[left_bit_index] \
            > flat_array[left_bit_index + 1]:
                gradient_bits.append('1')
            else:
                gradient_bits.append('0')
    if not output_hex:
        return ''.join(gradient_bits)
    else:
        return hexxer(gradient_bits)

def get_image_data(imgpath, resample=(8,8), **options):
    aspil_image = options.pop('pil', False)
    try:
        with Image.open(imgpath) as imgopen:
            imgdata = imgopen.resize(
                resample, Image.ANTIALIAS
            ).convert('L')
        if aspil_image:
            return imgdata
        else:
            return list(imgdata.getdata())
    except Exception as excp:
        print(excp)
        return None

# WRAPPER FUNCTIONS
def image_collection_hash(image_list, **options):
    hash_type = options.pop('type', 'phash')
    hash_file = options.pop('out', None)
    output_hex= options.pop('hex', False)
    hash_file = os.getcwd().rsplit(os.sep, 1)[1] + "-hash.json" \
        if hash_file is None \
        else hash_file
    img_res = (9,8) if hash_type == 'dhash' else (32,32)
    img_pil = False if hash_type == 'dhash' else True
    hash_collection = {
        'src' : 'ImageCollection',
        'uniq': None, 
        'type': hash_type, 
        'hex' : output_hex, 
        'imagesize': '%sx%s' % img_res,
        'hash_size': 8,
        'high_freq': 4,
        'hash': {}
    }
    for image_file in image_list:
        print_log('info', 'HASHING: "%s"', image_file)
        pixel_data = get_image_data(image_file, img_res, pil=img_pil)
        if hash_type == 'dhash':
            hash_value = dhash_flat(pixel_data, img_res, hex=output_hex)
        else:
            hash_value = phash_numpy(
                numpy.asarray(pixel_data), 
                hash_size=8, 
                hex=output_hex)
        hash_collection['hash'][image_file] = hash_value
    with open(hash_file, 'w+') as out_file:
        json.dump(hash_collection, out_file, indent=4)

# Create test screenshot: ffmpeg -i reld.mp4 -vf fps=1/60 cap-%03d.jpg
# Based off Marcan script, but uses scipy.fftpack.dct instead
def video_frame_hash(source_file, **options):
    import sys, numpy, ffms, math
    hash_type = options.pop('type', 'phash')
    hash_file = options.pop('out', None)
    output_hex= options.pop('hex', False)
    output_uniq= options.pop('uniq', False)
    output_cap = options.pop('cap', None)
    hash_file = source_file + "-hash.json" if hash_file is None else hash_file

    high_freq = 4
    hash_size = 8
    hash_resolution = hash_size * high_freq
    uniq_frames = set([])
    hash_json   = {
        'src' : source_file, 
        'uniq': output_uniq, 
        'hex' : output_hex, 
        'type': hash_type,
        'imagesize': '{0}x{0}'.format(hash_resolution),
        'hash_size': hash_size,
        'high_freq': high_freq,
    }
    hash_frames = {}
    print("Loading", source_file)
    if output_cap is not None:
        vsource_cap = ffms.VideoSource(source_file)
        #https://github.com/FFmpeg/FFmpeg/blob/master/libavutil/pixfmt.h#L237-L240
        vsource_cap.set_output_format([ffms.get_pix_fmt("rgb0")])
        # Full color, alpha channel is 0
    else:
        vsource_cap = None
    vsource = ffms.VideoSource(source_file)
    vsource.set_output_format(
        [ffms.get_pix_fmt("gray")], 
        width=hash_resolution, 
        height=hash_resolution
    )
    print("Hashing", source_file)

    for frameno in range(vsource.properties.NumFrames):
        # This is a numpy array? yes, 
        frame_data = vsource.get_frame(frameno).planes[0]
        # one dimension (flattened), len=M*M numpy array
        #print(type(frame_data), len(frame_data), str(frame_data)); exit()
        pixel_data = numpy.asarray(
            frame_data.reshape(
                (hash_resolution, hash_resolution)
            )
        )
        # Is a MxM 2D array? yes, also in grayscaled value
        #print(type(pixel_data), len(pixel_data), str(pixel_data))
        #img_data = toimage(pixel_data, mode='L')
        #img_data.save('screencap/my.png'); exit()
        #if hash_type == 'dhash':
        #    hash_string = dhash_numpy(pixel_data, hex=output_hex)
        #else:
        hash_string = phash_numpy(pixel_data, hash_size, hex=output_hex)

        if hash_string in uniq_frames:
            dump_file = False if output_uniq else True
        else:
            uniq_frames.add(hash_string)
            dump_file = True
            if vsource_cap is not None:
                cap_data = vsource_cap.get_frame(frameno)
                cap_dimensions = (
                    cap_data.EncodedHeight, 
                    cap_data.EncodedWidth, 
                    4
                )
                #https://docs.scipy.org/doc/scipy-0.19.1/reference/generated/scipy.misc.toimage.html
                #https://github.com/scipy/scipy/blob/v0.19.1/scipy/misc/pilutil.py#L131-L138
                screen_cap = toimage(
                    cap_data.planes[0].reshape(cap_dimensions), 
                    mode='RGBA'
                )
                print('Capping Uniq Frame:', frameno, cap_dimensions)
                screen_cap.save(
                    os.path.join(
                        output_cap, 
                        'frame-%s.png' % str(frameno).zfill(4)
                    )
                )
            else:
                pass
        if dump_file:
            if output_hex:
                hash_frames[frameno] = hash_string
            else:
                if hash_string.count('1') == 0 \
                or hash_string.count('0') == 0:
                    pass
                else:
                    hash_frames[frameno] = hash_string
        else:
            pass
    if len(hash_frames.keys()) > 0:
        hash_json['hash'] = hash_frames
        with open(hash_file, 'w+') as out_file:
            json.dump(hash_json, out_file, indent=4)
    else:
        pass
    return hash_json

# http://www.marcansoft.com/paste/czgaGc7a.txt
# returns hex, might not be compatible with myown implementations
def video_frame_hash_marcan(video_file, hash_file):
    import sys, numpy, ffms, math

    N = 32 # image size
    M = 8 # number of DCT coefficients

    k = math.sqrt(2.0 / N)
    dct_k = numpy.matrix([
        [k * math.cos((math.pi / 2 / N) * y * (2 * x + 1)) for x in range(N)]
        for y in range(1,M)
    ])
    dct_k_t = numpy.transpose(dct_k)

    print("Loading", video_file)
    vsource = ffms.VideoSource(video_file)
    vsource.set_output_format([ffms.get_pix_fmt("gray")], width=N, height=N)

    print("Hashing", video_file)
    with open(hash_file, 'w+') as out_file:
        for frameno in range(vsource.properties.NumFrames):
            # written for python 2.7, python3 needs no astype(float)
            data = vsource.get_frame(frameno).planes[0].reshape((N,N)) #.astype(float)
            coefs = numpy.array(dct_k * data * dct_k_t).flatten()
            median = numpy.median(coefs)
            h = sum((1<<i) for i,j in enumerate(coefs) if j > median)
            out_file.write("#%d: %016x\n" % (frameno, h))

# READ IMAGE AGAINST HASH STRING
def image_against_hash(image_path, calculated_hash, **options):
    match_percent = options.pop('percent', False)
    if os.path.isfile(image_path):
        ihash = image_hash(image_path)
        if match_percent:
            d_hash = hamming_distance(ihash.dhash(), calculated_hash, percent=True)
            d_match= True if d_hash >= 90 else False
        else:
            d_hash = hamming_distance(ihash.dhash(), calculated_hash)
            d_match= True if d_hash <= 5 else False
        if d_match:
            print_log(
                'debug', 
                'IMAGE Gradient Match %s [%s]: "%s"', 
                d_match, 
                '%s%%' % d_hash if match_percent else d_hash, 
                image_path
            )
            if match_percent:
                p_hash = hamming_distance(ihash.phash(), calculated_hash, percent=True)
                p_match= True if p_hash >= 90 else False
            else:
                p_hash = hamming_distance(ihash.phash(), calculated_hash)
                p_match= True if p_hash <= 5 else False
            if p_match:
                print_log(
                    'debug', 
                    'IMAGE DCT Match %s [%s]: "%s"', 
                    p_match, 
                    '%s%%' % p_hash if match_percent else p_hash, 
                    image_path, 
                )
                return True
            else:
                print_log(
                    'warn', 
                    'IMAGE DCT Mis-match %s [%s]: "%s"', 
                    p_match, 
                    '%s%%' % p_hash if match_percent else p_hash, 
                    image_path, 
                )
                return False
        else:
            print_log(
                'debug', 
                'IMAGE Gradient Mis-match [%s]: "%s"', 
                '%s%%' % d_hash if match_percent else d_hash, 
                image_path
            )
            return False
    else:
        print_log(
            'error', 
            'IMAGE Missing: "%s"', 
            image_path
        )
        return False

# READ 2 IMAGE AND COMPARE AGAINST EACH OTHER
def image_match(image_1, image_2, **options):
    match_percent = options.pop('percent', False)
    e1, e2 = os.path.isfile(image_1), os.path.isfile(image_2)
    if e1 and e2:
        i1, i2 = image_hash(image_1), image_hash(image_2)
        if match_percent:
            d_hash = hamming_distance(i1.dhash(), i2.dhash(), percent=True)
            d_match= True if d_hash >= 90 else False
        else:
            d_hash = hamming_distance(i1.dhash(), i2.dhash())
            d_match= True if d_hash <= 5 else False
        if d_match:
            print_log(
                'debug', 
                'IMAGE Gradient Match %s [%s]: "%s" === "%s" ', 
                d_match, 
                '%s%%' % d_hash if match_percent else d_hash, 
                image_1, 
                image_2
            )
            if match_percent:
                p_hash = hamming_distance(i1.phash(), i2.phash(), percent=True)
                p_match= True if p_hash >= 90 else False
            else:
                p_hash = hamming_distance(i1.phash(), i2.phash())
                p_match= True if p_hash <= 5 else False
            if p_match:
                print_log(
                    'debug', 
                    'IMAGE DCT Match %s [%s]: "%s" === "%s" ', 
                    p_match, 
                    '%s%%' % p_hash if match_percent else p_hash, 
                    image_1, 
                    image_2
                )
                return True
            else:
                print_log(
                    'warn', 
                    'IMAGE DCT Mis-match %s [%s]: "%s" =/= "%s" ', 
                    p_match, 
                    '%s%%' % p_hash if match_percent else p_hash, 
                    image_1, 
                    image_2
                )
                return False
        else:
            print_log(
                'debug', 
                'IMAGE Gradient Mis-match [%s]: "%s" =/= "%s" ', 
                '%s%%' % d_hash if match_percent else d_hash, 
                image_1, 
                image_2
            )
            return False
    else:
        print_log(
            'error', 
            'IMAGE Exists: "%s" [%s] / "%s" [%s]', 
            image_1, e1, 
            image_2, e2
        )
        return False
