import os
import re
import glob
from collections import defaultdict
from difflib import SequenceMatcher

def clean_name(name):
    """去除標點符號、括號內容與多餘空白，轉小寫以便比對相似度"""
    cleaned = re.sub(r'\(.*?\)', '', name)  # 移除括號內容
    cleaned = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', ' ', cleaned)  # 只留字母數字
    return ' '.join(cleaned.lower().split())

def similar(a, b):
    """計算兩名稱的相似度百分比"""
    return SequenceMatcher(None, a, b).ratio()

def parse_js_resources(data_dir="data"):
    resources = []
    files = glob.glob(os.path.join(data_dir, "*.js"))
    
    # 支援以正則表達式擷取每個 object 區塊
    obj_pattern = re.compile(r'\{([^{}]+)\}', re.DOTALL)
    
    for filepath in files:
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        matches = obj_pattern.findall(content)
        for obj_str in matches:
            name_m = re.search(r'name:\s*["\']([^"\']+)["\']', obj_str)
            url_m = re.search(r'direct_url:\s*["\']([^"\']+)["\']', obj_str)
            campus_m = re.search(r'campus:\s*["\']([^"\']+)["\']', obj_str)
            
            if name_m:
                name = name_m.group(1).strip()
                url = url_m.group(1).strip() if url_m else ""
                campus = campus_m.group(1).strip() if campus_m else ""
                
                resources.append({
                    "file": filename,
                    "name": name,
                    "clean_name": clean_name(name),
                    "url": url,
                    "campus": campus
                })
    return resources

def check_duplicates():
    resources = parse_js_resources()
    total_count = len(resources)
    
    print("=" * 65)
    print(f"🔍 開始檢測資源重複性，共讀取到 {total_count} 筆資源資料")
    print("=" * 65)
    
    # 1. 檢測完全重複的名稱
    name_map = defaultdict(list)
    for r in resources:
        name_map[r["name"]].append(r)
        
    exact_duplicates = {k: v for k, v in name_map.items() if len(v) > 1}
    
    # 2. 檢測高相似度名稱 (相似度 > 0.85 且非完全相同)
    fuzzy_duplicates = []
    checked_pairs = set()
    for i in range(len(resources)):
        for j in range(i + 1, len(resources)):
            r1, r2 = resources[i], resources[j]
            if r1["name"] == r2["name"]:
                continue
            pair_key = tuple(sorted([r1["name"], r2["name"]]))
            if pair_key in checked_pairs:
                continue
                
            sim_score = similar(r1["clean_name"], r2["clean_name"])
            if sim_score >= 0.85:
                fuzzy_duplicates.append((r1, r2, sim_score))
                checked_pairs.add(pair_key)
                
    # 輸出結果
    has_issue = False
    
    # 完全重複結果
    if exact_duplicates:
        has_issue = True
        print("\n❌ 【完全相同名稱重複】（建議立即刪除多餘筆數）：")
        for name, items in exact_duplicates.items():
            print(f"  ▪ 資源名稱: 「{name}」出現了 {len(items)} 次：")
            for item in items:
                print(f"     - 檔案: {item['file']} | 校區: {item['campus']} | 網址: {item['url']}")
    else:
        print("\n✅ 【完全相同名稱】：無任何重複項目！")
        
    # 高度相似結果（可能是多校區同名設施或重複加入）
    if fuzzy_duplicates:
        print("\n⚠️ 【高度相似名稱】（請確認是否為不同校區的同類設施）：")
        for r1, r2, score in fuzzy_duplicates:
            print(f"  ▪ 相似度 {int(score * 100)}%:")
            print(f"     1) [{r1['file']}] {r1['name']} ({r1['campus']})")
            print(f"     2) [{r2['file']}] {r2['name']} ({r2['campus']})")
    else:
        print("\n✅ 【高度相似名稱】：無異常重疊項目！")

    print("\n" + "=" * 65)
    if not has_issue:
        print("🎉 檢驗完成：未發現嚴重重複衝突！")
    else:
        print("⚠️ 檢驗完成：請依照上方提示清理重複項目。")
    print("=" * 65)

if __name__ == "__main__":
    check_duplicates()
