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

print(f"\n🔍 掃描到 {len(all_resources)} 筆資源，開始驗證目標跳轉與入口狀態...\n")
print(f"{'狀態':<10} | {'檔案來源':<22} | {'資源名稱':<32} | 最終抵達網址")
print("-" * 105)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

needs_fix = 0

for item in all_resources:
    raw_url = item["url"]
    
    # 1. 針對已知官方直達系統 (TracCloud / LibCal / iLab)，直接認定為直達入口
    if "asu.trac.cloud" in raw_url:
        print(f"{'✅ 直達入口':<10} | {item['file']:<22} | {item['name'][:30]:<32} | [TracCloud 預約系統直達] {raw_url}")
        continue

    if "libcal.asu.edu" in raw_url:
        print(f"{'✅ 直達入口':<10} | {item['file']:<22} | {item['name'][:30]:<32} | [LibCal 預約系統直達] {raw_url}")
        continue

    # 2. 其他網址自動連線追蹤
    try:
        resp = requests.get(raw_url, headers=headers, timeout=10, allow_redirects=True)
        final_url = resp.url.lower()
        html = resp.text.lower()

        # 入口特徵庫 (包含排班表 schedules、研究平台 ilab、軟體領取 portal)
        is_portal = any(k in final_url for k in ['corefacilities.org', 'schedules', 'cas/login', 'software']) or \
                    any(k in html for k in ['asurite sign in', 'schedule an appointment', 'reserve this room'])

        if is_portal:
            status = "✅ 直達入口"
        else:
            status = "⚠️ 仍為介紹頁"
            needs_fix += 1

        print(f"{status:<10} | {item['file']:<22} | {item['name'][:30]:<32} | {resp.url}")

    except Exception as e:
        needs_fix += 1
        print(f"{'❌ 失敗':<10} | {item['file']:<22} | {item['name'][:30]:<32} | 連線異常: {str(e)[:35]}")

print("-" * 105)
print(f"🏁 檢測完成！共有 {needs_fix} 筆資源仍為普通文章/介紹頁。\n")
