import argparse
import re

from tqdm import tqdm

def filter(args):
  with open(args.src_path, 'r', encoding='utf-8') as file:
    data = file.read().splitlines()
  data = [re.sub('([^A-Za-z0-9]+?)\. ', '\g<1>.\t', re.sub(r'\s{5,}', '\t', line)).split('\t')[1:] for line in data]
  
  for line in data:
    for i in range(len(line)):
      if ' 기자' in line[i] or '< 저작권자 ⓒ 국방일보, 무단전재 및 재배포 금지 >' in line[i] or '★오늘의 국방일보' in line[i]:
        del line[i:]
        break
  
  data = ['\n'.join(line) for line in data if len(line) > 2]

  with open(args.dst_path, 'w', encoding='UTF-8') as file:
    file.write('\n'.join(data)+'\n')

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--src-path', type=str, default='data/crawl.tsv', help='Path of raw crawled results')
  parser.add_argument('--dst-path', type=str, default='data/sentences.txt', help='Path to store filtered crawl results')
  args = parser.parse_args()

  filter(args)