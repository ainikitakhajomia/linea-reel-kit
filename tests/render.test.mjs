import {test} from 'node:test';
import assert from 'node:assert/strict';
import {validateJob} from '../src/render.mjs';
import {readFile} from 'node:fs/promises';
test('untrusted media stays local; invalid dimensions/times rejected',()=>{
 const good={duration:2,width:720,height:1280,fps:30,video:'jobs/demo/edited.mp4'};assert.equal(validateJob({...good}).width,720);
 for(const video of ['../secret','https://example.com/a.mp4','/etc/passwd','foo\\bar'])assert.throws(()=>validateJob({...good,video}));
 for(const duration of [NaN,0,-1,Infinity,601])assert.throws(()=>validateJob({...good,duration}));
 assert.throws(()=>validateJob({...good,width:721}));assert.throws(()=>validateJob({...good,effects:[{id:'x',start:-1,duration:1}]}));
});
test('67 unique recipes link real inventoried references and disclose status',async()=>{const catalog=JSON.parse(await readFile(new URL('../src/catalog.json',import.meta.url)));assert.equal(catalog.length,67);assert.equal(new Set(catalog.map(e=>e.id)).size,67);for(const e of catalog){assert.equal(e.status,'independent-baseline');assert.match(e.reference,/^https:\/\/justyn.ai\/reel-kit\/media\/fx\//);assert.match(e.license,/MIT/);}});
