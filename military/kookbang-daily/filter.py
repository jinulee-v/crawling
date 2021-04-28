import argparse

from tqdm import tqdm

jong_arr	= ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

def filter(args):
  with open(args.src_path, 'r', encoding='utf-8') as file:
    data = file.read().splitlines()
  data = [line.split('\t') for line in data]
  
  for line in data:
    for i in range(len(line)):
      if ' 기자' in line[i]:
        del line[i:]
        break
  data = ['\t'.join(line) for line in data]

  with open(args.dst_path, 'w', encoding='UTF-8') as file:
    file.write('\n'.join(data)+'\n')

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--src-path', type=str, default='data/crawl.tsv', help='Path of raw crawled results')
  parser.add_argument('--dst-path', type=str, default='data/crawl.tsv', help='Path to store filtered crawl results')
  args = parser.parse_args()

  filter(args)