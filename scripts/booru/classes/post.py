#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, json
from collections import namedtuple
from classes.utils import merge_two_dicts, gen_viewid
from helpers.str_helper import string_sanitizer, urlPrefixer
from browsers.scrapers import lxml_spider

class page():
    def __init__(self, mech_browser, **post_options):
        self.browser    = mech_browser
        self.xpath_sample = post_options.get('sample', None)
        self.xpath_full   = post_options.get('full', None)
        self.xpath_source = post_options.get('source_link', None)
        self.xpath_artist = post_options.get('artist', None)
        self.xpath_series = post_options.get('series', None)
        self.xpath_charas = post_options.get('charas', None)
        self.xpath_general= post_options.get('general', None)
        self.download_lq  = post_options.get('lq', False)
        self.post_onetag  = post_options.get('onetag', True)
        self._strornull = lambda x: None if x is None or len(x) == 0 else x[0]
        self._get_urlfile = lambda x: x.rsplit('/',1)[1].rsplit('_',1)[1] \
            if '/__' in x else x.rsplit('/',1)[1]

    def gen_mvptag(self, tags_pairs, **options):
        tags_return = namedtuple('TagsMVP', ['mvp', 'all'])
        if len(tags_pairs) == 0:
            return tags_return(mvp = None, all = [])
        else:
            zip_tag = lambda x, y, z: x[y][0] if len(x[y]) > 0 else z
            tag_all = set([])
            tag_mvp, tag_max = None, 0
            for tag_dict in tags_pairs:
                # print (tag_dict)
                tag_name = string_sanitizer(
                        zip_tag(
                        tag_dict, 'text_name', 'tagme'
                    ).replace(' ', '_'), 
                    paranoia = True
                )
                tag_info = zip_tag(tag_dict, 'text_count', '0')
                if 'k' in tag_info.lower():
                    tag_count = int(float(tag_info.strip('k')) * 1000)
                else:
                    tag_count = int(tag_info) \
                        if tag_info.isdigit() else 0
                if tag_count > tag_max or tag_mvp is None:
                    tag_mvp, tag_max = tag_name, tag_count
                else:
                    pass
                tag_all.add(tag_name)
            return tags_return(
                mvp = tag_mvp if tag_mvp is not None else 'tagme', 
                all = tag_all
            )

    def list_tags(self, postspider, **options):
        post_tags = namedtuple(
            'PostTags', [
                'artist', 'artists', 
                'character', 'characters', 
                'serie', 'series', 
                'general'
            ]
        )
        # print (self.xpath_artist)
        post_tags_getpairs = lambda x: postspider.scraper(**x)['pair'] \
            if x is not None else []
        post_tags_artist = self.gen_mvptag(
            post_tags_getpairs(self.xpath_artist))
        post_tags_series = self.gen_mvptag(
            post_tags_getpairs(self.xpath_series))
        post_tags_charas = self.gen_mvptag(
            post_tags_getpairs(self.xpath_charas))
        post_tags_general= self.gen_mvptag(
            post_tags_getpairs(self.xpath_general))
        return post_tags(
            artist = post_tags_artist.mvp, 
            artists= post_tags_artist.all,
            character = post_tags_charas.mvp, 
            characters= post_tags_charas.all, 
            serie = post_tags_series.mvp, 
            series= post_tags_series.all, 
            general = post_tags_general.all, 
        )

    def get_image(self, image_src, image_dst, **options):
        return None

    def uniq_img(self, img_list):
        uniq_files = set([])
        uniq_links = []
        for x in img_list:
            img_file = self._get_urlfile(x)
            if img_file not in uniq_files and x not in uniq_links:
                uniq_files.add(x)
                uniq_links.append(x)
            else:
                pass
        return uniq_links if len(uniq_links) > 0 else img_list

    def get(self, post_url, **post_infos):
        # dry_run = post_infos.pop('dryrun', False)
        post_html   = self.browser.read(post_url)
        if post_html is not None:
            postspider  = lxml_spider(post_html)
            post_id     = post_infos.get('id', gen_viewid(post_url))
            post_full   = postspider.scraper(auto_link=self.xpath_full)['auto_link']
            post_sample = postspider.scraper(auto_link=self.xpath_sample)['auto_link']
            post_tags   = self.list_tags(postspider)
            post_source = self._strornull(postspider.scraper(href=self.xpath_source)['href'])

            # print ('\n', post_id, '\n', post_full, '\n', post_sample, '\n', post_tags)
            file_prefix = ''
            for tag_txt in [post_tags.artist, post_tags.serie, post_tags.character]:
                if tag_txt is not None and tag_txt not in file_prefix:
                    file_prefix = ('%s %s' % (file_prefix, tag_txt)).strip()
                else:
                    pass
            if self.download_lq or len(post_full) == 0:
                post_images = self.uniq_img(post_sample)
            else:
                post_images = self.uniq_img(post_full)
            # print (post_images)
            post_data = []
            if len(post_full) == 0:
                return post_data
            else:
                for image_src in post_images:
                    image_url = urlPrefixer(image_src, post_url)
                    image_file= self._get_urlfile(image_src)
                    image_name, image_ext = image_file.rsplit('.', 1) \
                        if '.' in image_file \
                        else [image_file, 'bin']
                    # print (image_file, image_name, image_ext)
                    if post_id in image_file or post_id == 'null':
                        image_saveas = '{name}.{ext}'.format(
                            name = string_sanitizer(image_name, urldecode=True, paranoia=True), 
                            ext = image_ext
                        ).strip()
                    else:
                        image_saveas = '{prefix} {id}_{name}.{ext}'.format(
                            prefix = file_prefix, 
                            id = post_id, 
                            name = string_sanitizer(image_name, urldecode=True, paranoia=True), 
                            ext = image_ext
                        ).strip()
                    # print (image_url, image_saveas)
                    image_info = namedtuple('PostImage', ['src', 'file', 'source'])
                    post_data.append(image_info(src=image_url, file=image_saveas, source=post_source))
                return post_data
        else:
            return None



