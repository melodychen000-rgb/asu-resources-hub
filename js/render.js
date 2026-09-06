import { getParentCollege } from './filter.js';

export function renderCards(items, containerElement, countElement) {
  containerElement.innerHTML = '';
  countElement.textContent = items.length;

  if (items.length === 0) {
    containerElement.innerHTML = `
      <div class="col-span-full py-16 text-center text-slate-400 bg-white border border-slate-200 rounded-xl">
        <p class="text-base font-semibold">No resources match your search filters.</p>
        <p class="text-xs mt-1 text-slate-400">Try clearing filters or clicking "Reset" above.</p>
      </div>
    `;
    return;
  }

  items.forEach(item => {
    const card = document.createElement('div');
    card.className = "bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow-md hover:border-slate-300 transition-all flex flex-col justify-between";

    const tags = item.tags ? item.tags.split(',').map(t => t.trim()).filter(Boolean) : [];
    const isFree = item.cost === 'Free';

    let btnText = "Open Access Portal ↗";
    if (item.system_type === 'Walk-in') btnText = "View Location & Hours ↗";
    else if (item.system_type === 'LibCal') btnText = "Book via LibCal ↗";
    else if (item.system_type === 'TutorSearch') btnText = "Book via TracCloud / ASN ↗";
    else if (item.system_type === 'iLab') btnText = "Reserve via iLab Core ↗";

    card.innerHTML = `
      <div>
        <div class="flex items-center justify-between gap-2 mb-2.5">
          <span class="text-[11px] font-extrabold uppercase tracking-wide text-[#8C1D40] bg-rose-50 px-2 py-0.5 rounded border border-rose-100">
            ${getParentCollege(item.college)}
          </span>
          <div class="flex items-center gap-1.5">
            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full ${isFree ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}">
              ${item.cost || 'Free'}
            </span>
            <span class="text-xs text-slate-500 font-medium">
              📍 ${item.campus || 'Tempe'}
            </span>
          </div>
        </div>
        
        <h3 class="text-base font-bold text-slate-900 leading-snug mb-1">${item.name}</h3>
        <p class="text-xs text-slate-500 mb-3 flex items-start gap-1">
          <span>🏛</span>
          <span>${item.location || 'Location details in portal'}</span>
        </p>

        <div class="space-y-1.5 text-xs text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-100 mb-3">
          <div class="flex items-start gap-1.5">
            <span class="font-bold text-slate-700 whitespace-nowrap">Portal:</span>
            <span class="font-semibold text-indigo-700">${item.system_type || 'Direct Link'}</span>
          </div>
          <div class="flex items-start gap-1.5">
            <span class="font-bold text-slate-700 whitespace-nowrap">Access:</span>
            <span class="text-slate-700">${item.eligibility || 'Check website'}</span>
          </div>
          <div class="flex items-start gap-1.5">
            <span class="font-bold text-slate-700 whitespace-nowrap">Prerequisite:</span>
            <span class="text-slate-500">${item.prerequisites || 'None'}</span>
          </div>
        </div>

        <div class="flex flex-wrap gap-1 mb-4">
          ${tags.slice(0, 4).map(t => `<span class="bg-slate-100 text-slate-600 text-[10px] font-medium px-2 py-0.5 rounded-full">#${t}</span>`).join('')}
        </div>
      </div>

      <a 
        href="${item.direct_url || '#'}" 
        target="_blank" 
        rel="noopener noreferrer"
        class="w-full text-center bg-[#8C1D40] hover:bg-[#701733] text-white text-xs font-bold py-2.5 px-4 rounded-lg transition-colors flex items-center justify-center gap-1.5 shadow-sm"
      >
        ${btnText}
      </a>
    `;
    containerElement.appendChild(card);
  });
}
