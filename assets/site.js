(() => {
'use strict';
const toggle = document.querySelector('.nav-toggle');
const menu = document.getElementById('mobile-nav');
if (toggle && menu) {
  function setMenu(open) {
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? document.body.dataset.navClose || 'Close navigation' : document.body.dataset.navOpen || 'Open navigation');
    menu.hidden = !open;
  }
  toggle.addEventListener('click', () => setMenu(menu.hidden));
  menu.addEventListener('click', event => { if (event.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !menu.hidden) {
      setMenu(false);
      toggle.focus();
    }
  });
  window.addEventListener('resize', () => {
    if (!menu.hidden && !toggle.getClientRects().length) setMenu(false);
  });
}
const demo=document.querySelector('[data-frame-demo]');if(demo){const path=demo.querySelector('[data-plot]'),fps=demo.querySelector('[data-fps]'),peak=demo.querySelector('[data-peak]'),interpret=demo.querySelector('[data-interpret]'),buttons=[...demo.querySelectorAll('[data-mode]')];function setDemo(mode){const jitter=mode==='jitter';const base=(52*1000/60-4*53-3*35)/45;const rough=Array.from({length:52},(_,i)=>jitter?(i%13===0?53:i%17===0?35:base):(16.67+Math.sin(i*.73)*.65+Math.sin(i*1.23)*.35));const correction=1000/60-rough.reduce((a,b)=>a+b,0)/rough.length;const values=rough.map(v=>v+correction);const x=i=>18+i*(484/(values.length-1));const y=v=>205-(v/60)*180;path.setAttribute('d',values.map((v,i)=>(i?'L':'M')+x(i).toFixed(1)+' '+y(v).toFixed(1)).join(' '));path.setAttribute('stroke',jitter?'#ff727c':'#9ee0c0');fps.textContent='60';peak.textContent=Math.max(...values).toFixed(1)+' ms';interpret.textContent=(jitter?demo.dataset.jitter:demo.dataset.smooth)||(jitter?'Same illustrative average: 60 FPS. But intermittent 35–53 ms frames can cause perceptible hitches. Average FPS alone hides them.':'Same illustrative average: 60 FPS. Fairly even frame delivery gives more consistent motion. Both examples are synthetic, not measured game results.');buttons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===mode)))}buttons.forEach(b=>b.addEventListener('click',()=>setDemo(b.dataset.mode)));setDemo('smooth')}

})();
