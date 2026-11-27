"""Authenticated artifact download; credentials and signed URLs never enter logs."""
import sys,subprocess,urllib.request,urllib.error,zipfile,io,concurrent.futures
from pathlib import Path
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**k):return None
artifact,destination=sys.argv[1:3]
token=subprocess.check_output(['gh','auth','token'],text=True).strip()
req=urllib.request.Request(f'https://api.github.com/repos/ainikitakhajomia/linea-reel-kit/actions/artifacts/{artifact}/zip',headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json'})
try:urllib.request.build_opener(NoRedirect).open(req,timeout=30);raise RuntimeError('Expected redirect')
except urllib.error.HTTPError as e:
 if e.code!=302:raise RuntimeError('Artifact access failed') from None
 signed=e.headers['Location']
del token,req
with urllib.request.urlopen(urllib.request.Request(signed,method='HEAD'),timeout=30) as r:size=int(r.headers['Content-Length'])
print('Recovering',artifact,size,'bytes',flush=True)
chunk=2*1024*1024
parts=list(range(0,size,chunk))
def fetch(start):
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(signed,headers={'Range':f'bytes={start}-{min(start+chunk,size)-1}'}),timeout=40) as r:
    if r.status!=206:raise RuntimeError('Expected partial download')
    return r.read()
  except Exception:
   if attempt==2:raise RuntimeError('Artifact chunk failed') from None
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 data=bytearray()
 for i,part in enumerate(pool.map(fetch,parts)):
  data.extend(part)
  if i%10==0:print('Recovered',len(data),'/',size,flush=True)
with zipfile.ZipFile(io.BytesIO(data)) as z:
 root=Path(destination).resolve()
 for n in z.namelist():
  if n.endswith('/'):continue
  # Preserve all unique useful outputs; skip duplicate packaged site.
  if n.startswith('out/site/'):continue
  target=(root/n).resolve()
  if not target.is_relative_to(root):raise ValueError('Unsafe archive path')
  target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(n))
print('Recovered to',destination,flush=True)
