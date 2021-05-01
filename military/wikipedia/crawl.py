import argparse

import wikipediaapi
import requests
from tqdm import tqdm
from kss import split_sentences

topics = [
  '분류:공군',
  '분류:군사 계획',
  '분류:군사 용어',
  '분류:군사 전술',
  '분류:군인'
  '분류:무기',
  '분류:비전투 군사 작전',
  '분류:유형별 군사 작전'
  '분류:육군',
  '분류:전쟁별 군사 작전',
  '분류:전쟁별 분류',
  '분류:전쟁사',
  '분류:현대전',
  '분류:해군',
  '분류:해병대',
]

exclude_keywords = [
  '틀', '중요도',
  '작품', '영화', '문학', '드라마', '애니메이션', '가공의', '신화', '오디세', '만화', '잡지', '출판', '신문', '게임',
  '관련자', '동문', '사람',
  '기만', '심리전 전술', '실험', '악희',
  '군정기', '부역자', '친일파', '조선일보',
  '반전', '운동가',
  '국제 연맹', '후신 국가', '경제', '복지', '정치', '법', '문화', '사학',
  '혁명', '군벌', '반란', '분단', '홀로코스트', '수용소', '유엔', '신탁통치', '위성국', '정권', '봉기',
  '년',  '연도별',
  '번주', '고대', '유물', '로마', '씨', '시대', '석기', '식민지', '옛', '나라',
  '올림픽', '선수', '운동', '스포츠', '양궁', '사격', '바이애슬론', 'ACE', '사냥',
  '무술', '레슬', '복싱', '태권도', '우슈', '스모', '씨름', '카포에라', '무에타이',  '권투',
  '암호', '신원', '상거래', '보안', '프라이버시', '인터넷', '온라인', '네트워크', '웹',  '소프트웨어', '여론', '잡지', '대중 매체', '라디오', '텔레비전','미디어', '비디오',
  '남북', '냉전',
  '결투', '숙청', 
  ]

def address(topic, index):
  return 'https://terms.naver.com/entry.naver?docId={}&cid={}&categoryId={}'.format(
    index, topic, topic
  )

def parse(html):

  soup = BeautifulSoup(html, 'html.parser')

  # Title
  title = soup.find(
    'h2', class_='headword'
  ).text

  # Body text
  body_text = soup.select(
    '#size_ct'
  )[0].findAll(text=True, recursive=True)
  body_text = [obj for obj in body_text]
  body_text = ' '.join([text.strip().replace('\n', '').replace('\t', '') for text in body_text])
  body_text = body_text.replace('. ', '.\t')
  
  return [title, body_text]

def crawl(args):
  if args.load_pages:
    with open(args.load_pages, 'r', encoding='UTF-8') as file:
      wiki_list = file.read().splitlines()
      wiki_list = [title for title in wiki_list if title]
  else:
    # Init Wikipedia object
    wiki = wikipediaapi.Wikipedia('ko')

    visited_topics = set()
    def get_category_members(category, level=0, max_level=20):
      if level == max_level:
        return []
      categorymembers = category.categorymembers
      visited_topics.add(category.title)
      print(str(level) + ' / ' + category.title)
      wiki_list = []
      for c in categorymembers.values():
        if c.title in visited_topics:
          continue
        # Exclude less-related keywords
        exclude = False
        for excluded_key in exclude_keywords:
          if excluded_key in c.title:
            exclude=True
        if exclude:
          continue

        # Recursive call through topics, and
        # Retrieve pages
        if c.ns == wikipediaapi.Namespace.CATEGORY and c.title not in visited_topics:
          wiki_list.extend(get_category_members(c, level+1, max_level))
        elif c.ns == wikipediaapi.Namespace.CATEGORY:
          continue
        else:
          wiki_list.append(c)
      return wiki_list

    may_exist_dupl_wiki_list = []
    for topic in topics:
      root = wiki.page(topic)
      may_exist_dupl_wiki_list.extend(get_category_members(root))
      print('\n------------------------------------\n')
    wiki_list = set([page.title for page in may_exist_dupl_wiki_list])
    print('Total pages to crawl:')
    print(len(list(wiki_list)))
    if args.save_pages:
      with open(args.save_pages, 'w', encoding='UTF-8') as file:
        file.write('\n'.join(wiki_list))
    
  file = open(args.dst_path, 'w', encoding='UTF-8')
  # FIXME: stride=50
  stride = 1
  for i in tqdm(range(0, len(wiki_list), stride)):
    titles = wiki_list[i: min(i+stride, len(wiki_list))]
    response = requests.get(
      'https://ko.wikipedia.org/w/api.php',
      params={
          'action': 'query',
          'format': 'json',
          'titles': '|'.join(titles),
          'prop': 'extracts',
          'explaintext': True,
      }, headers={'User-Agent': 'Mozilla/5.0'}).json()
    if i == 0:
      print(response)
    result = [split_sentences(page['extract'].replace('\n', ' '), safe=True) for page in response['query']['pages'].values()]
    for title, result in zip(titles, result):
      file.write('\t'.join([title] + result) + '\n')
  file.close()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--dst-path', type=str, default='data/crawl.tsv', help='Path to store crawl results')
  parser.add_argument('--save-pages', type=str)
  parser.add_argument('--load-pages', type=str)
  args = parser.parse_args()
  assert not (args.save_pages and args.load_pages)

  crawl(args)