#!/usr/bin/env python
# -*- coding: utf-8 -*-



import sys
from os import path, listdir, remove, rmdir, rename, walk, getcwd, sep
from PIL import Image, ImageChops
from helpers.class_filevrf import FileVerifier
from helpers.module_utility_functions import print_log, utf2str, str2utf

class PillowImageEditor():
    def __init__(self, **kargs):
        self.accept_types = { 'BMP': '.bmp', 'JPEG': '.jpg', 'SVG': '.svg', 'PNG': '.png', 'GIF': '.gif', 'TIFF': '.tiff' }
        self.delete_original = kargs['mogrify'] if isinstance(kargs['mogrify'], bool) else True
        self.compression_quality = kargs['quality'] if 'quality' in list(kargs.keys()) \
                                   and str(kargs['quality']).isdigit() \
                                   else 90
        self.compression_optimize = kargs['optimize'] if 'optimize' in list(kargs.keys()) \
                                    and isinstance(kargs['optimize'], bool) \
                                    else True
        self.conversion_mode = {'L': 'monochrome','RGB': 'color'}
        self.default_size = (0,1800)
        
    def Compress(self, img_path, **kargs):
        with Image.open(img_path) as iopend:
            try:
                if self.delete_original: iopend.save(img_path,
                                                     quality=self.compression_quality, 
                                                     optimize=self.compression_optimize)
                else: iopend.save('%s_lq.%s' % tuple(str2utf(img_path).rsplit('.',1)), 
                                  quality=self.compression_quality,
                                  optimize=self.compression_optimize)
            except:
                print_log('err', 'IMG_COMPRESS - PATH="%s" to "%s%%"', img_path, self.compression_quality)
                raise
        
    def Convert(self, img_path, **kargs):
        iformat = kargs['format'] if 'format' in list(kargs.keys()) and \
                                    any(kargs['format']==f for \
                                        f in list(self.accept_types.keys())) \
                                  else 'JPEG'
        imode   = kargs['mode'] if 'mode' in list(kargs.keys()) and \
                                    any(kargs['mode']==m for \
                                        m in list(self.conversion_mode.keys())) \
                                else 'RGB'
        ipath_noext = str2utf(img_path).rsplit('.',1)[0]
        if iformat not in list(self.accept_types.keys()):
            print_log('err', 'IMG_CONVERT - PATH="%s" to Un-Supported "%s" file type', img_path, iformat)
            raise Exception('Un-Supported "%s" file type, Try one of the listed below:\n%s' % (iformat, list(self.accept_types.keys())))
        else:
            with Image.open(img_path) as iopend:
                if iopend.format == iformat:
                    print_log('warn', 'IMG_CONVERT - PATH="%s" detected="%s" request="%s" same file type', img_path, iopend.format, iformat)
                    img_after = img_path
                    pass
                else:
                    try:
                        img_after = ipath_noext + self.accept_types[iformat]
                        if path.isfile(img_after):
                            img_after = ipath_noext + '_coverted_to' + self.accept_types[iformat]
                        else:
                            pass
                        if path.isfile(img_after):
                            print_log('warn', 'IMG_CONVERT - SKIP Covert to PATH="%s" already exists.', img_after)
                        else:
                            iopend.convert(imode).save(img_after, iformat, 
                                                       quality=self.compression_quality)
                        print_log('ok', 'IMG_CONVERT - PATH="%s" detected="%s" request="%s"', img_path, iopend.format, iformat)
                    except:
                        print_log('err', 'IMG_CONVERT - PATH="%s" to "%s"', img_path, iformat)
                        raise
                    if self.delete_original: remove(img_path)
            return img_after
                    
    def Resize(self, img_path, **kargs):
        if 'size' in list(kargs.keys()):
            if 'x' in kargs['size']:
                new_size = kargs['size'].split('x')
                new_width = int(new_size[0]) if len(new_size[0]) > 0 else 0
                new_height = int(new_size[-1]) if len(new_size[-1]) > 0 else 0
            else:
                new_width = int(kargs['size'])
                new_height = 0
        else:
            new_width, new_height = self.default_size
        
        with Image.open(img_path) as iopend:
            orig_width, orig_height = iopend.size
            if new_width == 0: auto_scale = new_height / orig_height
            elif new_height == 0: auto_scale = new_width / orig_width
            else: auto_scale = min(new_height / orig_height, new_width / orig_width)
            resize2_width = int(round(orig_width * auto_scale))
            resize2_height = int(round(orig_height * auto_scale))
            if auto_scale >= 1:
                print_log('warn', 'IMG_RESIZE - PATH="%s" old=%s < new=%s SKIP as Upscale is NOT recommended', img_path, (orig_width,orig_height), (resize2_width,resize2_height))
                pass
            else:
                try:
                    iopend.thumbnail((resize2_width,resize2_height), Image.ANTIALIAS)
                    if self.delete_original: 
                        iopend.save(img_path, quality=self.compression_quality)
                    else:
                        iopend.save('%s_resized.%s' % tuple(str2utf(img_path).rsplit('.',1)), 
                                    quality=self.compression_quality)
                    print_log('ok', 'IMG_RESIZE - PATH="%s" old=%s to new=%s', img_path, (orig_width,orig_height), (resize2_width,resize2_height))
                except:
                    print_log('err', 'IMG_RESIZE - PATH="%s" current=%s', img_path, (orig_width,orig_height))
                    raise
                #if self.delete_original: remove(img_path)
    
    def Trim(self, img_path, **kargs):
        color_pallete_rgb = {'white': (255,255,255),
                             'black': (0,0,0)}
        color_pallete_l   = {'white': 255, 'black': 0}
        fuzz = -(int(kargs['fuzz'])/100*255) if 'fuzz' in list(kargs.keys()) \
                                             and str(kargs['fuzz']).isdigit() else -100 # ~45%
        scale= float(int(kargs['scale'])) if 'scale' in list(kargs.keys()) \
                       and str(kargs['scale']).isdigit() else 2.0
        with Image.open(img_path) as iopend:
            if 'border' in list(kargs.keys()) and str(kargs['border']) in list(color_pallete_rgb.keys()):
                if iopend.mode == 'L': 
                    border_color = color_pallete_l[kargs['border']]
                elif iopend.mode == 'RGB': 
                    border_color = color_pallete_rgb[kargs['border']]
                else:
                    border_color = iopend.getpixel((0,0))
            else:
                if 'border' in list(kargs.keys()) and isinstance(kargs['border'], tuple):
                    border_color = kargs['border']
                else:
                    border_color = iopend.getpixel((0,0))
            #print iopend.mode, iopend.size, border_color
            icanvas = Image.new(iopend.mode, iopend.size, border_color)
            idiff = ImageChops.difference(iopend, icanvas)
            idiff = ImageChops.add(idiff, idiff, scale, fuzz)
            bbox = idiff.getbbox()
            if bbox: iopend.crop(bbox).save(img_path)
            else: print_log('debug', 'IMG_TRIM - PATH="%s" CropZone=%s OrigSize=%s', img_path, bbox, iopend.size)
        return {'trimmed': border_color, 
                'reverse': tuple([255 if max(n,100) == 100 else 0 for n in border_color]) if isinstance(border_color, tuple) else border_color}
                
    def Tessy(self, img_path, **kargs):
        pass