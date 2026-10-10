"""Prepare original panoramas and register key drawings for local optical-flow animation."""
from pathlib import Path
import numpy as np
from PIL import Image
import json, sys
sys.path.insert(0,"/private/tmp/windbell-pydeps")
import cv2
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'film-source';TMP=ROOT/'output'/'film';TMP.mkdir(parents=True,exist_ok=True)
parts=[Image.open(SRC/f'district-{i:02}.png').convert('RGB').resize((2172,724),Image.Resampling.LANCZOS) for i in range(1,4)]
world=Image.new('RGB',(6324,724));world.paste(parts[0],(0,0))
for i in [1,2]:
    x=i*2076;a=np.asarray(world.crop((x,0,x+96,724))).astype(float);b=np.asarray(parts[i].crop((0,0,96,724))).astype(float)
    f=np.linspace(0,1,96)[None,:,None];blend=Image.fromarray((a*(1-f)+b*f).astype('uint8'))
    world.paste(parts[i],(x,0));world.paste(blend,(x,0))
world.save(ROOT/'assets'/'windbell-valley-panorama.png');world.save(ROOT/'assets'/'windbell-valley-panorama.webp',quality=94,method=6)

def key(image):
    arr=np.asarray(image.convert('RGB')).astype(float)
    dist=np.sqrt(np.sum((arr-[255,0,255])**2,axis=2))/441.7
    alpha=np.clip((dist-.095)/.08,0,1)
    # Recover edge colors from their original chroma blend to avoid purple outlines.
    safe=np.maximum(alpha,.04)[...,None]
    rgb=np.clip((arr-(1-alpha[...,None])*[255,0,255])/safe,0,255)
    return Image.fromarray(np.dstack([rgb,alpha*255]).astype('uint8'),'RGBA')

def cut(sheet,row,col,cols,rows):
    w,h=sheet.size
    if rows==2:
        y0,y1=(0,round(h*.61)) if row==0 else (round(h*.61),h)
    else:y0,y1=round(row*h/rows),round((row+1)*h/rows)
    return key(sheet.crop((round(col*w/cols),y0,round((col+1)*w/cols),y1)))

def register(images,name,figure_height,anchor='feet'):
    # Scale every drawing by ONE shared factor, never per-frame size jitter.
    boxes=[Image.fromarray((np.asarray(im)[:,:,3]>100).astype("uint8")*255).getbbox() for im in images]
    heights=[b[3]-b[1] for b in boxes]
    factor=figure_height/np.median(heights)
    frames=[]
    for im,b in zip(images,boxes):
        a=np.asarray(im)[:,:,3]; y=b[3]-1
        if anchor=='head':
            band=a[b[1]:b[1]+max(8,int((b[3]-b[1])*.2))];xs=np.where(band>100)[1];cx=(xs.min()+xs.max())/2-figure_height/factor*.07
        else:
            band=a[max(b[1],b[3]-int((b[3]-b[1])*.13)):b[3]];xs=np.where(band>100)[1];cx=float(np.median(xs))
        scaled=im.resize((round(im.width*factor),round(im.height*factor)),Image.Resampling.LANCZOS)
        out=Image.new('RGBA',(288,224),(0,0,0,0));out.alpha_composite(scaled,(round(144-cx*factor),round(210-y*factor)))
        frames.append(out)
    keys_dir=TMP/name/'keys';keys_dir.mkdir(parents=True,exist_ok=True)
    for i,im in enumerate(frames):im.save(keys_dir/f'{i:02}.png')
    return frames
walk=Image.open(SRC/'walk-keys.png');npc=Image.open(SRC/'npc-keys.png')
config=[('courier',[cut(walk,0,c,6,2)for c in range(6)],150,'head',5),('fox',[cut(walk,1,c,6,2)for c in range(6)],82,'feet',5),('gardener',[cut(npc,0,c,4,3)for c in range(4)],128,'feet',1.5),('baker',[cut(npc,1,c,4,3)for c in range(4)],134,'feet',1.5),('elder',[cut(npc,2,c,4,3)for c in range(4)],120,'feet',1.5)]
meta={}
for name,images,height,anchor,rate in config:
    keys=register(images,name,height,anchor)
    seq=list(range(len(keys))) if name in ['courier','fox'] else [0,1,2,3,2,1]
    period=len(seq)/rate
    dest=TMP/name/'frames';dest.mkdir(exist_ok=True)
    total=round(period*30)
    normalized=[np.asarray(im).astype(np.float32)/255 for im in keys]
    premul=[np.dstack([a[:,:,:3]*a[:,:,3:4],a[:,:,3]]) for a in normalized]
    flow_images=[cv2.cvtColor(np.clip((a[:,:,:3]*a[:,:,3:4]+.45*(1-a[:,:,3:4]))*255,0,255).astype('uint8'),cv2.COLOR_RGB2GRAY) for a in normalized]
    gy,gx=np.mgrid[0:224,0:288].astype(np.float32)
    flows={}
    for i in range(len(seq)):
        a,b=seq[i],seq[(i+1)%len(seq)]
        forward=cv2.calcOpticalFlowFarneback(flow_images[a],flow_images[b],None,.5,5,35,5,7,1.5,0)
        backward=cv2.calcOpticalFlowFarneback(flow_images[b],flow_images[a],None,.5,5,35,5,7,1.5,0)
        flows[i]=(forward,backward)
    for frame in range(total):
        position=frame/30*rate;i=int(position)%len(seq);f=position-int(position)
        a,b=seq[i],seq[(i+1)%len(seq)];forward,backward=flows[i]
        wa=cv2.remap(premul[a],gx-f*forward[:,:,0],gy-f*forward[:,:,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
        wb=cv2.remap(premul[b],gx-(1-f)*backward[:,:,0],gy-(1-f)*backward[:,:,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
        # Occlusion guard: never crossfade two nonmatching silhouettes (double heads/limbs).
        blend=wa.copy() if f<.5 else wb.copy()
        match=(wa[:,:,3]>.85)&(wb[:,:,3]>.85)&(np.max(np.abs(wa[:,:,:3]-wb[:,:,:3]),axis=2)<.16)
        average=(1-f)*wa+f*wb
        blend[match]=average[match]
        alpha=blend[:,:,3:4]
        rgb=np.clip(blend[:,:,:3]/np.maximum(alpha,.001),0,1)
        rgba=np.dstack([rgb,alpha]);rgba[alpha[:,:,0]<.025]=0
        Image.fromarray((rgba*255).astype('uint8'),'RGBA').save(dest/f'{frame+1:03}.png')
    files=sorted(dest.glob('*.png'));meta[name]={'cycleSeconds':period,'fps':30,'frames':len(files),'anchor':[144,210],'keyFrames':len(keys),'interpolation':'bidirectional Farneback optical flow in premultiplied RGBA with silhouette occlusion guard'}
    print(name,meta[name],flush=True)
(SRC/'animation-report.json').write_text(json.dumps(meta,indent=2))
# Asset contact sheet for visual verification of scale, cells and chroma cleanup.
contact=Image.new('RGB',(288*6,224*5),(238,239,221))
for r,(name,*_)in enumerate(config):
    files=sorted((TMP/name/'frames').glob('*.png'))
    for c in range(6):
        im=Image.open(files[round(c*(len(files)-1)/5)]).convert('RGBA');contact.paste(im,(c*288,r*224),im)
contact.save(TMP/'animation-contact.png')
print('Prepared 6324 × 724 panorama and five optical-flow animation loops',flush=True)
