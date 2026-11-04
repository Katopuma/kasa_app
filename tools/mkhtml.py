import re,shutil,os,glob
src=open('web/kasa.html').read()
s=src
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a[:80],s.count(a)); s=s.replace(a,b)
# fonts: local files only
FD='.cache/fonts/fontsource-%s/package/files/'
ranges={'cyrillic':'U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116','latin':'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD','latin-ext':'U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF'}
faces=[]
for fam,pkg,ws in [('Onest','onest-5.3.1',[400,500,600,700]),('Unbounded','unbounded-5.3.0',[500,700])]:
    for w in ws:
        for sub,rg in ranges.items():
            fn=f'{fam.lower()}-{sub}-{w}-normal.woff2'
            shutil.copy(FD%pkg+fn,'build/assets/fonts/'+fn)
            faces.append(f'@font-face{{font-family:"{fam}";font-style:normal;font-weight:{w};font-display:swap;src:url(fonts/{fn}) format("woff2");unicode-range:{rg}}}')
rep('<link rel="preconnect" href="https://fonts.googleapis.com">\n','')
s=re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\n','',s)
rep('<style>\n','<style>\n'+'\n'.join(faces)+'\n',1)
rep('<title>Каса Pre-release</title>','<title>Каса</title>')
rep('''    <span class="pill" style="align-self:flex-start;background:var(--accent-soft);color:var(--accent)">Pre-release</span>\n''','')
# theme: follow native night flag in auto mode, and tint system bars
rep('function isDark(){return themePref==="dark"||(themePref==="auto"&&matchMedia("(prefers-color-scheme: dark)").matches)}',
 'let nativeNight=null;try{nativeNight=window.KasaNative?KasaNative.isNight():null}catch(e){}\nfunction isDark(){return themePref==="dark"||(themePref==="auto"&&(nativeNight!=null?nativeNight:matchMedia("(prefers-color-scheme: dark)").matches))}\nwindow.onNativeNight=function(n){nativeNight=!!n;if(themePref==="auto"){applyTheme();render()}};')
rep('function applyTheme(){const el=document.documentElement;if(themePref==="auto")el.removeAttribute("data-theme");else el.setAttribute("data-theme",themePref)}',
 'function applyTheme(){const el=document.documentElement;const d=isDark();el.setAttribute("data-theme",d?"dark":"light");try{window.KasaNative&&KasaNative.setBars(d?"#161c42":"#ffffff",d?"#0d1230":"#f2effa",!d)}catch(e){}}')
# rates card text + backup card
rep('''<div class="hint">Сейчас: ${rd?`обновлены ${human(rd).toLowerCase()}`:"по умолчанию"}${S.rates&&S.rates.source?`, источник: ${esc(S.rates.source)}`:""}. Курс сверху соответствует официальному. Если меняете в обменнике по другому, впишите свой.</div>''',
'''<div class="hint">Сейчас: ${rd?`обновлены ${human(rd).toLowerCase()}`:"по умолчанию"}${S.rates&&S.rates.source?`, источник: ${esc(S.rates.source)}`:""}. Приложение само запрашивает официальный курс один раз в сутки, при первом открытии за день. Это единственное, что оно отправляет в интернет. Если меняете в обменнике по другому курсу, впишите свой, он продержится до следующего дня.</div>''')
rep('''  <form class="card" id="rateF"><h2>Курсы</h2>''','''  <div class="card"><h2>Резервная копия</h2>
    <div class="hint">Все записи хранятся только в памяти этого телефона. Если удалить приложение или сменить телефон, они пропадут. Сохраните копию, например, себе в «Избранное» мессенджера.</div>
    <div class="row" style="flex-wrap:wrap"><button class="btn primary" type="button" id="bkExport">Сохранить копию</button><button class="btn" type="button" id="bkShowImport">Восстановить из копии</button></div>
    ${bkImport?`<form class="field" id="bkF"><label for="bkText">Вставьте текст копии</label><textarea class="input" id="bkText" rows="5" style="font-size:13px"></textarea>
      <div class="hint">Восстановление заменит все текущие записи в приложении.</div>
      <div class="row"><button class="btn danger" type="submit">${bkArm?"Точно заменить всё":"Восстановить"}</button><button class="btn" type="button" id="bkCancel">Отмена</button></div></form>`:""}
  </div>
  <form class="card" id="rateF"><h2>Курсы</h2>''')
rep('''let recCur="RSD",''','''let bkImport=false,bkArm=false;\nlet recCur="RSD",''')
rep('''  if(t.id==="fab"){openSheet();return}''','''  if(t.id==="fab"){openSheet();return}
  if(t.id==="bkExport"){const txt=db._export();try{KasaNative.share(txt)}catch(e){navigator.clipboard&&navigator.clipboard.writeText(txt).then(()=>toast("Копия скопирована"),()=>toast("Не получилось сохранить копию"))}return}
  if(t.id==="bkShowImport"){bkImport=true;bkArm=false;renderPrefs();return}
  if(t.id==="bkCancel"){bkImport=false;bkArm=false;renderPrefs();return}''')
rep('''  else if(f.id==="txF")saveTx();''','''  else if(f.id==="txF")saveTx();
  else if(f.id==="bkF"){const raw=$("#bkText").value.trim();let obj;try{obj=JSON.parse(raw)}catch(err){toast("Это не похоже на копию Касы");return}
    if(!obj||typeof obj!=="object"||!obj.kasa||typeof obj.data!=="object"){toast("Это не похоже на копию Касы");return}
    if(!bkArm){bkArm=true;const v=$("#bkText").value;renderPrefs();$("#bkText").value=v;return}
    try{db._import(obj.data);bkImport=false;bkArm=false;toast("Данные восстановлены")}catch(err){toast("Не получилось восстановить")}}''')
# replace data layer
a=s.index('async function start(){'); b=s.index('applyTheme();\nstart();')
start_new='''// Local store: one JSON file inside the app's private storage on this phone. Nothing leaves the device except the daily rate request.
function makeLocalDb(){
  let data={};
  const load=()=>{try{const t=window.KasaNative?KasaNative.load():localStorage.getItem("kasa-data");data=t?JSON.parse(t):{}}catch(e){data={}}};
  const persist=()=>{const t=JSON.stringify(data);let ok=false;try{ok=window.KasaNative?KasaNative.save(t):(localStorage.setItem("kasa-data",t),true)}catch(e){}if(!ok)throw{code:"unavailable"}};
  load();
  const subs=new Set();const emit=()=>subs.forEach(f=>f());
  const clone=v=>v===undefined?undefined:JSON.parse(JSON.stringify(v));
  const rid=()=>Date.now().toString(36)+Math.random().toString(36).slice(2,8);
  const meta={fromCache:false,hasPendingWrites:false};
  const snap=p=>({id:p.split("/").pop(),exists:Object.prototype.hasOwnProperty.call(data,p),data:()=>clone(data[p]),metadata:meta});
  const merge=(a,b)=>{const o=Object.assign({},a);for(const k in b){const v=b[k];o[k]=v&&typeof v==="object"&&!Array.isArray(v)&&a&&typeof a[k]==="object"&&!Array.isArray(a[k])?merge(a[k],v):v}return o};
  const listen=f=>{subs.add(f);setTimeout(f,0);return()=>subs.delete(f)};
  const docRef=p=>({id:p.split("/").pop(),path:p,
    get:async()=>snap(p),
    set:async v=>{const old=data[p];data[p]=clone(v);try{persist()}catch(e){data[p]=old;throw e}emit()},
    update:async v=>{if(!(p in data))throw{code:"invalid_argument"};const old=data[p];data[p]=merge(old,clone(v));try{persist()}catch(e){data[p]=old;throw e}emit()},
    delete:async()=>{const old=data[p];delete data[p];try{persist()}catch(e){data[p]=old;throw e}emit()},
    onSnapshot:(next)=>listen(()=>next(snap(p))),
    collection:sub=>colRef(p+"/"+sub)});
  const colRef=p=>({path:p,
    doc:id=>docRef(p+"/"+(id||rid())),
    add:async v=>{const r=docRef(p+"/"+rid());await r.set(v);return r},
    onSnapshot:(next)=>listen(()=>{const pre=p+"/";const docs=Object.keys(data).filter(k=>k.startsWith(pre)&&k.indexOf("/",pre.length)<0).sort().map(snap);next({docs,size:docs.length,empty:!docs.length,metadata:meta,docChanges:()=>[]})})});
  return {doc:docRef,collection:colRef,
    _export:()=>JSON.stringify({kasa:1,exported:new Date().toISOString(),data}),
    _import:obj=>{const old=data;data=clone(obj);try{persist()}catch(e){data=old;throw e}emit()}};
}
// Daily official rates: fetched by the app itself, at most once per successful day.
let ratesAsked=false;
function refreshRates(){const r=S.rates;if(ratesAsked||!window.KasaNative)return;if(r&&r.fetched===today())return;ratesAsked=true;try{KasaNative.fetchRates()}catch(e){}}
window.onNativeRates=function(body,src){let RSD,RUB;try{const j=JSON.parse(body);
    if(j.rates){RSD=+j.rates.RSD;RUB=+j.rates.RUB}else if(j.eur){RSD=+j.eur.rsd;RUB=+j.eur.rub}}catch(e){}
  if(!(RSD>0&&RUB>0))return;
  const old=S.rates;const prev=old&&old.date&&old.date!==today()?{RSD:num(old.RSD),RUB:num(old.RUB),date:old.date}:(old&&old.prev)||null;
  const body2={RSD:Math.round(RSD*10000)/10000,RUB:Math.round(RUB*10000)/10000,date:today(),fetched:today(),source:src||"официальный курс"};if(prev)body2.prev=prev;
  db.doc("budget/rates").set(body2).catch(()=>{})};
window.kasaBack=function(){if($("#sheetHost").innerHTML){closeSheet();return}
  const tab=(location.hash||"#overview").slice(1);if(tab!=="overview"){location.hash="#overview";return}
  try{KasaNative.exit()}catch(e){}};
async function start(){
  route();
  db=makeLocalDb();
  let first=true;
  const done=()=>{if(first&&S.loaded.s&&S.loaded.r&&S.loaded.t&&S.loaded.c&&S.loaded.d){first=false;refreshRates()}};
  db.doc("budget/settings").onSnapshot(s=>{S.settings=s.exists?s.data():null;S.loaded.s=true;done();render()});
  db.doc("budget/rates").onSnapshot(s=>{S.rates=s.exists?s.data():null;S.loaded.r=true;done();render()});
  db.collection("tx").onSnapshot(q=>{S.tx=q.docs.map(d=>Object.assign({id:d.id},d.data()));S.loaded.t=true;done();render()});
  db.collection("debts").onSnapshot(q=>{S.debts=q.docs.map(d=>Object.assign({id:d.id},d.data()));S.loaded.d=true;done();render()});
  db.collection("recurring").onSnapshot(q=>{S.rec=q.docs.map(d=>Object.assign({id:d.id},d.data()));S.loaded.c=true;done();render()});
}
'''
s=s[:a]+start_new+s[b:]
rep('<div class="status" id="status">Загружаю данные…</div>','<div class="status" id="status">Открываю…</div>')
head='''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="default-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'none'">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
</head><body>
'''
s=head+s+'\n</body></html>\n'
rep('.btn{border:1px solid var(--line);','.btn{text-decoration:none;border:1px solid var(--line);')
rep('for(const x of bills){if(x.st==="overdue")alerts.push(["bad",`Просрочен платёж: ${x.name}`,`${fmt(+x.amount,x.currency)}, срок был ${human(x.due).toLowerCase()}.`]);',
 'for(const x of bills){const am=x.variable&&!x.amount?"сумма ещё не введена":fmt(+x.amount,x.currency);if(x.st==="overdue")alerts.push(["bad",`Просрочен платёж: ${x.name}`,`${am}, срок был ${human(x.due).toLowerCase()}.`]);')
rep('else if(x.st==="soon")alerts.push(["warn",`Скоро платёж: ${x.name}`,`${fmt(+x.amount,x.currency)}, ${human(x.due).toLowerCase()}.`]);}',
 'else if(x.st==="soon")alerts.push(["warn",`Скоро платёж: ${x.name}`,`${am}, ${human(x.due).toLowerCase()}.`]);}')
open('build/assets/index.html','w').write(s)
print(len(s))
