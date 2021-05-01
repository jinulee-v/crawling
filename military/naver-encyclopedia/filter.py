import argparse
import re
import string

discards = [
  ': ',
  '변형 및 파생기종',
  '이미지 크게보기',
  "item_alt",
  "original_image",
  '요약 '
]

def discard_check(sent):
  for discard in discards:
    if discard in sent:
      return True
  return False

def filter(args):
  with open(args.src_path, 'r', encoding='utf-8') as file:
    data = file.read().splitlines()
  data = [re.sub('<.*>', '', line) for line in data]
  data = [line.replace(' .', '.') for line in data]
  data = [line.replace('●|·', '\t') for line in data]
  data = [re.sub('([^A-Za-z0-9]+?)\. ([^A-Za-z0-9]+?)', '\g<1>.\t\g<2>', line) for line in data]
  data = [re.sub('([A-Za-z0-9]{2,}?)\. ([^A-Za-z0-9]+?)', '\g<1>.\t\g<2>', line) for line in data]
  data = [re.sub('([^A-Za-z0-9]+?)\. ([A-Za-z0-9]+?)', '\g<1>.\t\g<2>', line) for line in data]
  data = [line.split('\t')[2:] for line in data]
  
  result = set()
  for line in data:
    for sent in line:
      if discard_check(sent):
        continue
      if not sent:
        continue
      if not sent[-1] in string.punctuation.replace(')', ''):
        continue
      sent = re.sub('SE[A-Z_0-9\-]*', '', sent.replace('{', '').replace('}', '').replace('$', ''))
      sent = re.sub('\s+', ' ', sent).strip()
      if len(sent.split()) <= 2 or len(sent.split()) >= 50:
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