import os
import re
import glob
import time
import urllib.request
import urllib.error

def extract_urls_from_js(data_dir="data"):
    resources = []
    files = glob.glob(os.path.join(data_dir, "*.js"))
    obj_pattern = re.compile(r'\{([^{}]+)\}', re.DOTALL)
    
    for filepath in files:
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        matches = obj_pattern.findall(content)
        for obj_str in matches:
            name_m = re.search(r'name:\s*["\']([^"\']+)["\']', obj_str)
            url_m = re.search(r'direct_url:\s*["\']([^"\']+)["\']', obj_str)
            if name_m and url_m:
                resources.append({
                    "file": filename,
                    "name": name_m.group(1).strip(),
                    "url": url_m.group(1).strip()
                })
    return resources

def test_url(url, cache):
    if url in cache:
        return cache[url]

    # 設定標準瀏覽器 Header 避免被 ASU 防火牆阻擋
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers, method='HEAD')
            with urllib.request.urlopen(req, timeout=10) as resp:
                code = resp.getcode()
                cache[url] = (code, "OK")
                return cache[url]
        except urllib.error.HTTPError as e:
            if e.code == 429:  # 遇到頻率限制，休息 2 秒後重試
                time.sleep(2)
                continue
            elif e.code in [403, 405]:  # 部分伺服器禁止 HEAD，改用 GET 嘗試
                try:
                    req_get = urllib.request.Request(url, headers=headers, method='GET')
                    with urllib.request.urlopen(req_get, timeout=10) as resp_get:
                        cache[url] = (resp_get.getcode(), "OK")
                        return cache[url]
                except urllib.error.HTTPError as e_inner:
                    cache[url] = (e_inner.code, f"HTTP {e_inner.code}")
                    return cache[url]
                except Exception:
                    pass
            cache[url] = (e.code, f"HTTP {e.code}")
            return cache[url]
        except Exception as e:
            cache[url] = (999, str(e))
            return cache[url]

    cache[url] = (429, "Rate Limited")
    return cache[url]

def main():
    resources = extract_urls_from_js()
    print("=" * 70)
    print(f"🚀 開始全面驗證 {len(resources)} 筆校園資源網址...")
    print("=" * 70)

    url_cache = {}
    direct_ok = 0
    intro_ok = 0
    dead_links = 0

    for idx, r in enumerate(resources, start=1):
        url = r["url"]
        code, msg = test_url(url, url_cache)
        
        # 判定類型
        is_intro = "about" in url.lower() or "maker" in url.lower() or "landing" in url.lower()
        status_tag = ""

        if code in [200, 301, 302, 307, 308]:
            if is_intro:
                status_tag = "⚠️ 一般介紹"
                intro_ok += 1
            else:
                status_tag = "✅ 直達入口"
                direct_ok += 1
            print(f"{idx:3d} | {status_tag} | {r['file']:<20} | {r['name'][:30]:<30} | [{code}] {url}")
        else:
            status_tag = "❌ HTTP錯誤"
            dead_links += 1
            print(f"{idx:3d} | {status_tag} | {r['file']:<20} | {r['name'][:30]:<30} | [{code}] {url}")

        # 稍微暫停 0.05 秒，避免狂暴發送請求
        time.sleep(0.05)

    print("\n" + "=" * 70)
    print(f"🏁 檢驗完成：功能直達 {direct_ok} 筆 | 一般介紹 {intro_ok} 筆 | 失效死鏈 {dead_links} 筆")
    print("=" * 70)

    if dead_links > 0:
        exit(1)

if __name__ == "__main__":
    main()
