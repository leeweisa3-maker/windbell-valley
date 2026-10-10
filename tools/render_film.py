"""Compose the 42 second village film from a painted panorama and independent alpha loops."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,math,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];TMP=ROOT/'output'/'film';ASSETS=ROOT/'assets'
FPS=30;DURATION=42;WIDTH=1280;HEIGHT=720
original=Image.open(ASSETS/'windbell-valley-panorama.png').convert('RGB');scale=HEIGHT/original.height
world=original.resize((round(original.width*scale),HEIGHT),Image.Resampling.LANCZOS)
loops={name:[Image.open(p).convert('RGBA')for p in sorted((TMP/name/'frames').glob('*.png'))]for name in ['courier','fox','gardener','baker','elder']}
assert all(loops.values()),'Prepare animation loops first'
# A foreground parapet layer from the SAME panorama places the flute player behind the bridge rail.
mask=Image.new('L',world.size,0);draw=ImageDraw.Draw(mask)
poly=[(5290,388),(5330,365),(5370,346),(5420,332),(5470,328),(5520,332),(5570,344),(5620,366),(5670,393),(5670,455),(5290,455)]
draw.polygon([(round(x*scale),round(y*scale))for x,y in poly],fill=255)
rail=world.convert('RGBA');rail.putalpha(mask)
railbox=(round(5290*scale),round(328*scale),round(5670*scale),round(455*scale));rail=rail.crop(railbox)
report={'duration':42,'fps':30,'resolution':[1280,720],'map':[6324,724],'music':'Original 16-bar C major waltz, 72 BPM, five acoustic parts','interpolation':'local bidirectional Farneback optical flow, premultiplied RGBA','npcs':{'gardener':[1110,526],'baker':[2820,528],'elder':[5470,370]},'bridgeOcclusion':True}
(ROOT/'film-source'/'film-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))

def travel(t):
    if t<2:return t*t/4
    if t<=40:return t-1
    return 40-(42-t)**2/4

def actor(frame,name,x,y,phase,shadow=True):
    im=loops[name][int(phase*FPS)%len(loops[name])]
    left=round(x-144);top=round(y-210)
    if left>WIDTH or left+288<0:return
    if shadow:
        sh=Image.new('RGBA',(WIDTH,HEIGHT));d=ImageDraw.Draw(sh);r=22 if name!='fox' else 30
        d.ellipse((x-r,y-4,x+r,y+5),fill=(55,63,40,37));frame.alpha_composite(sh)
    frame.alpha_composite(im,(left,top))

def scene(t):
    distance=(world.width-WIDTH)*travel(t)/40;cam=round(distance)
    frame=world.crop((cam,0,cam+WIDTH,HEIGHT)).convert('RGBA')
    # NPCs live behind the moving characters, independently of the camera.
    for name,(x,y) in report['npcs'].items():actor(frame,name,x*scale-cam,y*scale,t+{'gardener':.25,'baker':1.1,'elder':2.2}[name],shadow=name!='elder')
    frame.alpha_composite(rail,(railbox[0]-cam,railbox[1]))
    walk_phase=distance/126
    actor(frame,'courier',400,592,walk_phase)
    actor(frame,'fox',565+10*math.sin(t*.6),596,walk_phase+.18)
    # Soft drifting seed fluff and a few creek glints add atmospheric motion without obscuring action.
    overlay=Image.new('RGBA',(WIDTH,HEIGHT));d=ImageDraw.Draw(overlay)
    for i in range(17):
        wx=(i*401+t*13)%world.width;x=wx-cam;y=470+(i*97)%135+8*math.sin(t*.9+i)
        if 0<x<WIDTH:d.ellipse((x,y,x+2.5,y+1.5),fill=(254,239,209,95))
    for i in range(9):
        wx=(4950+i*63)*scale-cam;wy=(458+5*math.sin(i*1.3))*scale
        if 0<wx<WIDTH:d.arc((wx-7,wy-2,wx+7,wy+2),0,175,fill=(235,253,232,round(75+40*math.sin(t*3+i))),width=1)
    frame.alpha_composite(overlay)
    return frame.convert('RGB')

# Composed contact sheet verifies character-ground relationships and districts BEFORE the full render.
contact=Image.new('RGB',(1280*2,720*3))
for i,t in enumerate([1,5.5,18,22,35,38]):
    im=scene(t);im.save(TMP/f'scene-{t:04.1f}.jpg',quality=94);contact.paste(im,((i%2)*1280,(i//2)*720))
contact.save(TMP/'scene-contact.jpg',quality=94)
scene(20.5).save(ASSETS/'scene-poster.jpg',quality=94)
if '--preview-only' in sys.argv:print('Composed preview ready');sys.exit(0)
cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','30','-i','-','-i',str(ASSETS/'film-score.wav'),'-map','0:v:0','-map','1:a:0','-vf','fade=t=in:d=0.7,fade=t=out:st=40.8:d=1.2','-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-t','42','-movflags','+faststart',str(ASSETS/'scene.mp4')]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
try:
    for i in range(FPS*DURATION):
        proc.stdin.write(scene(i/FPS).tobytes())
        if i%300==0:print(f'Rendered {i/FPS:.0f} / {DURATION}s',flush=True)
finally:proc.stdin.close()
if proc.wait():raise RuntimeError('Video encoder failed')
print('Finished assets/scene.mp4: 42 seconds, 1280 × 720, 30 fps, original soundtrack included',flush=True)
