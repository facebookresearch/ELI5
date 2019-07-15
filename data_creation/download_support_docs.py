import argparse
import json
import subprocess
import os

from os.path import join as pjoin
from os.path import isfile
from os.path import isdir
from subprocess import check_output
from time import time

from data_utils import *

def main():
    parser  = argparse.ArgumentParser(description='select support document pages from common crawl')
    parser.add_argument('-nw', '--slsize', default=716, type=int, metavar='N',
                        help='number of wet files in a slice')
    parser.add_argument('-ns', '--slnum', default=0, type=int, metavar='N',
                        help='commoncrawl slice number [0, ..., 71520 / args.slsize]')
    parser.add_argument('-wf', '--wet_urls', default='pre_computed/wet.paths', type=str,
                        help='path to file containing WET file URLs')
    parser.add_argument('-sr_l', '--subreddit_names', default='["explainlikeimfive", "askscience", "AskHistorians"]', type=str,
                        help='subreddit names')
    parser.add_argument('-nu', '--n_urls', default=100, type=int, metavar='N',
                        help='number of support documents to gather for each example')
    parser.add_argument('-sfq', '--save_freq', default=100, type=int, metavar='N',
                        help='how often are results written to file')
    parser.add_argument('-o', '--output_dir', default='processed_data/collected_docs', type=str,
                        help='where to save the output')
    args    = parser.parse_args()
    # parse full list of wet urls
    # slice urls for WET files can be found at https://commoncrawl.org/2018/08/august-2018-crawl-archive-now-available/
    # $ wget https://commoncrawl.s3.amazonaws.com/crawl-data/CC-MAIN-2018-34/wet.paths.gz
    # $ gunzip wet.paths.gz
    f       = open(args.wet_urls, buffering=4096)
    url_lst = [line.strip() for line in f]
    f.close()
    print("loading URL selection")
    ccrawl_ids_maps = {}
    sr_names        = json.loads(args.subreddit_names)
    for name in sr_names:
        print(name)
        ccrawl_ids_maps[name]   = json.load(open('pre_computed/%s_ccrawl_ids.json' % (name,)))
    # make a list of the CommonCrawl UIDs we want to process and keep
    select_ccid = make_ccid_filter(ccrawl_ids_maps, args.n_urls)
    print("loaded URL selection")
    # organize directories
    if not isdir(args.output_dir):
        subprocess.run(['mkdir', args.output_dir], stdout=subprocess.PIPE)
        if not isdir(pjoin(args.output_dir, 'tmp')):
            subprocess.run(['mkdir', pjoin(args.output_dir, 'tmp')], stdout=subprocess.PIPE)
    for name in sr_names:
        if not isdir(pjoin(args.output_dir, name)):
            subprocess.run(['mkdir', pjoin(args.output_dir, name)], stdout=subprocess.PIPE)
    # Download and parse slice of args.slsize WET files
    st_time     = time()
    articles    = dict([(name, {}) for name in sr_names])
    for i in range(args.slnum * args.slsize, (args.slnum + 1) * args.slsize):
        # Download wet file from amazon AWS
        dl_time = time()
        fname   = url_lst[i].split('/')[-1][:-3]
        # download and unzip if necessary
        fpath   = pjoin(args.output_dir, 'tmp', fname)
        print("processing", fpath)
        if not isfile(fpath):
            ct_try  = 0
            while not isfile(fpath):
                resp_c      = subprocess.run(['rm', fpath + ".gz"], stdout=subprocess.PIPE)
                while not isfile(fpath + ".gz"):
                    url     = "https://commoncrawl.s3.amazonaws.com/" + url_lst[i]
                    resp_a  = subprocess.run(['wget', '-P', pjoin(args.output_dir, 'tmp'), url], stdout=subprocess.PIPE)
                    print("download:", time() - dl_time)
                    ct_try  += 1
                    if ct_try > 5 and not isfile(fpath + ".gz"):
                        print("giving up on file", fname)
                        break
                downloaded  = isfile(fpath + ".gz")
                if downloaded:
                    resp_b  = subprocess.run(['gunzip', fpath + ".gz"], stdout=subprocess.PIPE)
                    print("download and gunzip:", time() - dl_time)
                if ct_try > 5 and not isfile(fpath):
                    print("giving up on file", fname)
                    break
        else:
            downloaded = isfile(fpath)
        if not downloaded:
            print("FAILED DOWNLOADING ", fpath)
            continue
        # Extract, tokenize, and filter articles by language
        f = open(fpath, buffering=4096)
        article_url = ''
        article_id  = ''
        article_txt = ''
        last_line   = ''
        read_text   = False
        ct          = 0
        start_time = time()
        ccid_path_tuple = False
        for line in f:
            if line.startswith("WARC/1.0"):
                if ccid_path_tuple:
                    ct += 1
                    article     = {'ccid': article_id,
                                   'url' : article_url,
                                   'text': word_url_tokenize(article_txt)}
                    name, eli_k, num            = ccid_path_tuple
                    articles[name][eli_k[:2]]   = articles[name].get(eli_k[:2], [])
                    articles[name][eli_k[:2]]   += [(eli_k, num, article)]
                article_txt = ''
                read_text   = False
            if line.startswith("WARC-Target-URI"):
                try:
                    article_url     = line.strip().split()[-1]
                except:
                    article_url     = '<UNK>'
            if line.startswith("WARC-Record-ID"):
                try:
                    article_id      = line.strip().split()[-1]
                    ccid_path_tuple = select_ccid.get(article_id, False)
                except:
                    article_id      = '<UNK>'
                    ccid_path_tuple = False
            if read_text and (last_line.strip() + line.strip()) != '':
                article_txt += line + '\n'
                last_line   = line
            if line.startswith("Content-Length: ") and ccid_path_tuple:
                read_text   = True
        if ccid_path_tuple:
            ct += 1
            article     = {'ccid': article_id,
                           'url' : article_url,
                           'text': word_url_tokenize(article_txt)}
            name, eli_k, num            = ccid_path_tuple
            articles[name][eli_k[:2]]   = articles[name].get(eli_k[:2], [])
            articles[name][eli_k[:2]]   += [(eli_k, num, article)]
        f.close()
        print(">>>>>>>>>> ARTICLES FOUND %d in %.2f" % (ct, time() - start_time))
        if i % args.save_freq == args.save_freq - 1:
            for name, elik_maps in articles.items():
                print('saving', name, i, len(elik_maps))
                for st, ls in elik_maps.items():
                    d_name  = pjoin(args.output_dir, name, st)
                    if not isdir(d_name):
                        subprocess.run(['mkdir', d_name], stdout=subprocess.PIPE)
                    json.dump(ls, open(pjoin(d_name, "docs_slice_%05d.json" % (args.slnum)), 'w'))
            print('saved json files %.2f' % (time() - start_time,))
        resp_c      = subprocess.run(['rm', fpath], stdout=subprocess.PIPE)
    print('final save')
    for name, elik_maps in articles.items():
        print('saving', name, i, len(elik_maps))
        for st, ls in elik_maps.items():
            d_name  = pjoin(args.output_dir, name, st)
            if not isdir(d_name):
                subprocess.run(['mkdir', d_name], stdout=subprocess.PIPE)
            json.dump(ls, open(pjoin(d_name, "docs_slice_%05d.json" % (args.slnum)), 'w'))
    print('saved json files %.2f' % (time() - start_time,))
    print("processing slice %d took %f seconds" % (i, time() - st_time))


if __name__ == '__main__':
    main()
