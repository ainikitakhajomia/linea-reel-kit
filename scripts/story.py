#!/usr/bin/env python3
"""Deterministic storyboard drafts and original SVG carousels; no external AI APIs."""
import argparse, html, json, math, re, textwrap
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def sentences(text):
    return [x.strip() for x in re.split(r'(?<=[.!?])\s+|\n+', text.strip()) if x.strip()]

def storyboard(text, brand):
    scenes = sentences(text)
    if not scenes:
        raise ValueError('Script is empty')
    effects, captions, start = [], [], 0.0
    choices = ['kinetic-hook', 'prompt-bar', 'nle-timeline', 'odometer-recursion', 'storyboard-deck', 'follow-chip']
    for i, sentence in enumerate(scenes):
        duration = max(2.4, len(sentence.split()) / 2.7)
        effect_id = choices[0] if i == 0 else choices[-1] if i == len(scenes)-1 else choices[1+(i-1)%4]
        effects.append({'id':effect_id,'start':round(start,3),'duration':round(duration,3),'text':sentence[:110]})
        for j, word in enumerate(sentence.split()):
            word_duration = duration / len(sentence.split())
            captions.append({'text':word,'startMs':round((start+j*word_duration)*1000),'endMs':round((start+(j+1)*word_duration)*1000),'timestampMs':None,'confidence':None})
        start += duration
    # Captions are script timing estimates, not speech alignment. No voice is generated.
    return {'job':{'title':'Script → motion','width':720,'height':1280,'fps':30,'duration':round(start,3),'brand':brand,'effects':effects,'captions':[]},'storyboard':{'method':'deterministic draft, agent should revise intent/pacing','scenes':scenes,'estimatedCaptions':captions,'audio':'none — supply owned narration, no TTS API used'}}

def svg_slide(sentence,index,total,brand):
    bg = brand['accent'] if index%3==0 else brand['background']
    ink = '#ffffff' if index%3==0 else brand['foreground']
    size=66 if len(sentence)<80 else 54
    lines=textwrap.wrap(sentence,width=23 if size==66 else 28,break_long_words=True)
    if len(lines)>10:
        raise ValueError('Carousel slide exceeds safe text capacity; split the script into shorter sentences')
    rendered=''.join(f'<tspan x="74" dy="{size*1.18}">{html.escape(line)}</tspan>' for line in lines)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1440" viewBox="0 0 720 960"><rect width="720" height="960" fill="{bg}"/><path d="M74 78H112" stroke="{ink}" stroke-width="3"/><text x="130" y="83" font-family="Arial" font-size="14" letter-spacing="3" fill="{ink}">STUDIO LINEA</text><text x="74" y="240" fill="{ink}" font-family="Arial" font-weight="700" font-size="{size}">{rendered}</text><line x1="74" y1="850" x2="646" y2="850" stroke="{ink}" opacity=".25"/><text x="74" y="895" fill="{ink}" font-size="17" font-family="Arial">Meer tijd voor wat écht telt.</text><text x="646" y="895" text-anchor="end" fill="{ink}" font-size="17" font-family="Arial">{index+1:02d} / {total:02d}</text></svg>'''

def feedback(job):
    issues=[]
    for i,e in enumerate(job.get('effects',[])):
        if e['duration']<1.2:issues.append(f'Effect {i}: too little time to read')
        if len(e.get('text','').split())/e['duration']>3.5:issues.append(f'Effect {i}: text density >3.5 words/s')
    return {'checks':'heuristic readability only; no aesthetic or semantic AI judgment','issues':issues}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['storyboard','carousel','feedback']);p.add_argument('input',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--brand',type=Path,default=ROOT/'brands/studio-linea.json');a=p.parse_args()
    brand=json.loads(a.brand.read_text());a.out.mkdir(parents=True,exist_ok=True)
    if a.command=='feedback':
        data=json.loads(a.input.read_text());(a.out/'feedback.json').write_text(json.dumps(feedback(data.get('job',data)),indent=2));return
    script=a.input.read_text()
    if a.command=='storyboard':
        result=storyboard(script,brand);(a.out/'job.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));(a.out/'feedback.json').write_text(json.dumps(feedback(result['job']),indent=2));print(a.out/'job.json')
    else:
        slides=sentences(script)
        if not slides:raise ValueError('Empty script')
        for i,s in enumerate(slides):(a.out/f'{i+1:02d}.svg').write_text(svg_slide(s,i,len(slides),brand))
        (a.out/'manifest.json').write_text(json.dumps({'format':'1080x1440','brand':brand,'slides':[f'{i+1:02d}.svg' for i in range(len(slides))]},ensure_ascii=False,indent=2));print(a.out/'manifest.json')
if __name__=='__main__':main()
