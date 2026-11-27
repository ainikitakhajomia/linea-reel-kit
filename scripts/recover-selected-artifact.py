import io,json,subprocess,urllib.request,urllib.error,zipfile,pathlib,sys
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None
artifact=sys.argv[1];destination=pathlib.Path(sys.argv[2]);mode=sys.argv[3] if len(sys.argv)>3 else 'evidence'
token=subprocess.check_output(['gh','auth','token'],text=True).strip()
request=urllib.request.Request(f'https://api.github.com/repos/ainikitakhajomia/linea-reel-kit/actions/artifacts/{artifact}/zip',headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json'})
try:urllib.request.build_opener(NoRedirect).open(request,timeout=30);raise RuntimeError('Expected artifact redirect')
except urllib.error.HTTPError as error:
 if error.code!=302:raise RuntimeError(f'Artifact endpoint: {error.code}') from None
 signed=error.headers['Location']
del token,request
class Remote(io.RawIOBase):
 def __init__(self):
  self.pos=0
  with urllib.request.urlopen(urllib.request.Request(signed,method='HEAD'),timeout=30) as r:self.size=int(r.headers['Content-Length'])
 def seekable(self):return True
 def readable(self):return True
 def tell(self):return self.pos
 def seek(self,offset,whence=0):self.pos=offset if whence==0 else self.pos+offset if whence==1 else self.size+offset;return self.pos
 def read(self,size=-1):
  size=min(self.size-self.pos,size if size>=0 else self.size-self.pos)
  if size<=0:return b''
  start=self.pos
  with urllib.request.urlopen(urllib.request.Request(signed,headers={'Range':f'bytes={start}-{start+size-1}'}),timeout=60) as r:
   if r.status!=206:raise RuntimeError('Artifact server does not support partial reads')
   data=r.read()
  self.pos+=len(data);return data
with zipfile.ZipFile(Remote()) as z:
 names=z.namelist();selected=[n for n in names if (n.startswith('out/') and '/' not in n[4:] and n.endswith(('.mp4','.json'))) or (n.startswith('public/renders/') and n.endswith(('.mp4','.json','.jpg'))) or n=='out/portable-review/public/demo/source.mp4']
 print('Recovering',len(selected),'existing review files',flush=True)
 infos=[z.getinfo(n) for n in selected]
import concurrent.futures,struct,zlib
root=destination.resolve()
def recover(info):
 end=info.header_offset+30+len(info.filename.encode('utf-8'))+1024+info.compress_size
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(signed,headers={'Range':f'bytes={info.header_offset}-{end}'}),timeout=60) as response:data=response.read()
   nameLength,extraLength=struct.unpack_from('<HH',data,26)
   offset=30+nameLength+extraLength
   raw=data[offset:offset+info.compress_size]
   content=zlib.decompress(raw,-15) if info.compress_type==8 else raw
   if zlib.crc32(content)!=info.CRC:raise ValueError('CRC mismatch')
   target=(root/info.filename).resolve()
   if not target.is_relative_to(root):raise ValueError('Unsafe path')
   target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(content)
   return info.filename
  except Exception:
   if attempt==2:raise RuntimeError('Could not recover '+info.filename) from None
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 for i,name in enumerate(pool.map(recover,infos)):
  if i%20==0:print('Recovered',i+1,'/',len(infos),flush=True)
print('Selected recovery complete',flush=True)
