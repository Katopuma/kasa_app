const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();let bad=0;
for(const w of [320,360,412]){const p=await b.newPage({viewport:{width:w,height:700}});
await p.addInitScript(()=>{const st={"budget/settings":{onboarded:true,salarySeeded:true,limit:90000,limitCur:"RSD",opening:{RSD:15000,EUR:500,RUB:1000}}};for(let i=0;i<30;i++)st["tx/t"+i]={type:"expense",amount:500+i,currency:"RSD",category:"Продукты",note:"Покупка "+i,date:"2026-11-0"+(1+i%3),created:"x"+i};
 st["recurring/rent"]={name:"Аренда квартиры",amount:500,share:.5,currency:"EUR",day:1,start:"2026-12-01",active:true};st["recurring/salary"]={name:"Зарплата",kind:"income",currency:"RSD",parts:[{day:5,amount:60000},{day:20,amount:90000}],active:true};st["debts/d"]={name:"Тестовый долг",amount:1000,currency:"RSD"};
 sessionStorage.setItem('s',JSON.stringify(st));window.KasaNative={isNight:()=>false,load:()=>sessionStorage.getItem('s'),save:t=>{sessionStorage.setItem('s',t);return true},setBars:()=>{},share:()=>{},exit:()=>{},fetchRates:()=>{}}});
for(const tab of ['overview','ops','bills','prefs']){await p.goto('file://'+process.cwd()+'/build/assets/index.html#'+tab);await p.waitForTimeout(400);
 await p.evaluate(()=>window.scrollTo(0,document.body.scrollHeight));await p.waitForTimeout(150);
 const r=await p.evaluate(()=>{const c=document.querySelector('.cat svg .kitty').getBoundingClientRect();const tb=document.querySelector('.tabbar').getBoundingClientRect();
   const top=Math.min(c.top,tb.top);const sec=document.querySelector('section:not([hidden])');
   const els=[...sec.querySelectorAll('*')].filter(e=>e.children.length===0||e.matches('button,input,.card'));let maxBottom=0,hit=[];
   for(const e of els){const r=e.getBoundingClientRect();if(!r.width||!r.height)continue;maxBottom=Math.max(maxBottom,r.bottom);
     if(r.bottom>c.top&&r.top<c.bottom&&r.right>c.left&&r.left<c.right)hit.push(e.tagName+'.'+e.className+':'+(e.textContent||'').trim().slice(0,20))}
   return {catTop:Math.round(c.top),barTop:Math.round(tb.top),contentBottom:Math.round(maxBottom),gap:Math.round(c.top-maxBottom),hit}});
 if(r.hit.length||r.gap<4)bad++;console.log(w,tab,JSON.stringify(r));
 if(w===360&&tab==='ops')await p.screenshot({path:'bottom-ops.png'});}
await p.close()}
console.log('problems:',bad);await b.close()})();
