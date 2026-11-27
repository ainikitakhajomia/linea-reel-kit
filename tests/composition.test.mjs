import {test} from 'node:test';
import assert from 'node:assert/strict';
import {cameraTransform,captionLines} from '../src/effects.mjs';
import {assetUrl} from '../src/media.mjs';
import {validateJob} from '../src/render.mjs';
test('dolly zoom separates background and foreground scale, with bounded end state',()=>{
 const start=cameraTransform('dolly-zoom',0,2),end=cameraTransform('dolly-zoom',2,2),late=cameraTransform('dolly-zoom',10,2);
 assert.equal(start.zoom,1);assert.equal(start.subjectZoom,1);assert.ok(end.zoom>1);assert.ok(end.subjectZoom<1);assert.deepEqual(late,end);
});
test('camera cuts settle while a punch holds, rather than sinusoidally drifting',()=>{
 assert.ok(cameraTransform('camera-transitions',0).x>500);
 assert.equal(cameraTransform('camera-transitions',1).x,0);
 assert.ok(cameraTransform('zoom-punch',1).zoom>1);
 assert.equal(cameraTransform('zoom-punch',1).zoom,cameraTransform('zoom-punch',2).zoom);
});
test('caption wrapping preserves word objects, sentence boundaries and at most two lines',()=>{
 const tokens='Dit is kort. Deze zin heeft veel meer lange woorden zonder een punt'.split(' ').map((text,i)=>({text,startMs:i*100,endMs:(i+1)*100}));
 const groups=captionLines(tokens,value=>value.length*10,100,3);
 assert.ok(groups.every(lines=>lines.length<=2&&lines.every(line=>line.length<=3)));
 assert.deepEqual(groups.flat(2),tokens);assert.equal(groups[0].at(-1).at(-1).text,'kort.');
});
test('transition media uses the same confined asset URLs',()=>{
 assert.equal(assetUrl('jobs/demo/next.png'),'/public/jobs/demo/next.png');
 for(const value of ['../private.mp4','/private.mp4','https://host/a.mp4','foo\\private'])assert.throws(()=>assetUrl(value));
});

test('transition and clean background inputs are validated before rendering',()=>{
 for(const key of ['previous','next','background']){
   assert.throws(()=>validateJob({duration:2,[key]:'../private.png'}));
   assert.equal(validateJob({duration:2,[key]:'jobs/demo/plate.png'})[key],'jobs/demo/plate.png');
 }
});
