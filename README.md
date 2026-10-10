# 风铃溪谷 / Windbell Valley

一个温暖手绘风格的可漫游村庄。原创地图、四位角色动作图集、原创 76.8 秒器乐循环，纯 HTML / Canvas / CSS，无构建依赖。

## 游玩

- WASD / 方向键：行走；点击地面：沿路前往。
- E：靠近村民后交谈，靠近风铃后拾取；Esc：关闭对话。
- 拖动地图：移动镜头；滚轮或 ＋／−：缩放；⌖：全景。
- 午后 / 夜色：切换氛围；开启声音：播放配乐。
- 手机提供方向按钮。风铃收集保存在浏览器本地。

## 场景

逻辑世界 3072 × 2048，手绘地图原图 1536 × 1024。六个区域通过 35 个路径节点与 38 段通路相连：麦香小巷、风铃广场、向日葵坡、溪畔花甸、云间茶屋、晚风小祠。角色沿路径运动，避免直接穿越建筑与溪流。地图的远景、建筑和植被为统一绘景；角色、风铃、溪流光纹、花瓣、夜间灯光为独立渲染层。角色按纵坐标排序。

参考：[aldegad/sprite-gen 的 village-scene.gif](https://github.com/aldegad/sprite-gen/blob/main/docs/assets/village-scene.gif)。用户提供的短链接实际指向 sprite-gen，原标签 sprite 返回 404。参考只用于场景分层组织，未复制其素材。原参考为横向街景，本项目拓展为俯视漫游村庄。

## 素材与动作

- `assets/valley.png`：AI 原创绘景源文件；`valley.webp`：网页优化版本。
- `assets/characters.png`：透明 4 × 4 动作图集。行：旅人、麦婆婆、小葵、阿澄；列：正面待机、左步、右步、背面。运行时两步交替、镜像、呼吸起伏，NPC 巡游。
- `assets/atlas.json`：动作图集元数据。
- `assets/windbell-valley.wav`：原创无损配乐；`windbell-valley.mp3`：网页版本。
- `tools/compose.py`：原创作曲与合成源，C 大调，75 BPM，3/4，32 小节，钢琴琶音、长笛旋律、低音与钟声。无第三方音乐采样。需要 NumPy；导出 MP3 需要 FFmpeg。
- `ASSET-PROMPTS.md`：内置 imagegen 生成提示记录。

## 本地启动

```sh
python3 -m http.server 4173
```

访问 http://localhost:4173。浏览器要求用户点击后才可播放声音。Google 字体加载失败时采用系统字体。应用素材均本地托管。

## GitHub Pages

静态站点，无需打包。Pages 设置：Deploy from a branch → main → /(root)。所有资产使用相对路径，支持项目 Pages 子目录。`.nojekyll` 禁用 Jekyll 处理。

部署地址：https://leeweisa3-maker.github.io/windbell-valley/
