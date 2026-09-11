import { productArt } from './art.js';

const $ = (id) => document.getElementById(id);
const escape = (value) => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const money = (cents) => cents == null ? '待確認' : `RM ${(cents / 100).toFixed(2)}`;
const uid = () => crypto.randomUUID();
const kinds = {light:'燈光',microphone:'收音',stand:'支架',accessory:'配件'};
const colors = {ivory:'米白',sage:'鼠尾草綠',black:'黑色',any:'無偏好'};
const ports = {'usb-c':'USB-C',lightning:'Lightning',any:'不需連接手機',unknown:'規格未確認'};
const toolNames = {ask_user:'確認影響方案的資訊',inspect_task:'核對需求與最新購物車',search_catalog:'搜尋商品與規格',inspect_product:'讀取具體商品',validate_plan:'驗證候選組合',apply_plan:'更新共享購物車',edit_cart:'修改商品',validate_cart:'核對已儲存購物車',require_items:'記錄必要物品'};
let state = null, csrf = '', config = {}, products = [], chatMessages = [], currentView = 'chat';
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
  if (!response.ok) throw new Error(value.error?.message || '輸入或操作未通過驗證，請檢查目前狀態。');
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
  csrf = result.csrf; config = result.config; chatMessages = result.messages;
  accept(result.state); renderMessages(); renderMode();
  const catalog = await request('/api/catalog'); products = catalog.products; renderProducts();
}

function renderMode() {
  const live = config.driver === 'live';
  $('driver-badge').textContent = live ? `真實模型 · ${config.model}` : config.driver === 'baseline' ? '固定流程對照 · 非 LLM' : '規則示範 · 非 LLM';
  $('driver-badge').classList.toggle('live', live);
  $('demo-note').textContent = live ? '工具由模型選擇；購物車狀態與完成判定由程式驗證。' : '目前為可操作的離線控制模式，沒有呼叫模型；不能當作 agent 表現證據。';
}

function renderMessages() {
  if (!chatMessages.length) {
    $('messages').innerHTML = `<div class="message welcome-card"><span class="avatar">✳</span><div class="bubble"><strong>先說說，你想完成什麼？</strong><br>例如佈置一個小小的手機拍片角落。<br>把預算、已有物品告訴我，不必先研究每件商品。</div></div>`;
  } else {
    $('messages').innerHTML = chatMessages.map(m => `<div class="message ${m.role === 'user' ? 'user':'assistant'}">${m.role === 'assistant' ? '<span class="avatar">✳</span>':''}<div class="bubble">${escape(m.text)}</div></div>`).join('');
    document.body.classList.add('compact');
  }
  const quick = !chatMessages.length ? [
    ['幫我準備桌面拍片組合', '我想找桌面拍片用的燈和麥克風，預算 RM300，手機是 USB-C，已經有支架。'],
    ['我想自己挑選', null]
  ] : state?.constraints.device_port === 'unknown' && state?.constraints.needs.includes('microphone') ? [['我的手機是 USB-C','我的手機是 USB-C。'],['我的手機是 Lightning','我的手機是 Lightning。']] : [['保留燈，預算改成 RM180','保留燈，預算改成 RM180。'],['自己看看其他選擇',null]];
  $('quick-actions').innerHTML = quick.map(([label, text]) => `<button type="button" ${text ? `data-prompt="${escape(text)}"` : 'data-browse'}>${escape(label)}</button>`).join('');
  $('messages').scrollTop = $('messages').scrollHeight;
}

function renderCart() {
  if (!state) return;
  const c = state.constraints, v = state.validation;
  $('cart-count').textContent = String(state.items.reduce((sum,item) => sum + item.quantity, 0));
  $('task-facts').innerHTML = `<span class="fact">${c.budget_cents ? `預算 ${money(c.budget_cents)}` : '預算未設定'}</span><span class="fact ${c.device_port === 'unknown' ? 'unknown':''}">${c.device_port === 'unknown' ? '接口待確認':ports[c.device_port]}</span>${c.owned.map(k => `<span class="fact">已有${kinds[k]}</span>`).join('')}`;
  $('cart-items').innerHTML = state.items.length ? state.items.map(item => {
    const p = item.product;
    return `<article class="cart-item" data-cart-item="${escape(p.id)}"><div class="cart-art">${productArt(p)}</div><div><h4>${escape(p.name_zh)}</h4><span class="spec">${colors[p.color]} · ${ports[p.port]} · ×${item.quantity}</span><div class="price-row"><span class="price">${money(p.price_cents * item.quantity)}</span>${item.locked ? '<span class="lock-badge">✓ 已保留</span>':''}</div><div class="cart-actions"><button data-edit="${item.locked ? 'unlock':'lock'}" data-id="${escape(p.id)}">${item.locked ? '解除保留':'保留這件'}</button><button data-replace="${escape(p.id)}">換一件</button><button data-edit="remove" data-id="${escape(p.id)}">移除</button><button data-edit="quantity" data-quantity="${item.quantity < 5 ? item.quantity+1:1}" data-id="${escape(p.id)}">數量 ${item.quantity < 5 ? '+1':'改為 1'}</button></div></div></article>`;
  }).join('') : `<div class="empty-cart"><span class="empty-symbol">⌑</span><strong>從一個需求，開始一份清單。</strong><p>你和助手的選擇會放在同一個購物車，<br>隨時都能調整。</p></div>`;
  $('cart-summary').innerHTML = `<div class="total-row"><span>商品小計</span><span>${money(v.subtotal_cents)}</span></div><div class="total-row"><span>全部模擬費用</span><span>${v.fee_cents === 0 ? '已包含':money(v.fee_cents)}</span></div><div class="total-row total"><span>合計</span><span>${money(v.total_cents)}</span></div>`;
  $('cart-issues').classList.toggle('ready', v.ready);
  $('cart-issues').textContent = v.ready ? '✓ 規格、預算與庫存已通過本機驗證' : state.items.length ? [...new Set(v.issues.map(i => i.code === 'MISSING_KIND' ? `尚缺${kinds[i.kind]}`:i.message))].join(' · ') : '不會在未經你確認的情況下下單。';
  $('checkout').disabled = !v.ready;
}

function setView(view) {
  currentView = view;
  $('chat-view').hidden = view !== 'chat'; $('browse-view').hidden = view !== 'browse';
  $('intro').hidden = view === 'browse';
  $('workspace-title').textContent = view === 'browse' ? '自己逛，也不會丟失進度' : '一起準備你的下一個小計畫';
  document.querySelectorAll('[data-view]').forEach(b => b.classList.toggle('active', b.dataset.view === view));
  if (view === 'browse') renderProducts();
}

function renderProducts() {
  const term = $('catalog-search').value.toLowerCase().trim();
  const matches = products.filter(p => (!filterKind || p.kind === filterKind) && (!term || `${p.name} ${p.name_zh} ${p.id} ${p.port}`.toLowerCase().includes(term)));
  $('browse-hint').textContent = replacement ? '正在替換一件商品。你選定的新商品會被保留，其餘購物車內容不變。' : '直接加入的選擇會自動保留，不會被 agent 悄悄替換。';
  $('product-grid').innerHTML = matches.length ? matches.map(p => `<article class="product-card"><button class="product-image" data-details="${escape(p.id)}" aria-label="查看 ${escape(p.name_zh)} ${escape(ports[p.port])} ${escape(colors[p.color])}"><span class="product-kind">${kinds[p.kind]}</span>${productArt(p)}</button><div class="product-info"><h3>${escape(p.name_zh)}</h3><p>${colors[p.color]} · ${ports[p.port]}</p><div class="product-bottom"><span class="price">${money(p.price_cents)}</span><button data-add="${escape(p.id)}" ${p.stock < 1 ? 'disabled':''}>${p.stock < 1 ? '已缺貨':replacement ? '用這件替換':'加入並保留 ＋'}</button></div></div></article>`).join('') : '<p>沒有符合條件的商品。請調整搜尋，或回到對話說明需求。</p>';
  document.querySelectorAll('[data-kind]').forEach(b => b.classList.toggle('active', b.dataset.kind === filterKind));
}

function logTool(name, result) {
  tools.push({name, result});
  $('tool-count').textContent = String(tools.length);
  $('tool-log').innerHTML = tools.slice(-40).map(t => `<div class="tool-row ${t.result.ok ? '':'error'}">${t.result.ok ? '✓':'!'} ${escape(toolNames[t.name] || t.name)}${t.result.ok ? '':` · ${escape(t.result.error?.code || '')}`}</div>`).join('');
  $('run-status').textContent = toolNames[name] || '處理工具回應';
}

async function sendMessage(text) {
  if (running || !text.trim()) return;
  running = true; $('send').disabled = true; $('run-status').classList.add('running');
  chatMessages.push({role:'user',text}); renderMessages(); $('message').value = '';
  try {
    const response = await fetch('/api/chat', {method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:JSON.stringify({message:text,request_id:uid()})});
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
        if (event.type === 'progress') $('run-status').textContent = event.message;
        if (event.type === 'tool') logTool(event.name,event.result);
        if (event.type === 'state') accept(event.state);
        if (event.type === 'error') notify(event.error.message);
        if (event.type === 'done') { accept(event.state); finished = true; }
      }
      if (done) break;
    }
    if (!finished) notify('連線中斷：已重新讀取實際購物車，沒有自動重送操作。');
  } catch (error) { notify(error.message || '執行中斷。'); }
  finally {
    running = false; $('send').disabled = false; $('run-status').classList.remove('running');
    $('run-status').textContent = '可繼續調整需求';
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
    $('product-details').innerHTML = `<p class="eyebrow">SYNTHETIC PRODUCT / ${escape(kinds[p.kind])}</p><div class="detail-art">${productArt(p)}</div><h2>${escape(p.name_zh)}</h2><strong class="price">${money(p.price_cents)}</strong><div class="detail-facts"><span>顏色</span><strong>${colors[p.color]}</strong><span>接口</span><strong>${ports[p.port]}</strong><span>桌面適用</span><strong>${p.desk_fit ? '是':'否'}</strong><span>模擬庫存</span><strong>${p.stock}</strong><span>必要配件</span><strong>${p.requires.length ? escape(p.requires.join(', ')):'無'}</strong><span class="wide">規格 ID：${escape(p.id)}<br>所有價格包含已知模擬費用。沒有真實商家或交易。</span></div><button class="primary-button" data-add="${escape(p.id)}" ${p.stock < 1 ? 'disabled':''}>${replacement ? '用這件替換':'加入並保留這件商品'}</button>`;
    $('product-dialog').showModal();
  } catch(error) { notify(error.message); }
}

function showConstraints() {
  const c = state.constraints;
  $('budget-input').value = c.budget_cents == null ? '' : (c.budget_cents/100).toFixed(2);
  $('port-input').value = c.device_port; $('color-input').value = c.preferred_color; $('desk-input').checked = c.desk_only;
  for (const [group,values] of [['need',c.needs],['owned',c.owned]]) {
    $(group+'-inputs').innerHTML = Object.entries(kinds).map(([k,label]) => `<label><input type="checkbox" name="${group}" value="${k}" ${values.includes(k) ? 'checked':''}>${label}</label>`).join('');
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
    $('confirmation-summary').innerHTML = s.items.map(i=>`<div class="confirmation-item"><span>${escape(i.product.name_zh)} ×${i.quantity}</span><strong>${money(i.product.price_cents*i.quantity)}</strong></div>`).join('')+`<div class="confirmation-total"><span>合計（已含模擬費用）</span><strong>${money(s.validation.total_cents)}</strong></div>`;
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

refresh().then(async()=>{const trace=await request('/api/trace');for(const e of trace.events.filter(e=>e.kind==='tool').slice(-40))logTool(e.payload.name,e.payload.result);$('run-status').textContent='準備好聽你說';}).catch(error=>notify('載入失敗：'+error.message));
