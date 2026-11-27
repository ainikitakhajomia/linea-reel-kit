// Lightweight source guard before public pushes. Report paths/rules, never matched secrets.
import {spawnSync} from 'node:child_process';
import {readFile} from 'node:fs/promises';
const listing=spawnSync('git',['ls-files','--cached','--others','--exclude-standard','-z'],{encoding:'utf8'});
if(listing.status)throw new Error('Cannot enumerate public source');
const rules=[['private-key',/-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----/],['github-token',/gh[pousr]_[A-Za-z0-9]{25,}/],['aws-access-id',/AKIA[0-9A-Z]{16}/],['api-secret',/sk-[A-Za-z0-9_-]{32,}/]];
const problems=[];let checked=0;
for(const path of new Set(listing.stdout.split('\0').filter(Boolean))){
 if(/(^|\/)(\.env(?:\..*)?|id_rsa|id_ed25519)$/.test(path)||/\.(pem|p12|pfx)$/.test(path))problems.push({path,rule:'credential-file'});
 if(/\.(mp4|mov|wav|mp3|m4a|png|jpe?g|webp)$/i.test(path))problems.push({path,rule:'media-requires-explicit-license-and-privacy-review'});
 if(!/\.(mjs|js|py|tsx?|json|md|html|css|yml|txt)$/.test(path))continue;
 const content=await readFile(path,'utf8');checked++;
 for(const [rule,pattern] of rules)if(pattern.test(content))problems.push({path,rule});
}
console.log(JSON.stringify({checkedSourceFiles:checked,findings:problems,scope:'Pattern/file guard only. Review provenance and privacy separately; absence of a signature is not proof.'},null,2));
if(problems.length)process.exitCode=1;
