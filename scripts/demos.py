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
from pathlib import Path
import shutil
import subprocess
import wave
from functools import lru_cache

ROOT = Path(__file__).resolve().parents[1]
FPS, WIDTH, HEIGHT = 24, 540, 960
# Distinct hooks, arcs and techniques, not one effect renamed ten times.
CONCEPTS = [
    ('01-talking-head', 'Dynamische captions', 'nl', 'Je hebt geen extra werkdag nodig. Begin met die ene taak die je elke week opnieuw doet.', [('camera-transitions', 'Die ene taak'), ('word-stamp', 'Elke week?'), ('follow-chip', 'Pak die eerst')], 'presenter'),
    ('02-behind-speaker', 'Tekst achter de spreker', 'nl', 'Dit staat niet voor je neus. Het staat achter mij. Zo blijft het verhaal letterlijk op de voorgrond.', [('kinetic-hook', 'ACHTER MIJ'), ('orbit-ring', 'HET VERHAAL'), ('giant-captions', 'BLIJFT VOORAAN')], 'matte'),
    ('03-walkthrough', 'Spreker plus walkthrough', 'nl', 'Hier zit de winst. Eerst een losse aanvraag. Dan een duidelijke volgende stap. Zonder zes keer dezelfde informatie overtypen.', [('prompt-bar', 'Nieuwe aanvraag'), ('live-cursor', 'Volgende stap'), ('odometer-recursion', 'Minder overtypen')], 'walkthrough'),
    ('04-product', 'SaaS productverhaal', 'en', 'Your inbox is not a workflow. Put the next step where your team can see it. Then get back to the work.', [('file-drop', 'One place'), ('video-card', 'A clear next step'), ('layer-explode', 'Back to the work')], 'product'),
    ('05-kinetic', 'Kinetic typography', 'nl', 'Nog een tabblad. Nog een lijstje. Nog een keer kopiëren. Of je maakt ruimte voor het werk dat telt.', [('giant-captions', 'NOG EEN TABBLAD'), ('word-stamp', 'NOG EEN LIJSTJE'), ('knockout-captions', 'MAAK RUIMTE')], 'type'),
    ('06-slideshow', 'Dynamische slideshow', 'nl', 'Drie beelden. Eén verhaal. Van een los idee naar een plan waar je morgen echt mee aan de slag kunt.', [('contact-sheet-hook', 'Eén verhaal'), ('storyboard-deck', 'Van idee naar plan'), ('video-card', 'Morgen beginnen')], 'slides'),
    ('07-humor', 'Humoristische social', 'nl', 'Ik doe het wel even handmatig. Beroemde laatste woorden. Drie uur later ben je nog steeds dezelfde kolom aan het kopiëren.', [('incoming-call', 'Ik doe het wel even'), ('impact-frame', 'DRIE UUR LATER'), ('receipt-printer', 'Handwerk: 180 min')], 'presenter'),
    ('08-story', 'Storytelling', 'nl', 'Maandag lag alles verspreid. Op vrijdag wist iedereen wat de volgende stap was. We begonnen met één proces. Niet met twintig tools.', [('screenplay-page', 'MAANDAG'), ('paper-tear', 'VRIJDAG'), ('intertitle', 'Begin met één proces')], 'story'),
    ('09-depth', 'Diepte en motion', 'en', 'A good edit has layers. The footage. The idea. The words. Give each one a job, and let the story do the moving.', [('layer-explode', 'FOOTAGE / IDEA / WORDS'), ('orbit-ring', 'THE STORY'), ('room-doors', 'Give it room')], 'matte'),
    ('10-hook-mix', 'Hooks en editingmix', 'nl', 'Stop. Voordat je nog een tool toevoegt: wat moet er eigenlijk eenvoudiger? Laat dat zien. Maak het klein. En test het morgen.', [('impact-frame', 'STOP'), ('blade-slice', 'Wat kan eenvoudiger?'), ('grade-slider', 'Test het morgen')], 'matte'),
]


def run(args):
    subprocess.run([str(x) for x in args], check=True)


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


@lru_cache(maxsize=24)
def font(size, bold=False):
    from PIL import ImageFont
    base = '/usr/share/fonts/truetype/dejavu/DejaVuSans' + ('-Bold' if bold else '') + '.ttf'
    return ImageFont.truetype(base, size) if Path(base).exists() else ImageFont.load_default(size=size)


def original_frame(t, mode, amplitude=0, transparent=False):
    from PIL import Image, ImageDraw
    im = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0) if transparent else '#f6f5f1')
    d = ImageDraw.Draw(im)
    if not transparent:
        d.rounded_rectangle((25, 28, 515, 928), 30, fill='#eeece6')
        d.text((45, 52), 'STUDIO LINEA / REEL LAB', font=font(17, True), fill='#27335f')
        d.text((45, 895), 'SYNTHETISCHE DEMONSTRATIE', font=font(14), fill='#596079')
        d.line((45, 876, 495, 876), fill='#c4c7d0', width=1)
    if mode in ['presenter', 'matte', 'walkthrough', 'story'] or transparent:
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
    elif mode in ['product', 'slides']:
        for i in range(3):
            y = 210 + i*180 + int(8*math.sin(t+i))
            d.rounded_rectangle((50+i*12, y, 475+i*4, y+150), 18, fill=['#27335f','#c6cce6','#dfe9d3'][i])
            d.text((78+i*12, y+22), ['01 / AANVRAAG','02 / VOLGENDE STAP','03 / RUIMTE TERUG'][i], font=font(19, True), fill='white' if i==0 else '#27335f')
            d.rounded_rectangle((78+i*12, y+65, 390, y+80), 5, fill='#ffffff77')
    else:
        d.text((45, 250), 'MINDER RUIS.', font=font(44, True), fill='#27335f')
        d.text((45, 315), 'MEER RUIMTE.', font=font(44, True), fill='#27335f')
    return im


def walkthrough_frame(t):
    from PIL import Image, ImageDraw
    im=Image.new('RGB', (WIDTH, HEIGHT), '#e9ebf0');d=ImageDraw.Draw(im)
    d.rounded_rectangle((15,160,525,780),20,fill='white')
    d.rectangle((15,160,525,220),fill='#27335f')
    d.text((35,180),'LINEA / CONCEPT WORKFLOW',font=font(19,True),fill='white')
    for i, label in enumerate(['Nieuwe aanvraag','Offerte voorbereiden','Klaar voor review']):
        y=270+i*145;d.rounded_rectangle((40,y,500,y+110),15,fill='#f1f2f6')
        d.text((62,y+20),label,font=font(22,True),fill='#27335f')
        complete=t>i*2+1
        d.text((62,y+62),'Gereed' if complete else 'Volgende stap',font=font(17),fill='#68815c' if complete else '#72788b')
        d.ellipse((450,y+35,476,y+61),fill='#9aaf8a' if complete else '#d5d8e0')
    x,y=400+int(35*math.sin(t)),300+int(280*(.5+.5*math.sin(t*.7)))
    d.polygon([(x,y),(x+8,y+28),(x+16,y+17),(x+28,y+14)],fill='#27335f')
    return im


def encode(path, frames, count, audio=None):
    args=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{WIDTH}x{HEIGHT}','-r',str(FPS),'-i','-']
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
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=ROOT/'public/demos')
    parser.add_argument('--asr',action='store_true',help='Run actual EN/NL tiny CPU ASR on every narration; downloads public weights once')
    a=parser.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    if not shutil.which('espeak-ng'):raise ValueError('espeak-ng is required on the isolated Linux runner')
    engine=None
    if a.asr:
        from faster_whisper import WhisperModel
        engine=WhisperModel('tiny',device='cpu',compute_type='int8')
    brand=json.loads((ROOT/'brands/studio-linea.json').read_text())
    manifest=[]
    walk=a.out/'walkthrough.mp4';count=FPS*14
    encode(walk,(walkthrough_frame(n/FPS) for n in range(count)),count)
    for identity,title,language,script,effects,mode in CONCEPTS:
        dest=a.out/identity;dest.mkdir(exist_ok=True)
        speech=dest/'speech.wav';run(['espeak-ng','-v',language,'-s','163','-w',speech,script])
        with wave.open(str(speech)) as wavefile:
            rate=wavefile.getframerate();samples=array.array('h',wavefile.readframes(wavefile.getnframes()))
        duration=len(samples)/rate+.35;count=math.ceil(duration*FPS)
        amplitudes=[]
        for n in range(count):
            values=samples[int(n/FPS*rate):int((n+1)/FPS*rate)]
            amplitudes.append(math.sqrt(sum(x*x for x in values)/max(1,len(values)))/32768)
        source=dest/'source.mp4'
        encode(source,(original_frame(n/FPS,mode,amplitudes[n]) for n in range(count)),count,speech)
        captions=[]
        if engine:
            segments,info=engine.transcribe(str(speech),language=language,word_timestamps=True,vad_filter=True)
            captions=[{'text':w.word,'startMs':round(w.start*1000),'endMs':max(round(w.start*1000)+1,round(w.end*1000)),'confidence':w.probability} for seg in segments for w in (seg.words or [])]
            if not captions:raise ValueError(f'ASR returned no captions for {identity}')
        relative=dest.relative_to(ROOT/'public').as_posix()
        job={'title':title,'width':WIDTH,'height':HEIGHT,'fps':FPS,'duration':count/FPS,'brand':brand,'video':relative+'/source.mp4','captions':captions,'effects':[]}
        step=count/FPS/3
        for i,(effect,text) in enumerate(effects):
            job['effects'].append({'id':effect,'start':round(i*step,4),'duration':round(step,4),'text':text,'mediaSources':[a.out.relative_to(ROOT/'public').as_posix()+'/walkthrough.mp4']})
        if mode=='walkthrough':job['walkthrough']=a.out.relative_to(ROOT/'public').as_posix()+'/walkthrough.mp4'
        if mode=='matte':
            matte=dest/'foreground';matte.mkdir(exist_ok=True)
            for n in range(count):original_frame(n/FPS,mode,amplitudes[n],True).save(matte/f'{n:06}.png')
            job['foregroundFrames']=relative+'/foreground/%06d.png'
        provenance={'kind':'original synthetic demonstration','script':script,'language':language,'voice':'espeak-ng local synthetic speech','visuals':'original Pillow illustration and concept UI, not a product screenshot or real presenter','captions':'actual faster-whisper tiny CPU/int8 word times' if engine else 'none; rerun --asr for actual captions','acceptance':'technical demonstration; human and reference visual acceptance outstanding','limitations':['Illustrative mouth responds to audio energy; not phonetic lip synchronization.','Authored alpha fixture proves compositing, not natural person segmentation.','3D recipes use Canvas perspective; not a full 3D engine.']}
        save(dest/'job.json',{'job':job,'provenance':provenance})
        save(dest/'transcript.json',{'captions':captions,'language':language,'model':'tiny' if engine else None,'script':script})
        manifest.append({'id':identity,'title':title,'job':relative+'/job.json','video':relative+'/final.mp4','duration':count/FPS,'provenance':provenance})
    save(a.out/'manifest.json',manifest)
    print(a.out/'manifest.json')

if __name__=='__main__':main()
