/**
 * 學院標準化對照
 */
export function getParentCollege(rawCollege) {
  if (!rawCollege) return 'Other';
  const c = rawCollege.toUpperCase();
  if (c.includes('ECEE') || c.includes('SCAI') || c.includes('SEMTE') || c.includes('SBHSE') || c.includes('FSE')) {
    return 'FSE (Engineering & Tech)';
  }
  if (c.includes('ASN') || c.includes('ACADEMIC SUPPORT') || c.includes('UASP')) {
    return 'Academic Support Network (ASN)';
  }
  if (c.includes('CORE') || c.includes('EYRING') || c.includes('BIODESIGN')) {
    return 'Core Research Facilities';
  }
  if (c.includes('HERBERGER') || c.includes('ART') || c.includes('MUSIC') || c.includes('DESIGN')) {
    return 'Herberger Institute (HIDA)';
  }
  if (c.includes('CRONKITE') || c.includes('JOURNALISM')) {
    return 'Cronkite Journalism';
  }
  if (c.includes('CAREY') || c.includes('BUSINESS')) {
    return 'W. P. Carey Business';
  }
  if (c.includes('LIBRARY')) {
    return 'ASU Library';
  }
  if (c.includes('SDFC') || c.includes('FITNESS')) {
    return 'Sun Devil Fitness (SDFC)';
  }
  if (c.includes('LAW')) {
    return "Sandra Day O'Connor Law";
  }
  if (c.includes('HEALTH') || c.includes('CHS') || c.includes('NURSING') || c.includes('EDSON')) {
    return 'Health & Nursing (Edson/CHS)';
  }
  if (c.includes('GLOBAL') || c.includes('FUTURES') || c.includes('SUSTAINABILITY')) {
    return 'Global Futures / Sustainability';
  }
  if (c.includes('COLLEGE') || c.includes('LIBERAL') || c.includes('SESE')) {
    return 'The College (CLAS / SESE)';
  }
  return rawCollege;
}

/**
 * 智慧校區判定
 */
export function matchesCampusCriteria(itemCampus, filterCampus) {
  if (filterCampus === 'ALL') return true;
  if (!itemCampus) return false;

  const f = filterCampus.toLowerCase();
  const c = itemCampus.toLowerCase();

  if (f.includes('online')) {
    return c.includes('online') || c.includes('remote') || c.includes('zoom') || c.includes('virtual');
  }

  return c.includes(f) || c.includes('all');
}

/**
 * 核心多維度過濾器
 */
export function filterResources(items, { rawQuery, campus, college, system, cost }) {
  const searchTokens = rawQuery ? rawQuery.toLowerCase().trim().split(/\s+/).filter(Boolean) : [];

  return items.filter(item => {
    const matchesCampus = matchesCampusCriteria(item.campus, campus);

    const parentCollege = getParentCollege(item.college);
    const matchesCollege = (college === 'ALL') || 
      parentCollege.toLowerCase().includes(college.toLowerCase()) || 
      (item.college && item.college.toLowerCase().includes(college.toLowerCase()));

    const matchesSystem = (system === 'ALL') || 
      (item.system_type && item.system_type.toLowerCase() === system.toLowerCase());

    const matchesCost = (cost === 'ALL') || 
      (item.cost && item.cost.toLowerCase() === cost.toLowerCase());

    const corpus = `${item.name} ${item.college} ${parentCollege} ${item.campus} ${item.location} ${item.tags} ${item.prerequisites} ${item.system_type} ${item.cost}`.toLowerCase();
    const matchesQuery = searchTokens.length === 0 || searchTokens.every(token => corpus.includes(token));

    return matchesCampus && matchesCollege && matchesSystem && matchesCost && matchesQuery;
  });
}
