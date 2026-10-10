"""Original Windbell Valley film theme: 16 bars, 72 BPM, 3/4."""
import json,struct
from pathlib import Path
root=Path(__file__).resolve().parents[1];beat=60/72
chords=[(48,52,55),(43,47,50),(45,48,52),(40,43,47),(41,45,48),(48,52,55),(38,41,45),(43,47,50),(48,52,55),(52,55,59),(45,48,52),(43,47,50),(41,45,48),(38,41,45),(43,47,50),(48,52,55)]
melody=[[72,76,79],[74,71,67],[69,72,76],[71,67,64],[69,72,77],[76,72,67],[69,74,77],[74,71,67],[76,79,84],[83,79,76],[81,76,72],[74,79,71],[77,76,72],[74,69,65],[71,74,79],[76,72,72]]
notes=[]
def add(track,note,start,dur,velocity):notes.append(dict(track=track,note=note,start=round(start,6),duration=round(dur,6),velocity=velocity))
for bar,(ch,mel) in enumerate(zip(chords,melody)):
    st=bar*3*beat
    add(4,ch[0]-12,st,2.8*beat,52)
    for k in range(6):add(1,ch[k%3]+12,st+k*beat/2,1.3*beat,47+k%2*3)
    for k,n in enumerate(mel):add(0,n,st+k*beat,beat*(1.5 if k==2 else .87),58)
    for n in ch:add(2,n+12,st,2.9*beat,30)
    if bar%4==0:add(3,84+bar%3*2,st+.08,1.8*beat,38)
score=dict(title='溪谷来信 / A Letter from the Valley',bpm=72,timeSignature='3/4',duration=42,programs=[73,24,48,9,32],notes=notes)
(root/'film-source'/'score.json').write_text(json.dumps(score,ensure_ascii=False,indent=2))
def var(v):
    a=[v&127];v>>=7
    while v:a.insert(0,(v&127)|128);v>>=7
    return bytes(a)
events=[(0,b'\xff\x51\x03'+int(60000000/72).to_bytes(3,'big')),(0,b'\xff\x58\x04\x03\x02\x18\x08')]
for ch,p in enumerate(score['programs']):events.append((0,bytes([0xc0|ch,p])))
for n in notes:
    start=int(n['start']/beat*480);end=int((n['start']+n['duration'])/beat*480)
    events.extend([(start,bytes([0x90|n['track'],n['note'],n['velocity']])),(end,bytes([0x80|n['track'],n['note'],0]))])
data=bytearray();last=0
for tick,event in sorted(events,key=lambda x:x[0]):data+=var(tick-last)+event;last=tick
data+=b'\x00\xff\x2f\x00'
(root/'film-source'/'score.mid').write_bytes(b'MThd'+struct.pack('>IHHH',6,0,1,480)+b'MTrk'+struct.pack('>I',len(data))+data)
print('Original score written: 16 bars, 42 seconds, five acoustic instrument parts')
