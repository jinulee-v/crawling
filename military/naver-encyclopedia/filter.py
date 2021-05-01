import argparse
import re
import string

discards = [
  '이미지 크게보기', '제작국가 ', '제작·판매 ', '구분 ', '제원정보 ',
  '개발 국가 ', '개발 연도 ', '구경 ', '작동방식', '무게 ', '전체 길이 ', '총열 길이 ', '총구(포구) 속도 ', '탄창 ', '사정거리  15m ', '개발연도  총기명 ',
  '이전 이미지 ', '원본보기', '다음 이미지', '이전 이미지목록', '다음 이미지목록', 'window.NAML_MODULE_LIST', '&lt', '"item_alt":'
  '항공기명 ', '항속 거리 약 ', '무게  자체 중량 ', '최대 이륙 중량 ', '크기  날개폭 ',
  '분류 ', '유형 ', '크기 ', '정원 ', '최고속도 ', '배수량 ', '장갑 ', '갑판 ', '잠항 시 ',
  '시대 ', '제조국 ', '승무원 ', '중량 ', '치수 ', '전폭 ', '전고 ', '기동 가능 거리 ', '장갑 ', '엔진  ', '성능  ', '도섭 ', '수직 장애물 ', '전체화면  '
]

deletes = [
  '1. 특징', '2. 특징', '3. 운용현황', '4. 변형 및 파생기종'
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
  data = [re.sub('\s?,\s+', ', ', line) for line in data]
  data = [line.replace(' .', '.') for line in data]
  data = [re.sub('●|∙|·', '\t', line) for line in data]
  data = [re.sub('\s{3,}', '  \t', line) for line in data]
  data = [line.replace(': ', '\t') for line in data]
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
      sent = re.sub('^요약 ', '', sent).strip()
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