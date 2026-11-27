// Isolated Linux only. Verify deployed assets and real playback in a clean browser.
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
const url=process.argv[2];if(!/^https:\/\//.test(url||''))throw new Error('Pass public HTTPS preview URL');
await mkdir('out',{recursive:true});
const browser=await chromium.launch();const context=await browser.newContext({viewport:{width:1440,height:1000}}),page=await context.newPage(),errors=[],requests=[];
page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400&&!r.url().endsWith('favicon.ico'))requests.push({url:r.url(),status:r.status()});});
try{
 await page.goto(url,{waitUntil:'networkidle'});await page.waitForSelector('.card');assert.equal(await page.locator('.card').count(),67);
 let played=0;
 for(let i=0;i<67;i++){
  const card=page.locator('.card').nth(i);await card.scrollIntoViewIfNeeded();await page.waitForTimeout(55);const first=await card.locator('canvas').evaluate(c=>c.toDataURL());const id=await card.getAttribute('data-effect');await page.waitForFunction(({id,first})=>document.querySelector(`[data-effect="${id}"] canvas`).toDataURL()!==first,{id,first},{timeout:3500});played++;
 }
 await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:'out/hosted-library.png'});
 await page.locator('#search').fill('orbit');assert.equal(await page.locator('.card').count(),1);await page.locator('.card').first().click();await page.locator('#dtext').fill('Een nieuw perspectief');await page.locator('#detailscrub').fill('1.2');await page.screenshot({path:'out/hosted-inspector.png'});await page.locator('#close').click();await page.locator('#search').fill('');
 const response=await context.request.get(new URL('public/demos/manifest.json',url));let demos=[];
 if(response.ok()){
  demos=await response.json();assert.equal(demos.length,10);await page.locator('#demobutton').click();await page.waitForSelector('.democard');
  for(const video of await page.locator('.democard video').all()){
   await video.scrollIntoViewIfNeeded();await video.evaluate(async v=>{v.muted=true;await v.play();});await page.waitForTimeout(180);assert.ok(await video.evaluate(v=>v.currentTime>0&&v.videoWidth>0),'Hosted demo must decode and play');await video.evaluate(v=>v.pause());
  }
  await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:'out/hosted-demos.png'});
 }
 await page.locator('#librarybutton').click();await page.setViewportSize({width:390,height:844});await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:'out/hosted-mobile.png'});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 assert.equal(errors.length,0,errors.join('\n'));assert.equal(requests.length,0,JSON.stringify(requests));await writeFile('out/hosted-validation.json',JSON.stringify({url,effectsVisible:67,effectsPlayed:played,demosPlayed:demos.length,pageErrors:errors,failedRequests:requests},null,2));console.log(`Public preview verified: ${played} animated cards, ${demos.length} films`);
}catch(error){await page.screenshot({path:'out/hosted-failure.png',fullPage:true});await writeFile('out/hosted-failure.json',JSON.stringify({error:error.message,pageErrors:errors,failedRequests:requests},null,2));throw error;}finally{await context.close();await browser.close();}
