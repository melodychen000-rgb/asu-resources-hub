import os
import re
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
                all_resources.append({"file": file, "name": name.strip(), "url": url.strip()})

print(f"\n🔍 掃描到 {len(all_resources)} 筆資源，開始真實網頁可用性診斷...\n")
print(f"{'狀態':<10} | {'檔案來源':<22} | {'資源名稱':<30} | 說明 / 最終網址")
print("-" * 110)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

# ASU 軟性 404 (Soft 404) 的特徵字串
NOT_FOUND_SIGNALS = [
    "hmm, we can't find that page",
    "page not found",
    "the requested page could not be found",
    "error 404",
    "404 not found",
    "access denied",
    "dns_probe_finished_nxdomain"
]

broken_count = 0
portal_count = 0

for item in all_resources:
    raw_url = item["url"]

    # 格式防呆
    if not raw_url.startswith("http"):
        print(f"{'❌ 格式無效':<10} | {item['file']:<22} | {item['name'][:28]:<30} | 網址格式錯誤: {raw_url}")
        broken_count += 1
        continue

    # LibCal 直接保留官方預約驗證
    if "libcal.asu.edu/reserve" in raw_url:
        print(f"{'✅ 直達預約':<10} | {item['file']:<22} | {item['name'][:28]:<30} | [LibCal 預約時段表] {raw_url}")
        portal_count += 1
        continue

    try:
        resp = requests.get(raw_url, headers=headers, timeout=12, allow_redirects=True)
        final_url = resp.url.lower()
        html = resp.text.lower()

        # 1. 檢查是否為死鏈或軟性 404
        if resp.status_code >= 400 or any(sig in html for sig in NOT_FOUND_SIGNALS):
            print(f"{'❌ 找不到網頁':<10} | {item['file']:<22} | {item['name'][:28]:<30} | (404/失效) {resp.url}")
            broken_count += 1
            continue

        # 2. 檢查是否為直達預約或查詢入口
        is_portal = any(k in final_url for k in ['corefacilities.org', 'tutoring', 'schedule', 'software', 'makerspace', 'reserve']) or \
                    any(k in html for k in ['asurite', 'sign in', 'schedule an appointment', 'reserve'])

        if is_portal:
            status = "✅ 直達入口"
            portal_count += 1
        else:
            status = "⚠️ 一般介紹頁"

        print(f"{status:<10} | {item['file']:<22} | {item['name'][:28]:<30} | {resp.url}")

    except Exception as e:
        broken_count += 1
        print(f"{'❌ 連線中斷':<10} | {item['file']:<22} | {item['name'][:28]:<30} | 錯誤: {str(e)[:35]}")

print("-" * 110)
print(f"🏁 檢測完成！有效直達: {portal_count} 筆 | 失效/找不到: {broken_count} 筆\n")
