
import requests
import time
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag

# アクセスするWebサイト
start_url = 'https://www.musashino-u.ac.jp/'

# 同一ドメインの判定
domain = urlparse(start_url).netloc

# URLとタイトルを保存する辞書
sitemap = {}

# これからアクセスするURL
url_list = [start_url]

# すでに確認したURL
checked_urls = set()

# HTTPリクエスト用のヘッダー
headers = {
    'User-Agent': 'Mozilla/5.0'
}

while url_list:
    url = url_list.pop(0)

    # URLの重複を防ぐ
    if url in checked_urls:
        continue

    checked_urls.add(url)

    time.sleep(1)

    try:
        res = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        # アクセスに失敗したページはスキップ
        if res.status_code != 200:
            print(f'取得失敗: {url} ({res.status_code})')
            continue

        # HTML以外はスキップ
        content_type = res.headers.get('Content-Type', '')
        if 'text/html' not in content_type.lower():
            continue

        # リダイレクト後のURLも同一ドメインか確認
        final_url = urldefrag(res.url)[0]
        if urlparse(final_url).netloc != domain:
            continue

        # HTMLを解析
        soup = BeautifulSoup(res.content, 'html.parser')

        # titleタグの文字列を取得
        title_tag = soup.find('title')

        if title_tag is not None:
            title = title_tag.get_text(strip=True)
        else:
            title = ''

        # URLをキー、タイトルを値として辞書に格納
        sitemap[final_url] = title

        print(f'取得: {final_url} : {title}')

        # ページ内のリンクをすべて取得
        for a in soup.find_all('a', href=True):
            link = urljoin(final_url, a['href'])
            link = urldefrag(link)[0]

            parsed = urlparse(link)

            # 同一ドメインのHTTP/HTTPSリンクのみ対象
            if parsed.scheme not in ('http', 'https'):
                continue

            if parsed.netloc != domain:
                continue

            # すでに確認済み・登録済みでなければ追加
            if link not in checked_urls and link not in url_list:
                url_list.append(link)

    except requests.RequestException as e:
        print(f'エラー: {url} : {e}')

# 辞書をCSVファイルに保存
with open('musashino-u-sitemap.csv', 'w',
          newline='', encoding='utf-8-sig') as f:

    writer = csv.writer(f)
    writer.writerow(['URL', 'title'])

    for url, title in sitemap.items():
        writer.writerow([url, title])

print('サイトマップの抽出が終了しました。')
print(f'取得したページ数: {len(sitemap)}')
print('CSVファイル: musashino-u-sitemap.csv')
