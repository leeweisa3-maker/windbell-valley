# 风铃溪谷：动画短片制作记录

## 最终交付

42 秒、1280 × 720、30 fps 的配乐 MP4。横向摄像机经过三段相连的原创村庄背景，旅人与白狐在前方小路旅行，园丁浇花、面包师挥手、老人吹笛。网页播放已渲染的影片，另有可横向拖动的大地图。

用户明确纠正了早期俯视互动网页的方向，要求以参考项目为准交付村庄动画视频。早期网页保留在 `legacy-interactive/`，不再作为首页。

## 制作方式

参考组织：[aldegad/sprite-gen 的 village-scene.gif](https://github.com/aldegad/sprite-gen/blob/main/docs/assets/village-scene.gif)。成片展示参考：[yuanyang749/windbell-valley](https://github.com/yuanyang749/windbell-valley)。仅参考场景分层与交付方式，未复制其地图、角色、音乐或视频。

图片全部由内置 imagegen 生成。ChatCut 连续动作视频生成尝试被账号套餐拦截，未生成视频、未使用该模型成品。用户随后明确选择“改用本地逐帧动画与补帧，继续完成配乐 MP4”。因此最终采取关键帧绘图与本地双向 Farneback 光流补帧，未使用 Grok 或 RIFE。

- 三段背景各为 2172 × 724，相邻段重叠 96 像素渐变拼接，得到 6324 × 724 地图。
- 主角与白狐分别 6 张动作关键帧，1.2 秒周期，补为 36 帧。
- 园丁、面包师和吹笛老人各 4 张关键帧，按往返动作次序组成 4 秒周期，补为 120 帧。
- 固定鞋底锚点、共用缩放比例；图集实际行高不均，因此按实际分界切分。
- 洋红背景先抠成透明图，补帧在预乘 RGBA 上完成。双向光流用于姿态过渡；不相符的轮廓使用单向变形，避免交叉淡化产生双头或多条腿。
- 景深顺序：村庄背景 → NPC → 从原图提取的桥前侧石栏 → 旅人与白狐 → 轻微环境效果。
- 镜头首尾减速，沿整个村庄向右移动。行走周期按实际移动距离同步。
- 原创 16 小节、72 BPM、3/4 拍 C 大调曲，以长笛、尼龙弦吉他、弦乐、钟琴和原声低音五声部组成。乐谱保存在 JSON 与 MIDI，通过 macOS 乐器声库离线渲染，加入混响、响度控制和首尾淡化。
- FFmpeg 导出 H.264 / AAC MP4，音乐直接合在视频里，`faststart` 便于网页播放。

## 可复用图像提示词（整理版）

以下是最终素材的制作规格与提示词整理，不是付费视频模型提示词。

### 1. 山坡住居

Create one ultrawide 3:1 lateral village background, target 2172 × 724. Original warm Japanese hand-painted watercolor and gouache animation scenery, delicate brown outlines, cream plaster, aged blue-green slate, sage foliage, honey afternoon light from the upper left. Frontal cottage facades, a little post office and red cylindrical mailbox, flower gardens, laundry and an orchard. Pale blue sky and hazy lakeside hills behind. A completely level horizontal sandy walking lane spans y=73%-86%, with low daisies and grasses below. Leave both outer 12% quiet and free of buildings for panorama joins. No people, animals, text, logos, UI or borders. Not aerial or isometric.

### 2. 村中集市

Use the hillside background as style, scale, road height and lighting reference. Create a NEW adjacent 3:1 district: cream and timber bakery with ochre awning and bread trays, fruit and flower market stall, old plane tree with empty curved bench and hanging windbells, little fountain set behind the road. Match sky, distant hills, frontal facades, upper-left light, y=73%-86% level road and quiet outer-edge transition areas. No characters, readable signage or UI.

### 3. 河岸水车

Use the same hillside reference for scale, light and road height. Create a NEW riverside watermill district: cream plaster mill, blue-green slate roof, wooden water wheel, willow, turquoise creek and raised stone arch bridge in the midground. Bridge has a readable deck and near-side stone parapet for a later independently placed flute player. Creek stays behind the uninterrupted y=73%-86% foreground road. Quiet matching meadow at both edges. No people, animals, lettering or UI. Ultrawide 3:1 lateral panorama.

### 4. 角色参考

Exactly six isolated subjects in a 3-column, 2-row atlas on flat pure magenta #FF00FF. Warm painted cel animation. Top: right-facing courier woman with brown bob, ochre capelet, cream blouse, teal skirt, brown boots and satchel; right-facing ivory fox with caramel tail tip and sage scarf; straw-hatted gardener with sage cardigan, apron and blue watering can. Bottom: red-haired baker in blue apron holding a bread basket; silver-haired bespectacled flute player in blue vest and brown trousers; brass windbell with paper slip. Full bodies and props, fixed ground baselines, ample gutters, no labels, ground or shadows.

### 5. 行走关键帧

Use the character reference for identity. Six equal columns, two rows, ultrawide 3:1. Courier repeated across the top, fox across the bottom. Six distinct sequential right-facing walking poses spanning one cycle: contact, lowered support/passing, rising swing, opposite contact, opposite support/passing, opposite rising swing. Maintain clothing, profile, body size, hip position and baseline; natural arm, satchel, cape and tail movement. Solid pure magenta background, no floor or shadows. Verify actual row boundaries before extraction.

### 6. NPC 动作关键帧

Use the reference identities in a four-column, three-row 4:3 sheet. Gardener row: relaxed upright can, raise can, lean and tip with visible blue water, return with droplets. Baker row: hold basket with one arm, lift free hand, open wave outward, wave back and lower. Flute elder row: upright playing, slight left nod, slight right nod with small golden notes, return as notes fade. All feet planted, props remain attached to the correct hands, full bodies, fixed baselines and scale. Pure magenta background, no labels or ground.

## 复现

Python 需要 Pillow、NumPy、OpenCV；配乐声库渲染需要 macOS 与 Swift；编码需要 FFmpeg。

```sh
python3 tools/film_score.py
swiftc tools/render_score.swift -o /tmp/windbell-render-score
/tmp/windbell-render-score film-source/score.json film-source/film-score-raw.wav
ffmpeg -i film-source/film-score-raw.wav -af 'loudnorm=I=-20:LRA=7:TP=-2,afade=t=in:d=1.2,afade=t=out:st=39.5:d=2.5' -ar 48000 -ac 2 assets/film-score.wav
python3 tools/prepare_film.py
python3 tools/render_film.py
```

`prepare_film.py` 支持普通安装的 OpenCV，当前制作时将临时依赖安装在 `/private/tmp/windbell-pydeps`。中间帧位于忽略的 `output/film/`；生成素材、配乐谱和制作脚本纳入仓库。

动画是图像关键帧与光流之间的过渡，并非逐帧人工重绘；大的姿态变化处可能有局部形变。素材检查与接缝检查不能替代观看完整影片。
