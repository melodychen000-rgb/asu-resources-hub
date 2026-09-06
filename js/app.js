import { allResources } from '../data/index.js';
import { filterResources } from './filter.js';
import { renderCards } from './render.js';

// 抓取 DOM 介面元素
const searchInput = document.getElementById('searchInput');
const campusFilter = document.getElementById('campusFilter');
const collegeFilter = document.getElementById('collegeFilter');
const systemFilter = document.getElementById('systemFilter');
const costFilter = document.getElementById('costFilter');
const resourceGrid = document.getElementById('resourceGrid');
const resultCount = document.getElementById('resultCount');
const resetBtn = document.getElementById('resetBtn');

// 核心更新函式：每次搜尋或點選篩選時觸發
function updateView() {
  const filterParams = {
    rawQuery: searchInput.value,
    campus: campusFilter.value,
    college: collegeFilter.value,
    system: systemFilter.value,
    cost: costFilter.value
  };

  // 1. 執行過濾邏輯 (來自 js/filter.js)
  const results = filterResources(allResources, filterParams);
  
  // 2. 渲染卡片畫面 (來自 js/render.js)
  renderCards(results, resourceGrid, resultCount);
}

// 快速點擊標籤功能（掛在 window 上供 HTML 按鈕使用）
window.setQuery = function(text) {
  searchInput.value = text;
  updateView();
};

// 一鍵清空所有篩選器
window.resetAllFilters = function() {
  searchInput.value = '';
  campusFilter.value = 'ALL';
  collegeFilter.value = 'ALL';
  systemFilter.value = 'ALL';
  costFilter.value = 'ALL';
  updateView();
};

// 綁定輸入與選單監聽事件
searchInput.addEventListener('input', updateView);
campusFilter.addEventListener('change', updateView);
collegeFilter.addEventListener('change', updateView);
systemFilter.addEventListener('change', updateView);
costFilter.addEventListener('change', updateView);
if (resetBtn) resetBtn.addEventListener('click', window.resetAllFilters);

// 頁面初次載入時立即執行一次渲染
updateView();
