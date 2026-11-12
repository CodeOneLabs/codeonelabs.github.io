(()=>{
const L=window.BBL||{};const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
let ac=null,soundOn=true;
function audio(){if(!ac){try{ac=new (window.AudioContext||window.webkitAudioContext)()}catch(e){}}if(ac&&ac.state==='suspended')ac.resume();return ac}
function blip(f,d,type,vol){if(!soundOn)return;const a=audio();if(!a)return;const o=a.createOscillator(),g=a.createGain();o.type=type||'square';o.frequency.setValueAtTime(f,a.currentTime);
o.frequency.exponentialRampToValueAtTime(Math.max(40,f*.45),a.currentTime+d);g.gain.setValueAtTime(vol||.05,a.currentTime);g.gain.exponentialRampToValueAtTime(.0001,a.currentTime+d);o.connect(g).connect(a.destination);o.start();o.stop(a.currentTime+d)}
function cellsOf(hex){const out=[];let v=BigInt('0x'+hex);for(let i=0;v>0n;i++,v>>=1n)if(v&1n)out.push(i);return out}
const AIM={1:(x,y)=>[[x,y]],2:(x,y)=>[...Array(8)].map((_,i)=>[i,y]),3:(x,y)=>[...Array(8)].map((_,i)=>[x,i]),
4:(x,y)=>[...Array(8)].flatMap((_,i)=>[[i,y],[x,i]]),5:(x,y)=>[-1,0,1].flatMap(a=>[-1,0,1].map(b=>[x+a,y+b])),
6:(x,y)=>[...Array(15)].flatMap((_,k)=>{const i=k-7;return[[x+i,y+i],[x+i,y-i]]})};

class Board{
 constructor(root){this.root=root;this.el=root.querySelector('.board');this.pads=[];this.px=3;this.py=4;this.playing=false;this.data=null;
  const led=(root.dataset.led||'').split(',');
  for(let i=0;i<64;i++){const p=document.createElement('div');p.className='pad';p.innerHTML='<i class="l"></i><i class="w"></i>';
   const ch=(led[i>>3]||'')[i&7];const a={'1':.3,'2':.6,'3':1}[ch];if(a)p.style.setProperty('--a',a);p.dataset.i=i;this.el.appendChild(p);this.pads.push(p)}
  this.el.addEventListener('pointerdown',e=>{const p=e.target.closest('.pad');if(!p)return;e.preventDefault();this.tap(+p.dataset.i)});
  this.ui=root.querySelector('.bb-ui');this.stat=root.querySelector('.bb-stat');
  if(this.ui)this.setupUI();
  if(root.dataset.demo&&!reduce)this.load().then(()=>{this.mode='demo';this.start(0)});
 }
 led(on){this.pads.forEach(p=>p.querySelector('.l').style.opacity=on?'':'0')}
 flash(cells,cls,ms){cells.forEach(i=>{const p=this.pads[i];if(!p)return;p.classList.add(cls);clearTimeout(p._t);p._t=setTimeout(()=>p.classList.remove(cls),ms||70)})}
 ripple(i){const x=i&7,y=i>>3;const cross=[];for(let k=0;k<8;k++){cross.push(y*8+k,k*8+x)}this.flash(cross,'boom',90);blip(520+x*40,.12,'square',.04);
  for(let r=1;r<9;r++)setTimeout(()=>{const ring=[];for(let j=0;j<64;j++){const d=Math.max(Math.abs((j&7)-x),Math.abs((j>>3)-y));if(d===r)ring.push(j)}this.flash(ring,'ring',80)},r*45)}
 tap(i){audio();this.ripple(i)}
 async load(){if(this.data)return this.data;const r=await fetch(this.root.dataset.src);this.data=await r.json();
  for(const k in this.data.tiers){this.data.tiers[k].hits.forEach(h=>h.cells=cellsOf(h[1]))}return this.data}
 setupUI(){const ui=this.ui;this.tier=this.root.dataset.tier||'extreme';
  ui.querySelectorAll('[data-tier]').forEach(b=>b.onclick=()=>{this.tier=b.dataset.tier;ui.querySelectorAll('[data-tier]').forEach(x=>x.classList.toggle('on',x===b));if(this.playing)this.start(this.fromMs)});
  this.sel=ui.querySelector('select');
  ui.querySelector('.play').onclick=()=>{audio();this.playing?this.stop():this.start(this.sel?+this.sel.value:0)};
  const snd=ui.querySelector('.snd');if(snd)snd.onclick=()=>{soundOn=!soundOn;snd.classList.toggle('on',soundOn)};
  document.querySelectorAll('[data-seek]').forEach(b=>b.onclick=()=>{if(this.sel)this.sel.value=b.dataset.seek;audio();this.start(+b.dataset.seek);this.root.scrollIntoView({behavior:'smooth',block:'center'})});
  document.querySelectorAll('[data-playtier]').forEach(b=>b.onclick=()=>{const t=ui.querySelector('[data-tier="'+b.dataset.playtier+'"]');if(t)t.click();audio();this.start(0);this.root.scrollIntoView({behavior:'smooth',block:'center'})});
 }
 async start(fromMs){await this.load();this.stop(true);this.fromMs=fromMs||0;const tier=this.data.tiers[this.mode==='demo'?'extreme':this.tier];
  this.hits=tier.hits;this.lead=tier.lead;this.i=0;while(this.i<this.hits.length&&this.hits[this.i][0]<this.fromMs)this.i++;
  this.resolved=new Map();this.nHit=0;this.nDodge=0;this.playing=true;if(this.mode!=='demo'){this.mode='play';this.px=3;this.py=4}
  this.endMs=this.mode==='demo'?this.data.demoEnd:(this.hits.length?this.hits[this.hits.length-1][0]+900:0);
  this.led(false);this.t0=performance.now()-(this.fromMs-this.lead-300);const pb=this.ui&&this.ui.querySelector('.play');if(pb)pb.textContent=L.stop||'STOP';this.root.classList.add('on');
  const loop=()=>{if(!this.playing)return;this.frame(performance.now()-this.t0);this.raf=requestAnimationFrame(loop)};loop()}
 stop(quiet){this.playing=false;cancelAnimationFrame(this.raf);this.pads.forEach(p=>{p.classList.remove('warn','hot');p.style.removeProperty('--w')});
  if(!quiet)this.led(true);
  const pb=this.ui&&this.ui.querySelector('.play');if(pb)pb.textContent=L.play||'PLAY';this.root.classList.remove('on')}
 resolve(h){let c=this.resolved.get(h);if(c)return c;c=h.cells.slice();const aim=h[2]||0,hole=h[3]||0;
  if(aim&&AIM[aim])AIM[aim](this.px,this.py).forEach(([x,y])=>{if(x>=0&&x<8&&y>=0&&y<8)c.push(y*8+x)});
  if(hole){const hx=Math.min(8-hole,Math.max(0,this.px-((h[4]||0)<0?hole-1:0))),hy=Math.min(8-hole,Math.max(0,this.py-((h[5]||0)<0?hole-1:0)));
   c=[];for(let j=0;j<64;j++){const x=j&7,y=j>>3;if(!(x>=hx&&x<hx+hole&&y>=hy&&y<hy+hole))c.push(j)}}
  this.resolved.set(h,c);return c}
 frame(t){const w=new Float32Array(64);
  for(let k=this.i;k<this.hits.length;k++){const h=this.hits[k];if(h[0]>t+this.lead)break;
   if(h[0]<=t){if(k===this.i){const cells=this.resolve(h);this.flash(cells,'boom',70);
     blip(300+cells.length*6,.06,'square',this.mode==='demo'?.02:.03);this.i++}continue}
   const p=1-(h[0]-t)/this.lead;this.resolve(h).forEach(c=>{if(p>w[c])w[c]=p})}
  for(let c=0;c<64;c++){const p=this.pads[c];if(w[c]>0){p.classList.add('warn');p.classList.toggle('hot',w[c]>.8);p.style.setProperty('--w',w[c].toFixed(3))}else if(p.classList.contains('warn')){p.classList.remove('warn','hot')}}
  if(t>this.endMs){if(this.mode==='demo'){this.start(0)}else{this.stop()}}}
}
document.querySelectorAll('.bb').forEach(r=>new Board(r));
document.querySelectorAll('.secret,.secret-line').forEach(el=>{const open=()=>el.classList.add('shown');el.addEventListener('click',open);el.addEventListener('keydown',e=>{if(e.key==='Enter')open()})});
const ra=document.querySelector('.reveal-all');if(ra)ra.onclick=()=>document.querySelectorAll('.secret,.secret-line').forEach(el=>el.classList.add('shown'));
// small LED marks: twinkle the header logo, city filter glow is CSS
})();
