import { productArt } from './art.js';

const $ = (id) => document.getElementById(id);
const translations = {
  zh: {banner:'研究原型 <span>／</span> 合成商品目錄 <span>／</span> 不涉及真實付款',chat:'購物對話',browse:'探索商品',cart:'購物車',newSession:'新對話',agent:'你的採購助手',trace:'查看實際工具操作',memory:'早期對話記憶',memoryWarning:'這是受限的歷史參考，不會改變購物車、預算或權限；目前狀態優先。',memoryCovered:'已壓縮訊息',memoryTopics:'主題',memoryNotes:'保留的舊使用者訊息',title:'把需要的，<br><span>準備剛好。</span>',intro:'告訴我你的用途、預算和已有的東西。<br>我來準備購物車，最後由你決定。',tags:'<span>從需求出發</span><span>保留你的選擇</span><span>不替你下單</span>',ready:'準備好聽你說',workspace:'一起準備你的下一個小計畫',explore:'自己逛，也不會丟失進度',resetDone:'已開始新的對話；購物車與本次對話已清空。',resetBusy:'目前正在處理需求；完成後才可開始新對話。',introEyebrow:'少找一點，多完成一點。',stillLabel:'你的創作一角',stillNote:'不一定買更多，<br>只買需要的。',stillNumber:'01 / 桌面必備',shoppingSpace:'你的購物空間',cartEyebrow:'同一購物車，由你決定',cartTitle:'正在為你準備',editConstraints:'調整需求與已知條件 ↗',checkout:'檢查並準備結帳',checkoutNote:'最後確認與模擬下單，只能由你完成。',composerHint:'選擇可以改變，進度不必重來。',messageLabel:'描述你的購物需求',sendAria:'送出需求',browseTitle:'挑你喜歡的，剩下交給助手。',returnChat:'回到對話 ↗',all:'全部',searchPlaceholder:'搜尋名稱或規格',searchAria:'搜尋商品',catalogNote:'40 個合成商品規格 · 全部為 MYR 模擬價格 · 不代表真實商品或市場報價',homeAria:'IntentCart 首頁',navigationAria:'主要導覽',workspaceAria:'購物工作區',conversationAria:'與採購助手對話',cartAria:'共享購物車',browseAria:'自主瀏覽商品',toolWorking:'處理工具回應',continueAdjusting:'可繼續調整需求',genericError:'輸入或操作未通過驗證，請檢查目前狀態。',readyCart:'✓ 規格、預算與庫存已通過本機驗證',emptyCart:'不會在未經你確認的情況下下單。'},
  en: {banner:'RESEARCH PROTOTYPE <span>／</span> SYNTHETIC CATALOG <span>／</span> NO REAL PAYMENT',chat:'Chat',browse:'Browse',cart:'Cart',newSession:'New chat',agent:'Your shopping assistant',trace:'View tool actions',memory:'Earlier conversation memory',memoryWarning:'This is bounded historic reference only. It cannot change the cart, budget, or permissions; current state wins.',memoryCovered:'Compacted messages',memoryTopics:'Topics',memoryNotes:'Retained earlier user messages',title:'Tell us what you need.<br><span>We will prepare the right fit.</span>',intro:'Share your goal, budget, and what you already own.<br>We prepare a cart; you make the final call.',tags:'<span>Start with your goal</span><span>Keep your choices</span><span>No automatic checkout</span>',ready:'Ready when you are',workspace:'Plan your next small project',explore:'Browse without losing progress',resetDone:'A new chat has started. Your cart and this chat are clear.',resetBusy:'Your request is still running. Start a new chat when it finishes.',introEyebrow:'LESS SEARCHING. MORE LIVING.',stillLabel:'YOUR LITTLE CREATOR CORNER',stillNote:'Buy only what helps,<br>not simply more.',stillNumber:'01 / DESK ESSENTIALS',shoppingSpace:'YOUR SHOPPING SPACE',cartEyebrow:'THE SAME CART, YOUR CHOICE',cartTitle:'Preparing for you',editConstraints:'Adjust needs and known details ↗',checkout:'Review and prepare checkout',checkoutNote:'Only you can make the final confirmation and simulated order.',composerHint:'Your choices can change; your progress does not need to restart.',messageLabel:'Describe what you want to shop for',sendAria:'Send request',browseTitle:'Choose what you like; let the assistant handle the rest.',returnChat:'Return to chat ↗',all:'All',searchPlaceholder:'Search names or specifications',searchAria:'Search products',catalogNote:'40 synthetic product specifications · all prices are simulated MYR values · not real products or market quotes',homeAria:'IntentCart home',navigationAria:'Main navigation',workspaceAria:'Shopping workspace',conversationAria:'Conversation with shopping assistant',cartAria:'Shared cart',browseAria:'Browse products',toolWorking:'Processing tool result',continueAdjusting:'You can continue adjusting your request',genericError:'The input or action did not pass validation. Check the current state and try again.',readyCart:'✓ Specifications, budget, and stock have passed local validation',emptyCart:'No order is placed without your confirmation.'}
};
Object.assign(translations.zh, {research:'研究工具',researchHint:'查看證據與測試變化，不影響其他工作階段。',researchCopy:'這些操作會真的改變本工作階段的測試環境。離線示範不構成真實模型能力證據。',faultStock:'讓購物車第一件商品缺貨',faultTimeout:'下次 agent 寫入後中斷',faultFee:'費用改為未知',restoreFee:'還原已知費用',export:'匯出本次研究紀錄 ↓',footer:'告訴它你的需要。最後由你決定。',productClose:'關閉商品詳情',constraintsClose:'關閉需求設定',constraintsEyebrow:'邊界，由你設定',constraintsTitle:'需求，由你說了算。',budgetLabel:'總預算（RM，留空表示未設定）',portLabel:'已確認的手機接口',unknown:'尚未確認',needLegend:'需要準備',ownedLegend:'已經擁有，不重複購買',colorLabel:'顏色偏好（非硬性限制）',any:'沒有偏好',deskOnly:'只找適合桌面使用的商品',save:'儲存條件',checkoutClose:'取消結帳',finalEyebrow:'最後一步，由你決定',finalTitle:'最後一步，由你確認。',finalCopy:'這是一筆模擬訂單，不會付款或配送。',confirm:'確認模擬下單',confirmNote:'此確認綁定目前商品、數量與金額；購物車改變後必須重新確認。'});
Object.assign(translations.en, {research:'Research tools',researchHint:'View evidence and test changes without affecting other sessions.',researchCopy:'These controls really change this session\'s test environment. The offline demo is not evidence of live-model capability.',faultStock:'Make the first cart item out of stock',faultTimeout:'Interrupt after the next agent write',faultFee:'Make fees unknown',restoreFee:'Restore known fees',export:'Export this research record ↓',footer:'Tell it what you need. Make the final call.',productClose:'Close product details',constraintsClose:'Close requirement settings',constraintsEyebrow:'YOU SET THE BOUNDARIES',constraintsTitle:'You define the requirements.',budgetLabel:'Total budget (RM; leave blank if unset)',portLabel:'Confirmed phone connector',unknown:'Not confirmed',needLegend:'Need to prepare',ownedLegend:'Already own; do not buy again',colorLabel:'Color preference (not a hard constraint)',any:'No preference',deskOnly:'Only show items suitable for a desk',save:'Save details',checkoutClose:'Cancel checkout',finalEyebrow:'THE FINAL CALL IS YOURS',finalTitle:'The final step is yours to confirm.',finalCopy:'This is a simulated order. No payment or delivery will occur.',confirm:'Confirm simulated order',confirmNote:'This confirmation is tied to the current items, quantities, and amount. Change the cart and you must confirm again.'});
let language = localStorage.getItem('intentcart-language') === 'en' ? 'en' : 'zh';
Object.assign(translations.zh, {thinking:'\u6b63\u5728\u8655\u7406\u4f60\u7684\u9700\u6c42\u2026'});
Object.assign(translations.en, {thinking:'Working on your request...'});
const t = (key) => translations[language][key];
const productName = (product) => language === 'en' ? product.name : product.name_zh;
const kindName = (kind) => language === 'en' ? ({light:'Lighting',microphone:'Audio',stand:'Stands',accessory:'Accessories'})[kind] : ({light:'燈光',microphone:'收音',stand:'支架',accessory:'配件'})[kind];
const colorName = (color) => language === 'en' ? ({ivory:'Ivory',sage:'Sage',black:'Black',any:'No preference'})[color] : ({ivory:'米白',sage:'鼠尾草綠',black:'黑色',any:'無偏好'})[color];
const portName = (port) => language === 'en' ? ({'usb-c':'USB-C',lightning:'Lightning',any:'No phone connection',unknown:'Unknown specification'})[port] : ({'usb-c':'USB-C',lightning:'Lightning',any:'不需連接手機',unknown:'規格未確認'})[port];
const escape = (value) => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const money = (cents) => cents == null ? '待確認' : `RM ${(cents / 100).toFixed(2)}`;
const uid = () => crypto.randomUUID();
const kinds = {light:'燈光',microphone:'收音',stand:'支架',accessory:'配件'};
const colors = {ivory:'米白',sage:'鼠尾草綠',black:'黑色',any:'無偏好'};
const ports = {'usb-c':'USB-C',lightning:'Lightning',any:'不需連接手機',unknown:'規格未確認'};
const toolNames = {ask_user:{zh:'確認影響方案的資訊',en:'Ask for a material detail'},inspect_task:{zh:'核對需求與最新購物車',en:'Inspect request and saved cart'},search_catalog:{zh:'搜尋商品與規格',en:'Search catalog'},inspect_product:{zh:'讀取具體商品',en:'Inspect product'},validate_plan:{zh:'驗證候選組合',en:'Validate proposed cart'},apply_plan:{zh:'更新共享購物車',en:'Update shared cart'},edit_cart:{zh:'修改商品',en:'Edit cart'},validate_cart:{zh:'核對已儲存購物車',en:'Validate saved cart'},require_items:{zh:'記錄必要物品',en:'Record required items'}};
const recommendationStarts = [
  {id:'dawn-ivory', label:{zh:'拍攝光線',en:'Better lighting'}, note:{zh:'想讓桌面拍片畫面更穩定、少受環境光影響。',en:'Start with steadier desk lighting and less reliance on room light.'}, draft:{zh:'我想先改善桌面拍片的光線。我的用途是＿＿，預算是 RM＿＿，我已經有＿＿。',en:'I want to improve lighting for desk videos. My goal is __, my budget is RM __, and I already have __.'}},
  {id:'clip-black-usb-c', label:{zh:'清晰收音',en:'Clearer audio'}, note:{zh:'想先讓人聲更清楚，再決定是否需要其他設備。',en:'Make speech clearer first, then decide whether other gear is needed.'}, draft:{zh:'我想先改善錄人聲的收音。我的手機接口是＿＿，預算是 RM＿＿，我已經有＿＿。',en:'I want clearer speech recording. My phone connector is __, my budget is RM __, and I already have __.'}},
  {id:'angle-ivory', label:{zh:'穩定機位',en:'Stable framing'}, note:{zh:'想從簡單、可調整的桌面拍攝角度開始。',en:'Begin with a simple, adjustable desk filming angle.'}, draft:{zh:'我想讓桌面拍片的機位更穩定。我要拍＿＿，預算是 RM＿＿，我已經有＿＿。',en:'I want more stable desk-video framing. I will film __, my budget is RM __, and I already have __.'}}
];
let state = null, csrf = '', config = {}, products = [], chatMessages = [], conversationMemory = null, currentView = 'chat';
let filterKind = '', replacement = null, running = false, tools = [], pendingCheckout = null, toastTimer;

function notify(message) {
  $('toast').textContent = message;
  $('toast').hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { $('toast').hidden = true; }, 6500);
}

async function request(path, body) {
  const response = await fetch(path, {method:body === undefined ? 'GET':'POST', credentials:'same-origin',
    headers:body === undefined ? {} : {'Content-Type':'application/json','X-CSRF-Token':csrf},
    body:body === undefined ? undefined : JSON.stringify(body)});
  const value = await response.json();
  if (!response.ok) throw new Error(value.error?.message || t('genericError'));
  return value;
}

function accept(snapshot) {
  if (!state || snapshot.version >= state.version) {
    state = snapshot;
    renderCart();
  }
}

async function refresh() {
  const result = await request('/api/state');
  if (csrf && csrf !== result.csrf) state = null;
  csrf = result.csrf; config = result.config; chatMessages = result.messages; conversationMemory = result.memory;
  accept(result.state); renderMessages(); renderMemory(); renderMode();
  const catalog = await request('/api/catalog'); products = catalog.products; renderMessages(); renderProducts();
}

function renderPending(message = t('thinking')) {
  let pending = $('agent-pending');
  if (!pending) {
    pending = document.createElement('div');
    pending.id = 'agent-pending';
    pending.className = 'message assistant pending-message';
    pending.innerHTML = '<span class="avatar">&#10033;</span><div class="bubble" role="status" aria-live="polite"><span class="typing-dots" aria-hidden="true"><i></i><i></i><i></i></span><span class="pending-copy"></span></div>';
    $('messages').append(pending);
  }
  pending.querySelector('.pending-copy').textContent = message;
  $('messages').scrollTop = $('messages').scrollHeight;
}

function clearPending() {
  $('agent-pending')?.remove();
}

function applyLanguage() {
  document.documentElement.lang = language === 'en' ? 'en' : 'zh-Hant';
  $('research-banner').innerHTML = t('banner');
  $('nav-chat').textContent = t('chat'); $('nav-browse').textContent = t('browse');
  $('cart-toggle').childNodes[0].textContent = `${t('cart')} `;
  $('new-session').textContent = t('newSession');
  $('language-toggle').textContent = language === 'en' ? '中文' : 'EN';
  $('agent-title').textContent = t('agent'); $('trace-label').textContent = t('trace');
  $('memory-label').textContent = t('memory'); $('memory-warning').textContent = t('memoryWarning');
  $('intro-eyebrow').innerHTML = `<span class="small-star">✳</span> ${t('introEyebrow')}`;
  $('still-label').textContent = t('stillLabel'); $('still-note').innerHTML = t('stillNote'); $('still-number').textContent = t('stillNumber');
  $('workspace-eyebrow').textContent = t('shoppingSpace'); $('cart-eyebrow').textContent = t('cartEyebrow'); $('cart-title').textContent = t('cartTitle');
  $('edit-constraints').textContent = t('editConstraints'); $('checkout-label').textContent = t('checkout'); $('checkout-note').textContent = t('checkoutNote');
  $('message-label').textContent = t('messageLabel'); $('composer-hint').textContent = t('composerHint'); $('send').setAttribute('aria-label', t('sendAria'));
  $('browse-title').textContent = t('browseTitle'); $('return-chat').textContent = t('returnChat');
  $('catalog-search').placeholder = t('searchPlaceholder'); $('catalog-search').setAttribute('aria-label', t('searchAria')); $('catalog-note').textContent = t('catalogNote');
  document.querySelectorAll('[data-i18n-aria]').forEach(node => node.setAttribute('aria-label', t(node.dataset.i18nAria)));
  document.querySelectorAll('[data-kind]').forEach(button => { button.textContent = button.dataset.kind ? kindName(button.dataset.kind) : t('all'); });
  const research = document.querySelector('.research-tools');
  research.querySelector('summary').childNodes[0].textContent = t('research') + ' ';
  research.querySelector('summary span').textContent = t('researchHint'); research.querySelector('.research-content > p').textContent = t('researchCopy');
  $('fault-stock').textContent = t('faultStock'); $('fault-timeout').textContent = t('faultTimeout'); $('fault-fee').textContent = t('faultFee'); $('restore-fee').textContent = t('restoreFee'); $('export').textContent = t('export');
  document.querySelector('footer span:nth-child(2)').textContent = t('footer');
  const constraints = $('constraints-dialog');
  constraints.querySelector('.dialog-close').setAttribute('aria-label', t('constraintsClose')); constraints.querySelector('.eyebrow').textContent = t('constraintsEyebrow'); constraints.querySelector('h2').textContent = t('constraintsTitle');
  const labels = constraints.querySelectorAll('form > label');
  labels[0].childNodes[0].textContent = t('budgetLabel'); labels[1].childNodes[0].textContent = t('portLabel'); labels[2].childNodes[0].textContent = t('colorLabel'); labels[3].childNodes[1].textContent = t('deskOnly');
  constraints.querySelector('fieldset:nth-of-type(1) legend').textContent = t('needLegend'); constraints.querySelector('fieldset:nth-of-type(2) legend').textContent = t('ownedLegend');
  $('port-input').options[0].textContent = t('unknown'); $('color-input').options[0].textContent = t('any'); $('constraints-form').querySelector('button[type="submit"]').textContent = t('save');
  const checkoutDialog = $('checkout-dialog');
  checkoutDialog.querySelector('.dialog-close').setAttribute('aria-label', t('checkoutClose')); checkoutDialog.querySelector('.eyebrow').textContent = t('finalEyebrow'); checkoutDialog.querySelector('h2').textContent = t('finalTitle');
  checkoutDialog.querySelector('h2 + p').textContent = t('finalCopy'); $('confirm-order').textContent = t('confirm'); checkoutDialog.querySelector('.checkout-note').textContent = t('confirmNote');
  $('product-dialog').querySelector('.dialog-close').setAttribute('aria-label', t('productClose'));
  $('intro-title').innerHTML = t('title'); $('intro-copy').innerHTML = t('intro'); $('intro-tags').innerHTML = t('tags');
  $('message').placeholder = language === 'en' ? 'For example: I have RM300 for a desk-video light and microphone…' : '例如：預算 RM300，幫我準備桌面拍片用的燈和麥克風…';
  if (!running) $('run-status').textContent = t('ready');
  renderMode(); renderMessages(); renderMemory(); renderCart(); renderProducts();
  setView(currentView);
}

function renderMode() {
  const live = config.driver === 'live';
  $('driver-badge').textContent = live ? `${language === 'en' ? 'Live model' : '真實模型'} · ${config.model}` : config.driver === 'baseline' ? (language === 'en' ? 'Fixed-flow control · Not an LLM' : '固定流程對照 · 非 LLM') : (language === 'en' ? 'Rule demo · Not an LLM' : '規則示範 · 非 LLM');
  $('driver-badge').classList.toggle('live', live);
  $('demo-note').textContent = live ? (language === 'en' ? 'The model chooses tools; saved cart state and readiness are verified by the application.' : '工具由模型選擇；購物車狀態與完成判定由程式驗證。') : (language === 'en' ? 'This is an interactive offline control, not model-performance evidence.' : '目前為可操作的離線控制模式，沒有呼叫模型；不能當作 agent 表現證據。');
}

function renderMessages() {
  if (!chatMessages.length) {
    const recommendations = recommendationStarts.map(start => {
      const product = products.find(p => p.id === start.id);
      if (!product) return '';
      return `<article class="recommendation-card"><span class="recommendation-label">${language === 'en' ? 'START HERE' : '推薦起點'} · ${escape(start.label[language])}</span><strong>${escape(productName(product))}</strong><p>${escape(start.note[language])}</p><div><span class="price">${money(product.price_cents)}</span><button type="button" data-recommendation="${escape(start.draft[language])}">${language === 'en' ? 'Start here →' : '從這裡開始 →'}</button></div></article>`;
    }).join('');
    const welcome = language === 'en' ? ['Explore a starting point, then tell us what you want to achieve.','Recommendations never add to your cart. Add your goal, budget, and existing gear before we prepare anything.','Explore this catalog','Fixed catalog suggestions; no personal data used'] : ['先看看適合你的起點，再告訴我你想完成什麼。','推薦不會自動加入購物車；補充用途、預算和已有物品後，我才會開始準備。','從目錄探索','固定目錄推薦，不使用個人資料'];
    $('messages').innerHTML = `<div class="message welcome-card"><span class="avatar">✳</span><div class="bubble"><strong>${welcome[0]}</strong><br>${welcome[1]}${recommendations ? `<section class="recommendation-starts" aria-label="${welcome[2]}"><div class="recommendation-heading"><span>${welcome[2]}</span><small>${welcome[3]}</small></div><div class="recommendation-grid">${recommendations}</div></section>` : ''}</div></div>`;
  } else {
    $('messages').innerHTML = chatMessages.map(m => `<div class="message ${m.role === 'user' ? 'user':'assistant'}">${m.role === 'assistant' ? '<span class="avatar">✳</span>':''}<div class="bubble">${escape(m.text)}</div></div>`).join('');
    document.body.classList.add('compact');
  }
  const quick = !chatMessages.length ? (language === 'en' ? [
    ['Prepare a desk-video setup', 'I need a desk light and microphone for videos. My budget is RM300, my phone uses USB-C, and I already own a stand.'],
    ['Browse products myself', null]
  ] : [
    ['幫我準備桌面拍片組合', '我想找桌面拍片用的燈和麥克風，預算 RM300，手機是 USB-C，已經有支架。'],
    ['我想自己挑選', null]
  ]) : state?.constraints.device_port === 'unknown' && state?.constraints.needs.includes('microphone') ? (language === 'en' ? [['My phone uses USB-C','My phone uses USB-C.'],['My phone uses Lightning','My phone uses Lightning.']] : [['我的手機是 USB-C','我的手機是 USB-C。'],['我的手機是 Lightning','我的手機是 Lightning。']]) : (language === 'en' ? [['Keep the light; change the budget to RM180','Keep the light; change the budget to RM180.'],['Browse other options',null]] : [['保留燈，預算改成 RM180','保留燈，預算改成 RM180。'],['自己看看其他選擇',null]]);
  $('quick-actions').innerHTML = quick.map(([label, text]) => `<button type="button" ${text ? `data-prompt="${escape(text)}"` : 'data-browse'}>${escape(label)}</button>`).join('');
  $('messages').scrollTop = $('messages').scrollHeight;
  if (running) renderPending();
}

function renderMemory() {
  const panel = $('conversation-memory');
  if (!conversationMemory) { panel.hidden = true; return; }
  panel.hidden = false;
  const topicLabels = {recording:language === 'en' ? 'Recording' : '拍攝／收音',recommendation:language === 'en' ? 'Recommendations' : '推薦',price_comparison:language === 'en' ? 'Prices' : '價格比較',catalog_browsing:language === 'en' ? 'Catalog browsing' : '瀏覽商品'};
  const lines = [`${t('memoryCovered')}: ${conversationMemory.covered_messages}`, `${t('memoryTopics')}: ${(conversationMemory.topics || []).map(topic => topicLabels[topic] || topic).join(', ') || '—'}`];
  const notes = conversationMemory.historical_user_notes || [];
  if (notes.length) lines.push('', `${t('memoryNotes')}:`, ...notes.map(note => `• ${note.text}`));
  $('memory-body').textContent = lines.join('\n');
}

function issueText(issue) {
  if (language !== 'en') return issue.code === 'MISSING_KIND' ? `尚缺${kindName(issue.kind)}` : issue.message;
  const labels = {
    MISSING_KIND: `Missing ${kindName(issue.kind)}`,
    OVER_BUDGET: 'The cart exceeds the budget',
    OUT_OF_STOCK: 'An item is out of stock',
    UNKNOWN_COMPATIBILITY: 'Connector compatibility is not confirmed',
    INCOMPATIBLE: 'An item is incompatible with the confirmed connector',
    MISSING_ACCESSORY: 'A required accessory is missing',
    UNKNOWN_FEE: 'Simulated fees are unknown',
    LOCKED: 'A kept selection cannot be changed automatically',
    EXCLUDED: 'A previously removed item cannot be re-added automatically'
  };
  return labels[issue.code] || 'The saved cart still needs attention';
}

function renderCart() {
  if (!state) return;
  const c = state.constraints, v = state.validation;
  $('cart-count').textContent = String(state.items.reduce((sum,item) => sum + item.quantity, 0));
  $('task-facts').innerHTML = `<span class="fact">${c.budget_cents ? `${language === 'en' ? 'Budget' : '預算'} ${money(c.budget_cents)}` : (language === 'en' ? 'No budget set' : '預算未設定')}</span><span class="fact ${c.device_port === 'unknown' ? 'unknown':''}">${c.device_port === 'unknown' ? (language === 'en' ? 'Connector unknown' : '接口待確認') : portName(c.device_port)}</span>${c.owned.map(k => `<span class="fact">${language === 'en' ? 'Owns ' : '已有'}${kindName(k)}</span>`).join('')}`;
  $('cart-items').innerHTML = state.items.length ? state.items.map(item => {
    const p = item.product;
    return `<article class="cart-item" data-cart-item="${escape(p.id)}"><div class="cart-art">${productArt(p)}</div><div><h4>${escape(productName(p))}</h4><span class="spec">${colorName(p.color)} · ${portName(p.port)} · ×${item.quantity}</span><div class="price-row"><span class="price">${money(p.price_cents * item.quantity)}</span>${item.locked ? `<span class="lock-badge">✓ ${language === 'en' ? 'Kept' : '已保留'}</span>`:''}</div><div class="cart-actions"><button data-edit="${item.locked ? 'unlock':'lock'}" data-id="${escape(p.id)}">${item.locked ? (language === 'en' ? 'Unlock':'解除保留') : (language === 'en' ? 'Keep this':'保留這件')}</button><button data-replace="${escape(p.id)}">${language === 'en' ? 'Replace':'換一件'}</button><button data-edit="remove" data-id="${escape(p.id)}">${language === 'en' ? 'Remove':'移除'}</button><button data-edit="quantity" data-quantity="${item.quantity < 5 ? item.quantity+1:1}" data-id="${escape(p.id)}">${language === 'en' ? 'Quantity' : '數量'} ${item.quantity < 5 ? '+1':(language === 'en' ? 'reset to 1':'改為 1')}</button></div></div></article>`;
  }).join('') : `<div class="empty-cart"><span class="empty-symbol">⌑</span><strong>${language === 'en' ? 'Turn one need into a useful list.' : '從一個需求，開始一份清單。'}</strong><p>${language === 'en' ? 'Your choices and the assistant share one cart.<br>You can adjust it at any time.' : '你和助手的選擇會放在同一個購物車，<br>隨時都能調整。'}</p></div>`;
  $('cart-summary').innerHTML = `<div class="total-row"><span>${language === 'en' ? 'Items subtotal' : '商品小計'}</span><span>${money(v.subtotal_cents)}</span></div><div class="total-row"><span>${language === 'en' ? 'Simulated fees' : '全部模擬費用'}</span><span>${v.fee_cents === 0 ? (language === 'en' ? 'Included' : '已包含') : money(v.fee_cents)}</span></div><div class="total-row total"><span>${language === 'en' ? 'Total' : '合計'}</span><span>${money(v.total_cents)}</span></div>`;
  $('cart-issues').classList.toggle('ready', v.ready);
  $('cart-issues').textContent = v.ready ? t('readyCart') : state.items.length ? [...new Set(v.issues.map(issueText))].join(' · ') : t('emptyCart');
  $('checkout').disabled = !v.ready;
}

function setView(view) {
  currentView = view;
  $('chat-view').hidden = view !== 'chat'; $('browse-view').hidden = view !== 'browse';
  $('intro').hidden = view === 'browse';
  $('workspace-title').textContent = view === 'browse' ? t('explore') : t('workspace');
  document.querySelectorAll('[data-view]').forEach(b => b.classList.toggle('active', b.dataset.view === view));
  if (view === 'browse') renderProducts();
}

function renderProducts() {
  const term = $('catalog-search').value.toLowerCase().trim();
  const matches = products.filter(p => (!filterKind || p.kind === filterKind) && (!term || `${p.name} ${p.name_zh} ${p.id} ${p.port}`.toLowerCase().includes(term)));
  $('browse-hint').textContent = replacement ? (language === 'en' ? 'You are replacing an item. The new choice will be kept and the rest of the cart will stay intact.' : '正在替換一件商品。你選定的新商品會被保留，其餘購物車內容不變。') : (language === 'en' ? 'Items you add directly are kept and will not be silently replaced by the agent.' : '直接加入的選擇會自動保留，不會被 agent 悄悄替換。');
  $('product-grid').innerHTML = matches.length ? matches.map(p => `<article class="product-card"><button class="product-image" data-details="${escape(p.id)}" aria-label="${language === 'en' ? 'View' : '查看'} ${escape(productName(p))} ${escape(portName(p.port))} ${escape(colorName(p.color))}"><span class="product-kind">${kindName(p.kind)}</span>${productArt(p)}</button><div class="product-info"><h3>${escape(productName(p))}</h3><p>${colorName(p.color)} · ${portName(p.port)}</p><div class="product-bottom"><span class="price">${money(p.price_cents)}</span><button data-add="${escape(p.id)}" ${p.stock < 1 ? 'disabled':''}>${p.stock < 1 ? (language === 'en' ? 'Out of stock':'已缺貨') : replacement ? (language === 'en' ? 'Replace with this':'用這件替換') : (language === 'en' ? 'Add and keep +':'加入並保留 ＋')}</button></div></div></article>`).join('') : `<p>${language === 'en' ? 'No matching products. Adjust your search or describe what you need in chat.' : '沒有符合條件的商品。請調整搜尋，或回到對話說明需求。'}</p>`;
  document.querySelectorAll('[data-kind]').forEach(b => b.classList.toggle('active', b.dataset.kind === filterKind));
}

function logTool(name, result) {
  tools.push({name, result});
  $('tool-count').textContent = String(tools.length);
  $('tool-log').innerHTML = tools.slice(-40).map(t => `<div class="tool-row ${t.result.ok ? '':'error'}">${t.result.ok ? '✓':'!'} ${escape(toolNames[t.name]?.[language] || t.name)}${t.result.ok ? '':` · ${escape(t.result.error?.code || '')}`}</div>`).join('');
  $('run-status').textContent = toolNames[name]?.[language] || t('toolWorking');
}

async function sendMessage(text) {
  if (running || !text.trim()) return;
  running = true; $('send').disabled = true; $('run-status').classList.add('running');
  chatMessages.push({role:'user',text}); renderMessages(); renderPending(); $('message').value = '';
  try {
    const response = await fetch('/api/chat', {method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:JSON.stringify({message:text,request_id:uid(),language})});
    if (!response.ok) { const data = await response.json(); throw new Error(data.error?.message || '這輪執行未啟動。'); }
    if (!response.body) throw new Error('瀏覽器無法讀取串流。');
    const reader = response.body.getReader(), decoder = new TextDecoder();
    let buffer = '', finished = false;
    while (true) {
      const {value,done} = await reader.read();
      buffer += decoder.decode(value || new Uint8Array(), {stream:!done});
      const lines = buffer.split('\n'); buffer = lines.pop() || '';
      for (const line of lines) {
        if (!line.trim()) continue;
        const event = JSON.parse(line);
        if (event.type === 'progress') { $('run-status').textContent = event.message; renderPending(event.message); }
        if (event.type === 'tool') logTool(event.name,event.result);
        if (event.type === 'state') accept(event.state);
        if (event.type === 'error') { clearPending(); notify(event.error.message); }
        if (event.type === 'done') { clearPending(); accept(event.state); conversationMemory = event.memory; renderMemory(); finished = true; }
      }
      if (done) break;
    }
    if (!finished) notify('連線中斷：已重新讀取實際購物車，沒有自動重送操作。');
  } catch (error) { notify(error.message || '執行中斷。'); }
  finally {
    clearPending();
    running = false; $('send').disabled = false; $('run-status').classList.remove('running');
    $('run-status').textContent = t('continueAdjusting');
    try { await refresh(); } catch { notify('無法重新讀取狀態，請稍後重新載入。'); }
  }
}

async function changeCart(operation, variantId, options = {}) {
  try {
    const result = await request('/api/cart', {operation,variant_id:variantId,expected_version:state.version,request_id:uid(),...options});
    accept(result.state);
    if (operation === 'add' || operation === 'replace') notify('已加入並保留你的選擇。聊天與瀏覽共用這份購物車。');
    await refresh();
    return true;
  } catch(error) { notify(error.message); await refresh(); return false; }
}

async function showProduct(id) {
  try {
    const p = await request(`/api/products/${encodeURIComponent(id)}`);
    const detail = language === 'en' ? {eyebrow:'SYNTHETIC PRODUCT',color:'Color',port:'Connector',desk:'Desk suitable',stock:'Simulated stock',requires:'Required accessories',none:'None',id:'Specification ID',note:'All prices include known simulated fees. There is no real merchant or transaction.',replace:'Replace with this item',add:'Add and keep this item',yes:'Yes',no:'No'} : {eyebrow:'合成商品',color:'顏色',port:'接口',desk:'桌面適用',stock:'模擬庫存',requires:'必要配件',none:'無',id:'規格 ID',note:'所有價格包含已知模擬費用。沒有真實商家或交易。',replace:'用這件替換',add:'加入並保留這件商品',yes:'是',no:'否'};
    $('product-details').innerHTML = `<p class="eyebrow">${detail.eyebrow} / ${escape(kindName(p.kind))}</p><div class="detail-art">${productArt(p)}</div><h2>${escape(productName(p))}</h2><strong class="price">${money(p.price_cents)}</strong><div class="detail-facts"><span>${detail.color}</span><strong>${colorName(p.color)}</strong><span>${detail.port}</span><strong>${portName(p.port)}</strong><span>${detail.desk}</span><strong>${p.desk_fit ? detail.yes:detail.no}</strong><span>${detail.stock}</span><strong>${p.stock}</strong><span>${detail.requires}</span><strong>${p.requires.length ? escape(p.requires.join(', ')):detail.none}</strong><span class="wide">${detail.id}: ${escape(p.id)}<br>${detail.note}</span></div><button class="primary-button" data-add="${escape(p.id)}" ${p.stock < 1 ? 'disabled':''}>${replacement ? detail.replace:detail.add}</button>`;
    $('product-dialog').showModal();
  } catch(error) { notify(error.message); }
}

function showConstraints() {
  const c = state.constraints;
  $('budget-input').value = c.budget_cents == null ? '' : (c.budget_cents/100).toFixed(2);
  $('port-input').value = c.device_port; $('color-input').value = c.preferred_color; $('desk-input').checked = c.desk_only;
  for (const [group,values] of [['need',c.needs],['owned',c.owned]]) {
    $(group+'-inputs').innerHTML = Object.keys(kinds).map(k => `<label><input type="checkbox" name="${group}" value="${k}" ${values.includes(k) ? 'checked':''}>${kindName(k)}</label>`).join('');
  }
  $('constraints-form').dataset.version = String(state.version);
  $('constraints-dialog').showModal();
}

$('hero-art').innerHTML = productArt({kind:'light',color:'ivory'},true) + productArt({kind:'microphone',color:'sage'},true);
$('chat-form').addEventListener('submit', event => { event.preventDefault(); sendMessage($('message').value); });
$('message').addEventListener('keydown', event => { if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {event.preventDefault(); sendMessage($('message').value);} });
$('catalog-search').addEventListener('input',renderProducts);
$('return-chat').addEventListener('click',() => setView('chat'));
$('cart-toggle').addEventListener('click',() => {setView('chat');$('cart-panel').scrollIntoView({behavior:'smooth',block:'start'});$('cart-panel').classList.add('focus-cart');setTimeout(()=>$('cart-panel').classList.remove('focus-cart'),1500);});
$('edit-constraints').addEventListener('click',showConstraints);
$('language-toggle').addEventListener('click',() => { language = language === 'en' ? 'zh' : 'en'; localStorage.setItem('intentcart-language', language); applyLanguage(); });

$('new-session').addEventListener('click',async () => {
  if (running) return notify(t('resetBusy'));
  try {
    const result=await request('/api/session/reset',{});
    csrf=result.csrf; config=result.config; chatMessages=[]; conversationMemory=result.memory; state=null; tools=[]; pendingCheckout=null; replacement=null;
    $('tool-count').textContent='0'; $('tool-log').innerHTML=''; $('receipt').hidden=true; clearPending();
    accept(result.state); renderMessages(); renderMemory(); renderMode();
    notify(t('resetDone'));
  } catch(error) {notify(error.message);}
});

$('constraints-form').addEventListener('submit',async event => {
  event.preventDefault();
  const selected = name => Array.from(document.querySelectorAll(`input[name="${name}"]:checked`)).map(el => el.value);
  const rawBudget = $('budget-input').value;
  const constraints = {budget_cents:rawBudget ? Math.round(Number(rawBudget)*100):null,needs:selected('need'),owned:selected('owned'),device_port:$('port-input').value,preferred_color:$('color-input').value,desk_only:$('desk-input').checked};
  try {
    const result = await request('/api/constraints',{constraints,expected_version:Number($('constraints-form').dataset.version),request_id:uid()});
    accept(result.state);$('constraints-dialog').close();notify('條件已儲存。可以請助手依照新條件調整。');
  } catch(error) {notify(error.message);await refresh();}
});

document.addEventListener('click',async event => {
  const button = event.target.closest('button'); if (!button) return;
  if (button.dataset.view) setView(button.dataset.view);
  if ('browse' in button.dataset) {replacement = null;setView('browse');}
  if (button.dataset.prompt) sendMessage(button.dataset.prompt);
  if (button.dataset.recommendation) {
    $('message').value = button.dataset.recommendation;
    $('message').focus();
    $('run-status').textContent = language === 'en' ? 'Recommendation added. Fill in the details, then send.' : '已帶入推薦起點，補充後再送出';
  }
  if ('kind' in button.dataset) {filterKind=button.dataset.kind;renderProducts();}
  if (button.dataset.details) showProduct(button.dataset.details);
  if (button.dataset.close) $(button.dataset.close).close();
  if (button.dataset.edit) {
    button.disabled=true;
    await changeCart(button.dataset.edit,button.dataset.id,button.dataset.quantity ? {quantity:Number(button.dataset.quantity)}:{});
    button.disabled=false;
  }
  if (button.dataset.replace) {
    replacement=button.dataset.replace; filterKind=products.find(p=>p.id===replacement)?.kind || '';setView('browse');
    $('browse-view').scrollIntoView({behavior:'smooth',block:'start'});
  }
  if (button.dataset.add) {
    button.disabled=true;
    const result=await changeCart(replacement ? 'replace':'add',button.dataset.add,replacement ? {target_id:replacement}:{});
    button.disabled=false;
    if (result) {replacement=null;$('product-dialog').close();renderProducts();}
  }
});

$('checkout').addEventListener('click',async () => {
  try {
    pendingCheckout = await request('/api/checkout/preview', {});
    pendingCheckout.request_id = uid();
    const s=pendingCheckout.state;
    $('confirmation-summary').innerHTML = s.items.map(i=>`<div class="confirmation-item"><span>${escape(productName(i.product))} ×${i.quantity}</span><strong>${money(i.product.price_cents*i.quantity)}</strong></div>`).join('')+`<div class="confirmation-total"><span>${language === 'en' ? 'Total (including simulated fees)' : '合計（已含模擬費用）'}</span><strong>${money(s.validation.total_cents)}</strong></div>`;
    $('checkout-dialog').showModal();
  } catch(error) {notify(error.message);await refresh();}
});

$('confirm-order').addEventListener('click',async () => {
  if (!pendingCheckout) return;
  $('confirm-order').disabled=true;
  try {
    const order=await request('/api/checkout/confirm',{confirmation_token:pendingCheckout.confirmation_token,expected_version:pendingCheckout.version,request_id:pendingCheckout.request_id});
    $('checkout-dialog').close();pendingCheckout=null;
    $('receipt').hidden=false;$('receipt').textContent=`✓ 模擬訂單 ${order.id} 已由你確認，共 ${money(order.snapshot.validation.total_cents)}。沒有真實付款，也不會配送。`;
    await refresh();$('receipt').scrollIntoView({behavior:'smooth',block:'center'});
  } catch(error) {notify(error.message);$('checkout-dialog').close();pendingCheckout=null;await refresh();}
  finally {$('confirm-order').disabled=false;}
});

async function fault(name,variantId=null) {
  try {const result=await request('/api/experiments',{fault:name,variant_id:variantId});accept(result.state);await refresh();$('experiment-status').textContent='環境已變更。回到對話請助手繼續，即可觀察修正與工具紀錄。';}
  catch(error){notify(error.message);}
}
$('fault-stock').addEventListener('click',()=>state.items.length ? fault('stock',state.items[0].product.id):notify('先在購物車加入一件商品。'));
$('fault-timeout').addEventListener('click',()=>fault('write_timeout'));
$('fault-fee').addEventListener('click',()=>fault('unknown_fee'));
$('restore-fee').addEventListener('click',()=>fault('restore_fee'));
$('export').addEventListener('click',async()=>{
  try {const data=await request('/api/export');const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='intentcart-session.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  catch(error){notify(error.message);}
});

applyLanguage();
refresh().then(async()=>{const trace=await request('/api/trace');for(const e of trace.events.filter(e=>e.kind==='tool').slice(-40))logTool(e.payload.name,e.payload.result);$('run-status').textContent=t('ready');}).catch(error=>notify((language === 'en' ? 'Could not load: ':'載入失敗：')+error.message));
