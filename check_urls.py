import os
import re
import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
all_resources = []
url_pattern = re.compile(
    r'name:\s*["\'](.*?)["\'].*?direct_url:\s*["\'](.*?)["\']', re.DOTALL
)

for file in sorted(os.listdir(DATA_DIR)):
  if file.endswith('.js') and file != 'index.js':
    filepath = os.path.join(DATA_DIR, file)
    with open(filepath, 'r', encoding='utf-8') as f:
      content = f.read()
      matches = url_pattern.findall(content)
      for name, url in matches:
        all_resources.append(
            {'file': file, 'name': name.strip(), 'url': url.strip()}
        )

print(
    f'\n🔍 掃描到 {len(all_resources)} 筆資源，開始無盲區真實連線驗證...\n'
)
print(f"{'狀態':<12} | {'檔案來源':<22} | {'資源名稱':<28} | 檢驗詳情 / 最終網址")
print('-' * 115)

headers = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,'
        ' like Gecko) Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept': (
        'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    ),
}

# 嚴格過濾 404 與不存在的網域特徵
SOFT_404_PATTERNS = [
    "hmm, we can't find that page",
    "page not found",
    'the requested page could not be found',
    'error 404',
    '404 not found',
]

valid_portal_count = 0
info_page_count = 0
failed_count = 0

for item in all_resources:
  raw_url = item['url']
  file_name = item['file']
  res_name = item['name'][:26]

  # 1. 抓出已知絕對不存在的幽靈子網域
  if any(fake in raw_url for fake in ['asu.trac.cloud', 'libcal.asu.edu']):
    print(
        f"{'❌ 無效網域':<12} | {file_name:<22} | {res_name:<28} | [NXDOMAIN]"
        f' 子網域不存在: {raw_url}'
    )
    failed_count += 1
    continue

  # 2. 真實連線測試
  try:
    resp = requests.get(
        raw_url, headers=headers, timeout=12, allow_redirects=True
    )
    final_url = resp.url.lower()
    html_lower = resp.text.lower()

    if resp.status_code >= 400:
      print(
          f"{'❌ HTTP錯誤':<12} | {file_name:<22} | {res_name:<28} |"
          f' [{resp.status_code}] {resp.url}'
      )
      failed_count += 1
      continue

    if any(sig in html_lower for sig in SOFT_404_PATTERNS):
      print(
          f"{'❌ 404死鏈':<12} | {file_name:<22} | {res_name:<28} | (ASU"
          f' 找不到此頁面) {resp.url}'
      )
      failed_count += 1
      continue

    is_portal = any(
        term in final_url
        for term in [
            'corefacilities.org',
            'libcal.com',
            'tutoring',
            'makerspace',
            'reserve',
        ]
    ) or any(
        kw in html_lower
        for kw in [
            'asurite',
            'sign in',
            'reserve a space',
            'schedule an appointment',
        ]
    )

    if is_portal:
      print(
          f"{'✅ 直達入口':<12} | {file_name:<22} | {res_name:<28} |"
          f' [已連通] {resp.url}'
      )
      valid_portal_count += 1
    else:
      print(
          f"{'⚠️ 一般介紹':<12} | {file_name:<22} | {res_name:<28} | {resp.url}"
      )
      info_page_count += 1

  except requests.exceptions.ConnectionError:
    print(
        f"{'❌ 連線中斷':<12} | {file_name:<22} | {res_name:<28} |"
        f' 無法解析/連線失敗: {raw_url}'
    )
    failed_count += 1
  except Exception as err:
    print(
        f"{'❌ 連線異常':<12} | {file_name:<22} | {res_name:<28} |"
        f' {str(err)[:35]}'
    )
    failed_count += 1

print('-' * 115)
print(
    f'🏁 檢驗完成：直達入口 {valid_portal_count} 筆 | 一般介紹頁'
    f' {info_page_count} 筆 | 失效死鏈 {failed_count} 筆\n'
)
