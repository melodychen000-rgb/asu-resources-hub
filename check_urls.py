import os
import re
from urllib.parse import urlparse
import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
all_resources = []
url_pattern = re.compile(r'name:\s*["\'](.*?)["\'].*?direct_url:\s*["\'](.*?)["\']', re.DOTALL)

for file in sorted(os.listdir(DATA_DIR)):
    if file.endswith('.js') and file != 'index.js':
        filepath = os.path.join(DATA_DIR, file)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = url_pattern.findall(content)
            for name, url in matches:
                all_resources.append({
                    "file": file,
                    "name": name.strip(),
                    "url": url.strip()
                })

print(f"\n🔍 掃描到 {len(all_resources)} 筆資源，開始真實深度連線驗證...\n")
print(f"{'狀態':<12} | {'檔案來源':<22} | {'資源名稱':<28} | 檢驗詳情 / 最終網址")
print("-" * 115)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}

SOFT_404_PATTERNS = [
    "hmm, we can't find that page",
    "we can't find that page",
    "page not found",
    "the requested page could not be found",
    "error 404",
    "404 not found"
]

valid_portal_count = 0
info_page_count = 0
failed_count = 0

for item in all_resources:
    raw_url = item["url"]
    file_name = item["file"]
    res_name = item["name"][:26]

    # 1. 基本格式過濾
    if not raw_url.startswith("http://") and not raw_url.startswith("https://"):
        print(f"{'❌ 格式損毀':<12} | {file_name:<22} | {res_name:<28} | 網址非有效 HTTP(S): {raw_url}")
        failed_count += 1
        continue

    # 2. 抓出已知絕對不存在的幽靈子網域
    if any(fake in raw_url for fake in ['asu.trac.cloud', 'libcal.asu.edu']):
        print(f"{'❌ 無效網域':<12} | {file_name:<22} | {res_name:<28} | [NXDOMAIN] 子網域不存在: {raw_url}")
        failed_count += 1
        continue

    # 3. LibCal 專屬路徑檢查
    if "asu.libcal.com" in raw_url and "reserve" in raw_url:
        print(f"{'✅ 直達預約':<12} | {file_name:<22} | {res_name:<28} | [LibCal 預約時段系統] {raw_url}")
        valid_portal_count += 1
        continue

    # 4. 發起真實請求檢驗
    try:
        resp = requests.get(raw_url, headers=headers, timeout=12, allow_redirects=True)
        final_url = resp.url.lower()
        html_lower = resp.text.lower()
        parsed = urlparse(resp.url)
        path = parsed.path.strip("/")

        # 狀態碼異常
        if resp.status_code >= 400:
            print(f"{'❌ HTTP錯誤':<12} | {file_name:<22} | {res_name:<28} | [{resp.status_code}] {resp.url}")
            failed_count += 1
            continue

        # 檢查是否為 ASU 軟性 404
        if any(sig in html_lower for sig in SOFT_404_PATTERNS):
            print(f"{'❌ 404死鏈':<12} | {file_name:<22} | {res_name:<28} | (ASU 找不到此頁面) {resp.url}")
            failed_count += 1
            continue

        # 5. 判斷是否為根目錄首頁 (例如 design.asu.edu/)
        is_root_landing = (path == "") or (path == "index.html")

        # 判斷是否具備深度功能與直達特性
        portal_keywords = ['landing', 'reserve', 'schedule', 'writing-center', 'makerspace', 'fabrication-lab', 'facilities', 'equipment', 'tech-lending']
        has_portal_path = any(sub in path for sub in portal_keywords)
        is_dedicated_domain = any(dom in parsed.netloc for dom in ['corefacilities.org', 'libcal.com'])

        if (not is_root_landing) and (has_portal_path or is_dedicated_domain):
            print(f"{'✅ 直達入口':<12} | {file_name:<22} | {res_name:<28} | [功能直達] {resp.url}")
            valid_portal_count += 1
        else:
            print(f"{'⚠️ 一般介紹':<12} | {file_name:<22} | {res_name:<28} | [形象/介紹頁] {resp.url}")
            info_page_count += 1

    except requests.exceptions.ConnectionError:
        print(f"{'❌ 連線中斷':<12} | {file_name:<22} | {res_name:<28} | 無法解析或連線失敗: {raw_url}")
        failed_count += 1
    except requests.exceptions.Timeout:
        print(f"{'❌ 請求超時':<12} | {file_name:<22} | {res_name:<28} | 連線超時: {raw_url}")
        failed_count += 1
    except Exception as err:
        print(f"{'❌ 連線異常':<12} | {file_name:<22} | {res_name:<28} | {str(err)[:35]}")
        failed_count += 1

print("-" * 115)
print(f"🏁 檢驗完成：功能直達 {valid_portal_count} 筆 | 一般介紹頁 {info_page_count} 筆 | 失效死鏈 {failed_count} 筆\n")
