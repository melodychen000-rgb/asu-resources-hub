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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

needs_fix = 0

for item in all_resources:
    try:
        resp = requests.get(item["url"], headers=headers, timeout=10, allow_redirects=True)
        final_url = resp.url.lower()
        html = resp.text.lower()

        # 入口特徵判定 (TracCloud, LibCal, iLab, ASURITE SSO 等)
        is_portal = any(k in final_url for k in ['trac.cloud', 'libcal.asu.edu', 'corefacilities.org', 'cas/login', 'auth', 'sign-in']) or \
                    any(k in html for k in ['asurite sign in', 'login with asurite', 'reserve this room', 'schedule appointment'])

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
print(f"🏁 檢測完成！共有 {needs_fix} 筆資源仍停留在普通文章/介紹頁，需要換成直達入口。\n")
