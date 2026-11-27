#!/usr/bin/env python3
"""Generate ten original, explicitly synthetic editorial fixtures on Linux.

No customer media, stock footage, paid service, or reference media is used.
Pillow draws the illustrative presenter/UI; espeak-ng speaks authored scripts.
ASR word times come from faster-whisper, never uniform script estimates.
"""
from __future__ import annotations
import argparse
import array
import json
import math
import re
import unicodedata
from pathlib import Path
import shutil
import subprocess
import wave
from functools import lru_cache

ROOT = Path(__file__).resolve().parents[1]
FPS, WIDTH, HEIGHT = 24, 540, 960
SCALE = 2
FRAME_WIDTH, FRAME_HEIGHT = WIDTH*SCALE, HEIGHT*SCALE
# Distinct hooks, arcs and techniques, not one effect renamed ten times.
CONCEPTS = [
    ('01-talking-head', 'Dynamische captions', 'nl', 'Je hebt geen extra werkdag nodig. Begin met die ene taak die je elke week opnieuw doet.', [('camera-transitions', 'Die ene taak'), ('word-stamp', 'Elke week?'), ('follow-chip', 'Pak die eerst')], 'presenter'),
    ('02-behind-speaker', 'Tekst achter de spreker', 'nl', 'Dit staat niet voor je neus. Het staat achter mij. Zo blijft het verhaal letterlijk op de voorgrond.', [('kinetic-hook', 'ACHTER MIJ'), ('orbit-ring', 'HET VERHAAL'), ('giant-captions', 'BLIJFT VOORAAN')], 'matte'),
    ('03-walkthrough', 'Spreker plus walkthrough', 'nl', 'Hier zit de winst. Eerst een losse aanvraag. Dan een duidelijke volgende stap. Zonder zes keer dezelfde informatie overtypen.', [('intertitle', 'Nieuwe aanvraag'), ('word-stamp', 'Volgende stap'), ('follow-chip', 'Geen dubbel werk')], 'walkthrough'),
    ('04-product', 'SaaS productverhaal', 'en', 'Your inbox is not a workflow. Put the next step where your team can see it. Then get back to the work.', [('file-drop', 'One place'), ('video-card', 'A clear next step'), ('layer-explode', 'Back to the work')], 'product'),
    ('05-kinetic', 'Kinetic typography', 'nl', 'Nog een tabblad. Nog een lijstje. Nog een keer kopiëren. Of je maakt ruimte voor het werk dat telt.', [('giant-captions', 'NOG EEN TABBLAD'), ('word-stamp', 'NOG EEN LIJSTJE'), ('knockout-captions', 'MAAK RUIMTE')], 'type'),
    ('06-slideshow', 'Dynamische slideshow', 'nl', 'Drie beelden. Eén verhaal. Van een los idee naar een plan waar je morgen echt mee aan de slag kunt.', [('contact-sheet-hook', 'Eén verhaal'), ('storyboard-deck', 'Van idee naar plan'), ('video-card', 'Morgen beginnen')], 'slides'),
    ('07-humor', 'Humoristische social', 'nl', 'Ik doe het wel even handmatig. Beroemde laatste woorden. Drie uur later ben je nog steeds dezelfde kolom aan het kopiëren.', [('incoming-call', 'Ik doe het wel even'), ('impact-frame', 'DRIE UUR LATER'), ('receipt-printer', 'Handwerk: 180 min')], 'presenter'),
    ('08-story', 'Storytelling', 'nl', 'Maandag lag alles verspreid. Op vrijdag wist iedereen wat de volgende stap was. We begonnen met één proces. Niet met twintig tools.', [('screenplay-page', 'MAANDAG'), ('paper-tear', 'VRIJDAG'), ('intertitle', 'Begin met één proces')], 'story'),
    ('09-depth', 'Diepte en motion', 'en', 'A good edit has layers. The footage. The idea. The words. Give each one a job, and let the story do the moving.', [('layer-explode', 'FOOTAGE / IDEA / WORDS'), ('orbit-ring', 'THE STORY'), ('room-doors', 'Give it room')], 'matte'),
    ('10-hook-mix', 'Hooks en editingmix', 'nl', 'Stop. Voordat je nog een tool toevoegt: wat moet er eigenlijk eenvoudiger? Laat dat zien. Maak het klein. En test het morgen.', [('impact-frame', 'STOP'), ('blade-slice', 'Wat kan eenvoudiger?'), ('grade-slider', 'Test het morgen')], 'matte'),
]


CUE_PHRASES = {
 '01-talking-head': ['je hebt','begin','elke week'],
 '02-behind-speaker': ['dit staat','achter mij','voorgrond'],
 '03-walkthrough': ['hier zit','volgende stap','overtypen'],
 '04-product': ['your inbox','next step','back'],
 '05-kinetic': ['nog een tabblad','nog een lijstje','of je maakt'],
 '06-slideshow': ['drie beelden','van een los idee','morgen'],
 '07-humor': ['handmatig','drie uur later','kopiëren'],
 '08-story': ['maandag','vrijdag','één proces'],
 '09-depth': ['layers','the words','let the story'],
 '10-hook-mix': ['stop','wat moet','test het morgen'],
}


def normalized_words(text):
    plain=''.join(c for c in unicodedata.normalize('NFKD',text.lower()) if not unicodedata.combining(c))
    return re.findall(r'\w+',plain)


def speech_cues(captions, phrases, duration, minimum_hold=.5):
    """Match ordered cues to actual ASR onsets; explicitly report word-quantile fallback.

    Scheduled starts may be constrained to leave readable holds. They never change
    any ASR timestamp. The first visual hook intentionally starts before its cue.
    """
    if not phrases or not math.isfinite(duration) or duration<len(phrases)*minimum_hold:
        raise ValueError('Duration cannot provide the minimum hold for every cue')
    tokens=[]
    for caption in captions:
        onset=caption['startMs']/1000
        if not math.isfinite(onset) or onset<0 or onset>=duration:
            raise ValueError('ASR onset must lie inside the actual source duration')
        for word in normalized_words(caption['text']):
            tokens.append((word,onset))
    if len(tokens)<len(phrases) or any(tokens[i][1]>tokens[i+1][1] for i in range(len(tokens)-1)):
        raise ValueError('Cue scheduling requires ordered actual ASR words for every cue')
    records=[];cursor=0;starts=[]
    for i,phrase in enumerate(phrases):
        needle=normalized_words(phrase)
        # Reserve at least one later real ASR word per remaining cue.
        last=len(tokens)-(len(phrases)-i-1)
        index=next((j for j in range(cursor,last-len(needle)+1) if [x[0] for x in tokens[j:j+len(needle)]]==needle),None) if needle else None
        exact=index is not None
        if not exact:index=min(last-1,max(cursor,len(tokens)*i//len(phrases)))
        onset=tokens[index][1]
        requested=0 if i==0 else onset
        earliest=0 if i==0 else starts[-1]+minimum_hold
        latest=duration-minimum_hold*(len(phrases)-i)
        start=min(latest,max(earliest,requested))
        starts.append(start)
        records.append({'phrase':phrase,'mode':'exact-normalized-asr' if exact else 'actual-asr-word-quantile','asrTokenIndex':index,'asrToken':tokens[index][0],'asrOnsetSeconds':onset,'start':start,'firstHookPreroll':i==0,'clampedForMinimumHold':abs(start-requested)>1e-8,'fallbackReason':None if exact else 'Phrase was not recognized in the remaining ordered ASR words; using an actual word onset.'})
        cursor=index+(len(needle) if exact else 1)
    for i,record in enumerate(records):
        end=starts[i+1] if i+1<len(starts) else duration
        record['duration']=end-record['start']
    return records


def run(args):
    subprocess.run([str(x) for x in args], check=True)


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


@lru_cache(maxsize=24)
def font(size, bold=False):
    size = round(size*SCALE)
    from PIL import ImageFont
    base = '/usr/share/fonts/truetype/dejavu/DejaVuSans' + ('-Bold' if bold else '') + '.ttf'
    return ImageFont.truetype(base, size) if Path(base).exists() else ImageFont.load_default(size=size)


class NativeDraw:
    """Draw logical layout coordinates directly at native export resolution.

    No raster resize: geometry, strokes and font glyphs are rasterized at SCALE.
    """
    def __init__(self, image, layout_scale=1, offset=(0,0)):
        from PIL import ImageDraw
        self.draw = ImageDraw.Draw(image)
        self.factor=layout_scale*SCALE
        self.offset=tuple(value*SCALE for value in offset)

    def coords(self, value):
        if value and isinstance(value[0], (tuple,list)):
            return tuple(self.coords(x) for x in value)
        return tuple(number*self.factor+self.offset[index%2] for index,number in enumerate(value))

    def __getattr__(self, name):
        target = getattr(self.draw, name)
        def call(xy, *args, **kwargs):
            if name == 'rounded_rectangle' and args:
                args = (args[0]*self.factor, *args[1:])
            if 'width' in kwargs:
                kwargs['width'] = max(1, round(kwargs['width']*self.factor))
            if 'radius' in kwargs:
                kwargs['radius'] *= self.factor
            return target(self.coords(xy), *args, **kwargs)
        return call


def original_frame(t, mode, amplitude=0, transparent=False):
    from PIL import Image, ImageDraw
    im = Image.new('RGBA', (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0) if transparent else '#f6f5f1')
    d = NativeDraw(im)
    if not transparent:
        d.rounded_rectangle((25, 28, 515, 928), 30, fill='#eeece6')
        d.text((45, 52), 'STUDIO LINEA / REEL LAB', font=font(17, True), fill='#27335f')
        d.text((45, 895), 'SYNTHETISCHE DEMONSTRATIE', font=font(14), fill='#596079')
        d.line((45, 876, 495, 876), fill='#c4c7d0', width=1)
    if mode in ['presenter', 'matte', 'walkthrough'] or transparent:
        if mode=='walkthrough' and not transparent:d=NativeDraw(im,layout_scale=.42,offset=(295,510))
        dx = int(math.sin(t*1.4)*7)
        # Original illustrated presenter; mouth responds to the local speech waveform.
        d.rounded_rectangle((125+dx, 540, 415+dx, 875), 75, fill='#27335f')
        d.ellipse((168+dx, 338, 372+dx, 592), fill='#ddb99f')
        d.pieslice((161+dx, 322, 376+dx, 480), 180, 360, fill='#252933')
        d.rounded_rectangle((200+dx, 422, 257+dx, 462), 10, outline='#252933', width=5)
        d.rounded_rectangle((282+dx, 422, 339+dx, 462), 10, outline='#252933', width=5)
        d.line((257+dx, 438, 282+dx, 438), fill='#252933', width=4)
        opening = 3 + min(21, int(amplitude*80))
        d.ellipse((250+dx, 506-opening, 292+dx, 512+opening), fill='#7b463c')
        d.rounded_rectangle((245+dx, 586, 295+dx, 635), 10, fill='#c6cce6')
    return im


def walkthrough_frame(t):
    from PIL import Image
    # Original 4:3 concept screen, matching the renderer's single UI panel.
    im=Image.new('RGB',(960*SCALE,720*SCALE),'#e9ebf0');d=NativeDraw(im)
    d.rounded_rectangle((15,25,945,695),20,fill='white')
    d.rectangle((15,25,945,105),fill='#27335f')
    d.text((42,52),'LINEA / CONCEPT WORKFLOW',font=font(26,True),fill='white')
    for i,label in enumerate(['Nieuwe aanvraag','Offerte voorbereiden','Klaar voor review']):
        y=155+i*155;d.rounded_rectangle((42,y,918,y+118),15,fill='#f1f2f6')
        d.text((70,y+20),label,font=font(29,True),fill='#27335f')
        complete=t>i*2+1
        d.text((70,y+70),'Gereed' if complete else 'Volgende stap',font=font(23),fill='#68815c' if complete else '#72788b')
        d.ellipse((844,y+43,880,y+79),fill='#9aaf8a' if complete else '#d5d8e0')
    x,y=790+int(35*math.sin(t)),190+int(300*(.5+.5*math.sin(t*.7)))
    d.polygon([(x,y),(x+10,y+34),(x+19,y+20),(x+34,y+17)],fill='#27335f')
    d.text((42,643),'ILLUSTRATIEVE UI / GEEN PRODUCTSCREENSHOT',font=font(18),fill='#72788b')
    return im


def slide_frame(index):
    """Three distinct, original square illustrations, drawn at native resolution."""
    from PIL import Image
    im=Image.new('RGB',(540*SCALE,540*SCALE),['#eee5d4','#eef0f6','#dfe9d3'][index]);d=NativeDraw(im)
    d.text((38,40),['01 / HET IDEE','02 / HET PLAN','03 / MORGEN'][index],font=font(29,True),fill='#27335f')
    if index==0:
        d.rounded_rectangle((65,125,475,465),20,fill='#fffaf0')
        for row,line in enumerate(['Wat als we','die ene stap','eenvoudiger','maken?']):
            d.text((100,165+row*60),line,font=font(31,True),fill='#27335f')
        d.line((98,418,410,418),fill='#c7a866',width=5)
    elif index==1:
        for i,label in enumerate(['INPUT','ACTIE','KLAAR']):
            x=32+i*170;d.rounded_rectangle((x,145,x+155,460),15,fill='white')
            d.text((x+14,165),label,font=font(18,True),fill='#27335f')
            for j in range(3-i):
                y=218+j*68;d.rounded_rectangle((x+13,y,x+141,y+48),8,fill=['#c6cce6','#dfe9d3','#e3d9cb'][i])
    else:
        d.rounded_rectangle((92,128,448,458),20,fill='white')
        d.rectangle((92,128,448,200),fill='#27335f')
        d.text((126,147),'EEN KLEIN BEGIN',font=font(21,True),fill='white')
        d.text((167,215),'28',font=font(105,True),fill='#27335f')
        d.text((147,375),'Gewoon starten.',font=font(24),fill='#27335f')
    return im


def encode(path, frames, count, audio=None, frame_size=None):
    width,height=frame_size or (FRAME_WIDTH,FRAME_HEIGHT)
    args=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{width}x{height}','-r',str(FPS),'-i','-']
    if audio:args += ['-i',str(audio),'-af','apad,loudnorm=I=-16:TP=-1.5:LRA=11']
    args += ['-t',str(count/FPS),'-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p']
    if audio:args += ['-c:a','aac','-ar','48000']
    args += ['-movflags','+faststart',str(path)]
    proc=subprocess.Popen(args,stdin=subprocess.PIPE)
    try:
        for im in frames:proc.stdin.write(im.convert('RGB').tobytes())
        proc.stdin.close()
        if proc.wait():raise ValueError('Fixture encoder failed')
    finally:
        if proc.poll() is None:proc.kill();proc.wait()


def main():
    global SCALE, FRAME_WIDTH, FRAME_HEIGHT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=ROOT/'public/demos')
    parser.add_argument('--model',choices=['tiny','base','small','medium'],default='small',help='Multilingual local ASR: small for final, tiny for smoke')
    parser.add_argument('--scale',type=int,choices=[1,2],default=2,help='2: native1080x1920 final; 1: native540x960 smoke')
    parser.add_argument('--asr',action='store_true',help='Run actual EN/NL CPU ASR on every narration; downloads selected public model weights once')
    a=parser.parse_args();a.out=a.out.resolve()
    if not a.out.is_relative_to((ROOT/'public').resolve()):parser.error('--out must be inside this repository public/ directory')
    a.out.mkdir(parents=True,exist_ok=True)
    SCALE=a.scale;FRAME_WIDTH,FRAME_HEIGHT=WIDTH*SCALE,HEIGHT*SCALE
    if not a.asr:parser.error('Use --asr: complete demo scheduling requires actual speech word times')
    if not shutil.which('espeak-ng'):raise ValueError('espeak-ng is required on the isolated Linux runner')
    engine=None
    if a.asr:
        from faster_whisper import WhisperModel
        print(f'Loading public {a.model} weights for local CPU ASR',flush=True)
        engine=WhisperModel(a.model,device='cpu',compute_type='int8')
    brand=json.loads((ROOT/'brands/studio-linea.json').read_text())
    manifest=[]
    slides=a.out/'slides';slides.mkdir(exist_ok=True)
    slide_paths=[]
    for index,name in enumerate(['idea','plan','tomorrow']):
        slide_frame(index).save(slides/f'{name}.png')
        slide_paths.append((slides/f'{name}.png').relative_to(ROOT/'public').as_posix())
    walk=a.out/'walkthrough.mp4';count=FPS*14
    encode(walk,(walkthrough_frame(n/FPS) for n in range(count)),count,frame_size=(960*SCALE,720*SCALE))
    for identity,title,language,script,effects,mode in CONCEPTS:
        print(f'Preparing {identity}: {language}, original synthetic {mode}',flush=True)
        dest=a.out/identity;dest.mkdir(exist_ok=True)
        speech=dest/'speech.wav';run(['espeak-ng','-v',language,'-s','145' if language=='nl' else '153','-w',speech,script])
        with wave.open(str(speech)) as wavefile:
            rate=wavefile.getframerate();samples=array.array('h',wavefile.readframes(wavefile.getnframes()))
        duration=len(samples)/rate+.35;count=math.ceil(duration*FPS)
        amplitudes=[]
        for n in range(count):
            values=samples[int(n/FPS*rate):int((n+1)/FPS*rate)]
            amplitudes.append(math.sqrt(sum(x*x for x in values)/max(1,len(values)))/32768)
        source=dest/'source.mp4'
        encode(source,(original_frame(n/FPS,'blank' if identity in ['07-humor','08-story'] else mode,amplitudes[n]) for n in range(count)),count,speech)
        captions=[]
        if engine:
            segments,info=engine.transcribe(str(speech),language=language,word_timestamps=True,vad_filter=True)
            captions=[{'text':w.word,'startMs':round(w.start*1000),'endMs':max(round(w.start*1000)+1,round(w.end*1000)),'confidence':w.probability} for seg in segments for w in (seg.words or [])]
            if not captions:raise ValueError(f'ASR returned no captions for {identity}')
            print(f'{identity}: {len(captions)} actual ASR words; {count} source frames',flush=True)
        relative=dest.relative_to(ROOT/'public').as_posix()
        job={'title':title,'width':FRAME_WIDTH,'height':FRAME_HEIGHT,'fps':FPS,'duration':count/FPS,'brand':brand,'video':relative+'/source.mp4','captions':captions,'effects':[]}
        cues=speech_cues(captions,CUE_PHRASES[identity],count/FPS)
        for (effect,text),cue in zip(effects,cues):
            params={}
            if effect in ['kinetic-hook','giant-captions','knockout-captions']:
                span=[word for word in captions if cue['start']*1000<=word['startMs']<(cue['start']+cue['duration'])*1000][:5]
                if span:text=' '.join(word['text'].strip() for word in span);params['syncWords']=True
            event={'id':effect,'start':cue['start'],'duration':cue['duration'],'text':text,'params':params,'mediaSources':slide_paths if identity=='06-slideshow' else [a.out.relative_to(ROOT/'public').as_posix()+'/walkthrough.mp4']}
            if identity=='01-talking-head' and effect in ['word-stamp','follow-chip']:event.update(offsetY=-300,scale=.85)
            if identity=='03-walkthrough':
                y,scale={'intertitle':(-430,.5),'word-stamp':(-350,.6),'follow-chip':(-400,.65)}[effect]
                event.update(offsetY=y,scale=scale)
            job['effects'].append(event)
        if mode=='walkthrough':
            job['effects'].insert(0,{'id':'broll','src':a.out.relative_to(ROOT/'public').as_posix()+'/walkthrough.mp4','mediaType':'video','start':0,'duration':count/FPS})
        if mode=='matte':
            original_frame(0,'blank').save(dest/'background.png')
            job['background']=relative+'/background.png'
            matte=dest/'foreground';matte.mkdir(exist_ok=True)
            for n in range(count):original_frame(n/FPS,mode,amplitudes[n],True).save(matte/f'{n:06}.png')
            job['foregroundFrames']=relative+'/foreground/%06d.png'
        provenance={'kind':'original synthetic demonstration','nativeResolution':[FRAME_WIDTH,FRAME_HEIGHT],'rasterization':'geometry, strokes and font glyphs drawn natively; no raster upscaling','script':script,'language':language,'voice':'espeak-ng local synthetic speech','visuals':'original Pillow illustration and concept UI, not a product screenshot or real presenter','cueReport':cues,'asrModel':a.model,'captions':f'actual faster-whisper {a.model} CPU/int8 word times' if engine else 'none; rerun --asr for actual captions','acceptance':'technical demonstration; human and reference visual acceptance outstanding','limitations':['Illustrative mouth responds to audio energy; not phonetic lip synchronization.','Authored alpha fixture proves compositing, not natural person segmentation.','3D recipes use Canvas perspective; not a full 3D engine.']}
        save(dest/'job.json',{'job':job,'provenance':provenance})
        save(dest/'transcript.json',{'captions':captions,'language':language,'model':a.model if engine else None,'script':script})
        manifest.append({'id':identity,'title':title,'job':relative+'/job.json','video':relative+'/final.mp4','duration':count/FPS,'provenance':provenance})
    save(a.out/'manifest.json',manifest)
    print(a.out/'manifest.json')

if __name__=='__main__':main()
