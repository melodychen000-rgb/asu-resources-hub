import { academicSupportResources } from './academic-support.js';
import { engineeringResources } from './engineering.js';
import { coreFacilitiesResources } from './core-facilities.js';
import { artsAndMediaResources } from './arts-media.js';
import { healthLawOtherResources } from './health-law-other.js';

// 自動合併所有分類資料庫
export const allResources = [
  ...academicSupportResources,
  ...engineeringResources,
  ...coreFacilitiesResources,
  ...artsAndMediaResources,
  ...healthLawOtherResources
];
