import argparse
import re

def filter(args):
  with open(args.src_path, 'r', encoding='utf-8') as file:
    data = file.read().splitlines()
  data = [line.split('\t') for line in data]
  
  for line in data:
    for i in range(len(line)):
      line[i] = re.sub('SE[A-Z_0-9\-]*', '', line[i].replace('{', '').replace('}', '').replace('$', '')).strip()
      line[i] = re.sub('\s+', ' ', line[i])

  data = ['\t'.join([sent for sent in line if len(sent)>3]) for line in data if len(line) > 3]

  with open(args.dst_path, 'w', encoding='UTF-8') as file:
    file.write('\n'.join(data)+'\n')

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--src-path', type=str, default='data/crawl.tsv', help='Path of raw crawled results')
  parser.add_argument('--dst-path', type=str, default='data/crawl.tsv', help='Path to store filtered crawl results')
  args = parser.parse_args()

  filter(args)