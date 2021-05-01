import argparse
import re

from tqdm import tqdm

discards = [
  '이력',
  '관련 항목',
  '가족',
  '각주',
  '외부 링크'
]

def discard_check(sent):
  for discard in discards:
    if '== ' + discard + ' ==' in sent:
      return True
  return False


def filter(args):
  with open(args.src_path, 'r', encoding='utf-8') as file:
    data = file.read().splitlines()
  data = [re.sub('([^A-Za-z0-9]+?)\.|\?|!\s*?([^A-Za-z0-9]+?)', '\g<1>.\t\g<2>', line) for line in data]
  data = [re.sub('([A-Za-z0-9]{2,}?)\.|\?|!\s*?([^A-Za-z0-9]+?)', '\g<1>.\t\g<2>', line) for line in data]
  data = [re.sub('([^A-Za-z0-9]+?)\.|\?|!\s*?([A-Za-z0-9]+?)', '\g<1>.\t\g<2>', line) for line in data]
  data = [line.split('\t')[1:] for line in data]

  result = set()

  for line in data:
    if len(line) == 0:
      continue
    for sent in line:
      if discard_check(sent):
        continue
      sent = re.sub(r'== .* ==', '', sent).replace('=', '').strip()
      sent = re.sub(r'\(.{5,}\)', '', sent).strip()
      if len(sent.split()) <= 3:
        continue
      if not re.match('.*?[\u3131-\u314e|\u314f-\u3163|\uac00-\ud7a3]', sent):
        continue
      result.add(sent)
  

  with open(args.dst_path, 'w', encoding='UTF-8') as file:
    file.write('\n'.join(list(result))+'\n')


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--src-path', type=str, default='data/crawl.tsv', help='Path of raw crawled results')
  parser.add_argument('--dst-path', type=str, default='data/sentences.txt', help='Path to store filtered crawl results')
  args = parser.parse_args()

  filter(args)