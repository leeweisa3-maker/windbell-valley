"""Original score: A breeze by the creek, 32 bars, 3/4, 75 BPM, C major.
Deterministic additive synthesis. No samples or third-party music.
"""
import numpy as np, wave
from pathlib import Path
SR=32000; BEAT=.8; LENGTH=32*3*BEAT
out=np.zeros((int(SR*LENGTH),2),dtype=np.float64)
rng=np.random.default_rng(32)
def note(midi,start,duration,voice='piano',volume=.13,pan=0):
    hz=440*2**((midi-69)/12); t=np.arange(int((duration+2)*SR))/SR
    attack=1-np.exp(-t/(.035 if voice=='flute' else .008))
    if voice=='piano':
        sig=sum(np.sin(2*np.pi*hz*h*t+.0008*h*np.sin(2*np.pi*3*t))*a*np.exp(-t/(1.7/h)) for h,a in [(1,1),(2,.31),(3,.13),(4,.05)])
        env=attack*np.minimum(1,np.maximum(0,(duration+1.1-t)/1.1))
    elif voice=='flute':
        phase=2*np.pi*hz*t+0.018*np.sin(2*np.pi*4.8*t)
        sig=np.sin(phase)+.12*np.sin(phase*2)+.035*np.sin(phase*3)
        env=attack*np.minimum(1,np.maximum(0,(duration+.15-t)/.3))*np.exp(-t*.15)
    elif voice=='bell':
        sig=sum(a*np.sin(2*np.pi*hz*h*t)*np.exp(-t/(2.5/h)) for h,a in [(1,1),(2.01,.35),(3.97,.15)])
        env=attack
    else:
        sig=np.sin(2*np.pi*hz*t)+.12*np.sin(2*np.pi*hz*2*t)
        env=attack*np.minimum(1,np.maximum(0,(duration-t)/.25))*.6
    sig*=env*volume
    stereo=np.column_stack([sig*np.sqrt((1-pan)/2),sig*np.sqrt((1+pan)/2)])
    ix=(int(start*SR)+np.arange(len(t)))%len(out)
    np.add.at(out,ix,stereo)
chords=[(48,52,55),(43,47,50),(45,48,52),(40,43,47),(41,45,48),(48,52,55),(38,41,45),(43,47,50), (48,52,55),(52,55,59),(45,48,52),(43,47,50),(41,45,48),(38,41,45),(43,47,50),(48,52,55)]
melody=[[72,76,79],[74,71,67],[69,72,76],[71,67,64],[69,72,77],[76,72,67],[69,74,77],[74,71,67],[76,79,84],[83,79,76],[81,76,72],[74,79,71],[77,76,72],[74,69,65],[71,74,79],[76,72,72]]
for bar in range(32):
    start=bar*3*BEAT; ch=chords[bar%16]
    note(ch[0]-12,start,2.8*BEAT,'bass',.15,-.2)
    for k in range(6):note(ch[k%3]+12,start+k*BEAT/2,1.2,'piano',.11,-.35 if k%2 else .25)
    for k,m in enumerate(melody[bar%16]):
        if bar==31 and k==2:continue
        note(m,start+k*BEAT,BEAT*(1.7 if k==2 else .86),'flute',.09,.15)
    if bar%4==0:note(84+bar%3*2,start+.05,2,'bell',.045,.55)
# Warm stereo room reverb with wrap-around keeps the exported theme loopable.
source=out.copy()
for delay,gain in [(.17,.15),(.31,.11),(.53,.065),(.79,.04)]:out+=np.roll(source,int(delay*SR),axis=0)[:,::-1]*gain
out=np.tanh(out*1.4);out*=.82/max(.82,np.max(np.abs(out)))
path=Path(__file__).resolve().parents[1]/'assets'/'windbell-valley.wav'
with wave.open(str(path),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes((out*32767).astype('<i2').tobytes())
print(f'Original instrumental score: {LENGTH:.1f}s, stereo, {SR} Hz')
