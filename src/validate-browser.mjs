// Isolated Linux runner only: deterministic pixels, clean browser, UI and export-job parity.
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {createServer} from './server.mjs';
await mkdir('out',{recursive:true});
const browser=await chromium.launch(),server=await createServer(0),url=`http://127.0.0.1:${server.address().port}`;
const context=await browser.newContext({viewport:{width:1440,height:1000},acceptDownloads:true});
const page=await context.newPage(),errors=[],failedRequests=[],report=[],shots=[];
page.on('pageerror',e=>errors.push(e.message));page.on('response',response=>{if(response.status()>=400&&!response.url().includes('favicon'))failedRequests.push({url:response.url(),status:response.status()});});
try{
 await page.goto(url+'/src/stage.html');await page.waitForFunction(()=>window.ready);
 const catalog=JSON.parse(await readFile('src/catalog.json')),brand=JSON.parse(await readFile('brands/studio-linea.json'));
 for(const e of catalog){
  await page.evaluate(job=>window.setJob(job),{width:288,height:512,brand,duration:e.duration,effects:[{...e.parameters,id:e.id,start:0,duration:e.duration}]});
  const a=await page.evaluate(()=>window.frame(.15)),b=await page.evaluate(()=>window.frame(1.6)),again=await page.evaluate(()=>window.frame(.15));
  assert.equal(a,again,e.id+' not deterministic');assert.notEqual(a,b,e.id+' has no movement');assert.ok(Buffer.from(b,'base64').length>2000,e.id+' blank');
  shots.push({id:e.id,png:b});report.push({id:e.id,animated:true,deterministic:true,sha256:createHash('sha256').update(a).digest('hex')});
 }
 await page.goto(url);await page.waitForSelector('.card',{timeout:8000});assert.equal(await page.locator('.card').count(),67);assert.equal(failedRequests.length,0,JSON.stringify(failedRequests));
 const before=await page.locator('.card canvas').first().evaluate(c=>c.toDataURL());await page.waitForTimeout(250);assert.notEqual(await page.locator('.card canvas').first().evaluate(c=>c.toDataURL()),before,'Gallery must play');
 await page.locator('#pause').click();await page.waitForTimeout(100);const frozen=await page.locator('.card canvas').first().evaluate(c=>c.toDataURL());await page.waitForTimeout(150);assert.equal(await page.locator('.card canvas').first().evaluate(c=>c.toDataURL()),frozen);
 await page.locator('#search').fill('sszdgas');await page.waitForSelector('#empty:not(.hidden)');assert.equal(await page.locator('.card').count(),0);await page.locator('#clearfilters').click();assert.equal(await page.locator('.card').count(),67);
 for(const category of [...new Set(catalog.map(e=>e.category))]){await page.locator('#category').selectOption(category);assert.equal(await page.locator('.card').count(),catalog.filter(e=>e.category===category).length);}
 await page.locator('#category').selectOption('');await page.locator('.save').first().click();await page.locator('#favoritefilter').click();assert.equal(await page.locator('.card').count(),1);await page.reload();await page.waitForSelector('.card');assert.equal(await page.locator('.save[aria-pressed=true]').count(),1);
 await page.locator('#sort').selectOption('name');await page.locator('.card').first().click();await page.waitForSelector('dialog[open]');
 await page.locator('#dtext').fill('Jouw verhaal, helder verteld.');await page.locator('#dduration').fill('3.5');await page.locator('#dduration').dispatchEvent('change');await page.locator('#daccent').fill('#a43b40');
 await page.locator('summary').click();await page.locator('#dparams').fill('{');await page.locator('#applyparams').click();assert.ok((await page.locator('#paramstatus').textContent()).length>0);await page.locator('#dparams').fill(JSON.stringify({text:'Jouw verhaal, helder verteld.',duration:3.5,value:245}));await page.locator('#applyparams').click();
 await page.locator('#detailscrub').fill('0.8');await page.waitForTimeout(120);const detail=await page.locator('#detail').evaluate(c=>c.toDataURL().split(',')[1]);
 const downloadEvent=page.waitForEvent('download');await page.locator('#downloadjob').click();const download=await downloadEvent;const job=JSON.parse(await readFile(await download.path()));assert.equal(job.effects[0].text,'Jouw verhaal, helder verteld.');assert.equal(job.duration,3.5);assert.equal(job.brand.accent,'#a43b40');
 const stage=await context.newPage();await stage.goto(url+'/src/stage.html');await stage.waitForFunction(()=>window.ready);await stage.evaluate(j=>window.setJob(j),job);assert.equal(await stage.evaluate(()=>window.frame(.8)),detail,'Inspector/export stage pixel parity');await stage.close();
 await page.screenshot({path:'out/review-inspector.png'});await page.locator('#close').click();await page.locator('#sort').selectOption('catalog');await page.screenshot({path:'out/review-library.png'});
 await page.locator('#jobbutton').click();await page.locator('#playjob').click();assert.match(await page.locator('#jobstatus').textContent(),/Laad eerst/);await page.locator('#back').click();
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:'out/review-mobile.png'});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Mobile must not overflow');
 assert.equal(errors.length,0,errors.join('\n'));assert.equal(failedRequests.length,0,JSON.stringify(failedRequests));
 await page.setViewportSize({width:1800,height:1400});await page.setContent('<body style="margin:0;padding:25px;background:#f6f5f1;font:12px Arial"><h1>67 independent recipes · deterministic stage frames at 1.6 s</h1><div id="shots" style="display:grid;grid-template-columns:repeat(10,1fr);gap:14px"></div></body>');
 await page.evaluate(shots=>{for(const shot of shots){const card=document.createElement('div'),label=document.createElement('p'),img=document.createElement('img');label.textContent=shot.id;img.src='data:image/png;base64,'+shot.png;img.style.width='100%';card.append(label,img);document.querySelector('#shots').append(card);}},shots);await page.screenshot({path:'out/all-effects-contact-sheet.png',fullPage:true});
 await writeFile('out/browser-validation.json',JSON.stringify({effects:report,pageErrors:errors,failedRequests,checks:['clean session','67 cards','gallery playback and pause','all category counts','empty search','saved effect persistence','sort','text/color/duration/custom parameters','invalid JSON feedback','downloaded job pixel parity','mobile overflow']},null,2));console.log('67 animated recipes, clean UI, filtering, settings, exported-job pixel parity: passed');
}catch(error){await page.screenshot({path:'out/browser-failure.png',fullPage:true});await writeFile('out/browser-failure.json',JSON.stringify({error:error.message,pageErrors:errors,failedRequests},null,2));throw error;}finally{await context.close();await browser.close();await new Promise(r=>server.close(r));}
