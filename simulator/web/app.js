'use strict';
const $=id=>document.getElementById(id);
const headings=['↑ 북','→ 동','↓ 남','← 서'], arrows=['↑','→','↓','←'];
let cases=[],config=null,session=null,frames=[],cursor=0,running=false,busy=false,tool='inspect',timer=null;
const clone=x=>JSON.parse(JSON.stringify(x));
function message(text,error=false){$('message').textContent=text;$('message').classList.toggle('error',error);}
async function api(path,data){const response=await fetch('/api/'+path,data?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}:{});const body=await response.json();if(!response.ok)throw new Error(body.error||'요청 실패');return body;}
function pause(){running=false;clearTimeout(timer);timer=null;render();}
function coordSet(points){return new Set((points||[]).map(p=>p.join(',')));}
function td(row,text){const el=document.createElement('td');el.textContent=text;row.appendChild(el);}
function initialFrame(c){return{tick:0,position:c.start,direction:c.direction,dust:c.dust,cleaned:[],mopped:[],controller:null,sensors:null,changes:[],collision:false};}
function clearEvaluation(){$('result').value='';$('notes').value='';$('eval-ticks').value='';$('evaluation-status').textContent='평가 대기';}
async function useConfig(candidate){
 if(busy)return;pause();busy=true;render();
 try{const result=await api('new',{config:candidate,replace:session});config=clone(result.config);session=result.id;frames=[result.frame];cursor=0;clearEvaluation();$('map-name').value=config.name;$('direction').value=config.direction;$('limit').value=config.max_ticks;message('준비되었습니다. 시작 또는 한 틱 실행을 선택하세요.');}
 catch(error){message(error.message,true);}
 finally{busy=false;render();}
}
function render(){
 if(!config)return;
 const frame=frames[cursor]||initialFrame(config),c=frame.controller,atLimit=frames.length-1>=config.max_ticks;
 $('tick').replaceChildren(document.createTextNode(String(frame.tick).padStart(3,'0')+' '));let small=document.createElement('small');small.textContent='/ '+config.max_ticks;$('tick').appendChild(small);
 $('run-status').textContent=busy?'처리 중':running?'실행 중':atLimit?'틱 제한 도달':cursor<frames.length-1?'과거 기록':'준비';
 $('position').textContent=frame.position.join(', ');$('heading').textContent=headings[frame.direction];
 $('state-badge').textContent=c?c.state:'INITIAL';$('cleaner').textContent=c?(c.cleaner.enabled?(c.cleaner.power===2?'강화 · 물걸레':'청소 · 물걸레'):'중지'):'대기';
 $('timer').textContent=c?c.boost_remaining+' ticks':'—';
 $('transition').textContent=c?`${c.previous_state} → ${c.state}${frame.collision?' · 이동 차단':''}`:'첫 C 업데이트 전입니다.';
 let sensorOrigin=$('sensor-origin');if(!sensorOrigin){sensorOrigin=document.createElement('p');sensorOrigin.id='sensor-origin';sensorOrigin.className='hint';$('sensors').after(sensorOrigin);}
 const before=frames[Math.max(0,cursor-1)];sensorOrigin.textContent=c?`센서는 동작 전 (${before.position.join(', ')}) ${headings[before.direction]} 기준입니다.`:'센서는 첫 틱에서 관측합니다.';
 $('state-json').textContent=JSON.stringify(frame,null,2);
 $('sensors').replaceChildren();for(const [key,label]of [['front','전방'],['left','좌측'],['right','우측'],['dust','먼지']]){let span=document.createElement('span');span.className='sensor'+(frame.sensors?.[key]?' on':'');span.textContent=label+' '+(frame.sensors?frame.sensors[key]?'ON':'OFF':'—');$('sensors').appendChild(span);}
 const walls=coordSet(config.obstacles),dust=coordSet(frame.dust),cleaned=coordSet(frame.cleaned),mopped=coordSet(frame.mopped);
 $('grid').replaceChildren();for(let y=0;y<10;y++)for(let x=0;x<10;x++){
  const key=x+','+y,cell=document.createElement('button');cell.type='button';cell.className='cell';cell.setAttribute('role','gridcell');cell.dataset.x=x;cell.dataset.y=y;
  let label=`(${x}, ${y}) `;
  if(walls.has(key)){cell.classList.add('wall');cell.textContent='▧';label+='장애물';}
  else if(dust.has(key)){cell.classList.add('dust');cell.textContent='✦';label+='먼지';}
  else if(cleaned.has(key)){cell.classList.add('cleaned');label+='청소 완료';}else label+='빈 칸';
  if(mopped.has(key))cell.classList.add('mopped');
  const pos=frame.position;if(x===pos[0]&&y===pos[1]){const bot=document.createElement('span');bot.className='bot';bot.textContent=arrows[frame.direction];cell.appendChild(bot);label+=' / 로봇';}
  const coordinate=document.createElement('span');coordinate.className='coord';coordinate.textContent=key;cell.appendChild(coordinate);cell.setAttribute('aria-label',label);cell.disabled=running||busy;cell.addEventListener('click',()=>edit(x,y));$('grid').appendChild(cell);
 }
 $('history-slider').max=frames.length-1;$('history-slider').value=cursor;$('history-label').textContent=cursor+' / '+(frames.length-1);
 $('history').replaceChildren();for(const f of [...frames].reverse()){
  const row=document.createElement('tr');row.classList.toggle('active',f.tick===cursor);row.addEventListener('click',()=>{if(!busy){pause();cursor=f.tick;render();}});const a=f.controller;
  td(row,f.tick.toString().padStart(3,'0'));td(row,f.position.join(', ')+' '+arrows[f.direction]);td(row,a?a.previous_state+' → '+a.state:'INITIAL');td(row,f.sensors?Object.values(f.sensors).join(' / '):'—');td(row,a?a.motor:'—');td(row,a?(a.cleaner.enabled?'ON ×'+a.cleaner.power:'OFF')+' / '+(a.cleaner.mop?'ON':'OFF'):'—');td(row,a?a.boost_remaining:'—');td(row,f.changes.join(', ')||'—');$('history').appendChild(row);
 }
 $('start').disabled=busy||running||(atLimit&&cursor===frames.length-1);$('pause').disabled=!running;$('step').disabled=busy||running||(atLimit&&cursor===frames.length-1);
 for(const id of ['reset','restart','scenario','reload','clear','direction','limit','save-map','import-map','save-evaluation','export-map','export-trace'])$(id).disabled=busy||running;
 $('previous').disabled=busy||cursor===0;$('next').disabled=busy||cursor===frames.length-1;$('history-slider').disabled=busy||running;
 document.querySelectorAll('[data-tool]').forEach(b=>{b.disabled=busy||running;b.classList.toggle('selected',b.dataset.tool===tool);});
 $('requirements').replaceChildren();for(const requirement of config.requirements||['사용자 지도']){const tag=document.createElement('span');tag.textContent=requirement;$('requirements').appendChild(tag);}
 $('expected').textContent=config.expected||'사용자 정의 지도입니다. 기대 동작을 P1 기준으로 검토하고 수동 평가하세요.';
}
async function step(){
 if(busy||!config)return;busy=true;render();
 try{if(cursor<frames.length-1)cursor++;else{const frame=await api('step',{id:session});frames.push(frame);cursor=frames.length-1;}
  if(frames.length-1>=config.max_ticks&&cursor===frames.length-1){running=false;message('틱 제한에 도달했습니다. 기록을 검토한 뒤 평가하세요.');}
 }catch(error){running=false;message(error.message,true);}finally{busy=false;render();}
}
async function loop(){if(!running)return;await step();if(running)timer=setTimeout(loop,Number($('speed').value));}
function start(){if(busy||running)return;running=true;message('실제 C 제어기로 실행 중입니다.');render();loop();}
async function edit(x,y){
 if(busy||running||tool==='inspect')return;
 const c=clone(config),key=x+','+y,has=(list)=>list.some(p=>p.join(',')===key),remove=list=>list.filter(p=>p.join(',')!==key);
 if(tool==='start'){if(has(c.obstacles))return message('장애물 위에는 시작점을 놓을 수 없습니다.',true);c.start=[x,y];}
 if(tool==='obstacle'){if(c.start.join(',')===key)return message('시작 위치에 장애물을 놓을 수 없습니다.',true);if(has(c.obstacles))c.obstacles=remove(c.obstacles);else{c.obstacles.push([x,y]);c.dust=remove(c.dust);}}
 if(tool==='dust'){if(has(c.obstacles))return message('장애물 칸에는 먼지를 놓을 수 없습니다.',true);if(has(c.dust))c.dust=remove(c.dust);else c.dust.push([x,y]);}
 if(tool==='erase'){c.obstacles=remove(c.obstacles);c.dust=remove(c.dust);}
 c.id='CUSTOM';c.expected='편집된 사용자 지도입니다. P1 동작을 기준으로 수동 평가하세요.';c.name='사용자 지도';await useConfig(c);
}
function download(name,data){const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
async function refreshCases(){cases=await api('scenarios');$('scenario').replaceChildren();for(const c of cases){const option=document.createElement('option');option.value=c.id;option.textContent=c.id+' · '+c.name;$('scenario').appendChild(option);}$('scenario-count').textContent=cases.length+' CASES';}
function selected(){return cases.find(c=>c.id===$('scenario').value);}
$('start').onclick=start;$('pause').onclick=pause;$('step').onclick=step;
$('reset').onclick=()=>useConfig(config);$('restart').onclick=async()=>{await useConfig(config);start();};
$('previous').onclick=()=>{pause();cursor=Math.max(0,cursor-1);render();};$('next').onclick=()=>{pause();cursor=Math.min(frames.length-1,cursor+1);render();};
$('history-slider').oninput=()=>{const target=Number($('history-slider').value);pause();cursor=target;render();};
$('scenario').onchange=()=>useConfig(selected());$('reload').onclick=()=>useConfig(selected());
$('direction').onchange=()=>useConfig({...clone(config),direction:Number($('direction').value)});
$('limit').onchange=()=>useConfig({...clone(config),max_ticks:Number($('limit').value)});
$('clear').onclick=()=>useConfig({...clone(config),id:'CUSTOM',name:'빈 지도',obstacles:[],dust:[],start:[4,4],expected:'빈 지도입니다. 경계 회피와 청소·물걸레 동작을 확인하세요.'});
document.querySelectorAll('[data-tool]').forEach(button=>button.onclick=()=>{tool=button.dataset.tool;render();});
$('save-map').onclick=async()=>{try{const saved=await api('scenarios',{config:{...config,name:$('map-name').value}});await refreshCases();$('scenario').value=saved.id;await useConfig(saved);message('새 시나리오를 로컬에 저장했습니다.');}catch(error){message(error.message,true);}};
$('export-map').onclick=()=>download('rvc-map.json',{...config,name:$('map-name').value});
$('import-map').onchange=async event=>{try{const file=event.target.files[0];if(!file)return;if(file.size>65536)throw new Error('지도 파일이 너무 큽니다.');const data=JSON.parse(await file.text());await useConfig(data.config||data);}catch(error){message('불러오기 실패: '+error.message,true);}finally{event.target.value='';}};
$('export-trace').onclick=async()=>{try{download('rvc-trace.json',await api('trace/'+session));}catch(error){message(error.message,true);}};
$('save-evaluation').onclick=async()=>{try{const evaluation={result:$('result').value,evaluator:$('evaluator').value,notes:$('notes').value,ticks:$('eval-ticks').value};await api('evaluate',{id:session,evaluation});$('evaluation-status').textContent=evaluation.result;message('평가와 전체 실행 기록을 simulator/saved에 저장했습니다.');}catch(error){message(error.message,true);}};
(async()=>{try{await refreshCases();await useConfig(cases[0]);}catch(error){message('서버 연결 실패: '+error.message,true);}})();
