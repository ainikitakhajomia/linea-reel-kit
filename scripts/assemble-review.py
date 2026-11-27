"""Collect existing synthetic render outputs without rendering or changing them."""
import json,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'public/review-media'; DEST.mkdir(parents=True,exist_ok=True)
def keep(path):
    path=Path(path)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    target=DEST/(digest[:24]+path.suffix.lower())
    if not target.exists():shutil.copyfile(path,target)
    return 'review-media/'+target.name
sources=[('corrected','Gecorrigeerd · small ASR · 1080p','46048561317',ROOT/'out/recovered/latest'),('native','Eerdere versie · 1080p','46047685973',ROOT/'out/recovered/previous'),('first','Eerste versie · 540p · visueel afgekeurd','46046650541',Path('/Users/nikitakhajomia/linea-dev/worktrees/mattia/task-20261127-175400-eededbe663/linea-reel-kit/out/rendered-first'))]
result={'effects':{},'films':[],'extras':[],'carousels':[],'provenance':'Original synthetic demonstrations from preserved GitHub Actions outputs. No client footage. Reference media is linked directly, never copied.','sources':[]}
films={}
for key,label,run,base in sources:
    if not base.exists():continue
    portable=base/'out/portable-review/public'
    if not portable.exists():raise SystemExit('Missing portable review '+str(base))
    result['sources'].append({'label':label,'run':run,'url':f'https://github.com/ainikitakhajomia/linea-reel-kit/actions/runs/{run}'})
    manifest=json.loads((portable/'demos/manifest.json').read_text()) if (portable/'demos/manifest.json').exists() else []
    for demo in manifest:
        if 'synthetic' not in json.dumps(demo.get('provenance',{})).lower():raise ValueError('Unapproved provenance')
        folder=portable/'demos'/demo['id']
        if not (folder/'final.mp4').exists():continue
        jobdoc=json.loads((folder/'job.json').read_text());job=jobdoc.get('job',jobdoc)
        film=films.setdefault(demo['id'],{'id':demo['id'],'title':demo['title'],'script':demo['provenance'].get('script',''),'limitations':demo['provenance'].get('limitations',[]),'versions':[]})
        v={'label':label,'key':key,'run':run,'video':keep(folder/'final.mp4'),'duration':demo['duration'],'effects':job.get('effects',[]),'captions':job.get('captions',[]),'storyboard':jobdoc.get('storyboard',job.get('storyboard',[])),'prompt':demo['provenance'].get('script',''),'provenance':demo['provenance']}
        for name,field in [('source.mp4','source'),('poster.jpg','poster'),('job.json','job')]:
            if (folder/name).exists():v[field]=keep(folder/name)
        film['versions'].append(v)
    if key=='corrected':
        for e in json.loads((ROOT/'src/catalog.json').read_text()):
            video=portable/'renders'/(e['id']+'.mp4');poster=portable/'renders'/(e['id']+'-poster.jpg')
            if not video.exists():raise ValueError('Missing effect '+e['id'])
            result['effects'][e['id']]={'video':keep(video),'poster':keep(poster)}
        for image in sorted((base/'out/carousel').glob('*.png')):result['carousels'].append(keep(image))
    for name in ['talking-head-demo.mp4','talking-head-with-sfx.mp4','slideshow.mp4']:
        p=base/'out'/name
        if p.exists():result['extras'].append({'title':name.removesuffix('.mp4').replace('-',' '),'version':label,'run':run,'video':keep(p),'source':keep(portable/'demo/source.mp4') if (portable/'demo/source.mp4').exists() else None})
# Preserve the original local synthetic pipeline cuts as well.
local=Path('/Users/nikitakhajomia/linea-dev/worktrees/moeder/task-20261127-173344-4f2dc9d203/linea-reel-kit/public')
if local.exists():
 for folder in ['demo','asr-demo']:
  p=local/'jobs'/folder/'edited.mp4'
  if p.exists():result['extras'].append({'title':'Lokale pipeline · '+folder,'version':'Oorspronkelijke lokale synthetische cut','run':None,'video':keep(p),'source':keep(local/'demo/source.mp4')})
result['films']=list(films.values())
if len(result['effects'])!=67:raise ValueError('Recover all 67 latest effect MP4s first')
(ROOT/'public/review-manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({'effects':len(result['effects']),'films':len(result['films']),'versions':sum(len(f['versions']) for f in result['films']),'extras':len(result['extras']),'mediaBytes':sum(p.stat().st_size for p in DEST.iterdir())}))
