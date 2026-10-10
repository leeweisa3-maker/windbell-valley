# 风铃溪谷 / Windbell Valley

[观看动画短片](https://leeweisa3-maker.github.io/windbell-valley/) · [直接观看 / 下载 MP4](https://leeweisa3-maker.github.io/windbell-valley/assets/scene.mp4)

一部温暖手绘的横向村庄漫游短片。旅人阿禾与白狐小棉沿路旅行，经过山坡住居、村中集市与河岸水车，遇见浇花的园丁、挥手的面包师与吹笛的老人。

- 成片：42 秒、1280 × 720、30 fps，H.264 / AAC，原创配乐已合入视频。
- 大地图：6324 × 724，可横向拖动与跳转街区。
- 动作：原创图像关键帧 + 本地双向光流补帧。旅人与白狐分别 36 帧循环，NPC 分别 120 帧循环。
- 配乐：原创 72 BPM 三拍小曲，长笛、尼龙弦吉他、轻弦乐、钟琴和低音；保留 MIDI 与乐谱数据。
- 网页：动画 / 全景地图切换、三位村民动作跳转、音乐开关、视频与地图下载。

[制作过程、素材规格与提示词](PROMPT.md)

## 文件

```text
index.html / style.css / app.js  静态展示页面
assets/scene.mp4                 带配乐的最终动画影片
assets/scene-poster.jpg          封面
assets/windbell-valley-panorama.png / .webp  完整地图
assets/film-score.wav            原创完整音轨
film-source/                    原始绘景、角色关键帧、MIDI、乐谱与合成报告
tools/prepare_film.py            透明角色提取、定位与光流补帧
tools/render_film.py             场景分层与影片合成
tools/film_score.py / render_score.swift  作曲数据与乐器声库渲染
legacy-interactive/              已备份的早期互动网页
```

参考了 [sprite-gen 村庄示例](https://github.com/aldegad/sprite-gen/blob/main/docs/assets/village-scene.gif) 的场景组织及 [yuanyang749/windbell-valley](https://github.com/yuanyang749/windbell-valley) 的视频展示方式。未复制参考项目素材。本版本没有使用 Grok 或 RIFE；ChatCut 视频生成因套餐限制未启动，用户选择了本地动画方案。

## 本地预览与发布

使用支持 HTTP Range 的本地服务，确保 MP4 可按时间跳转：

```sh
npx --yes http-server@14.1.1 . -a 127.0.0.1 -p 4174 -c-1
```

GitHub Pages 从 `main` 分支根目录发布，`.nojekyll` 禁用 Jekyll；所有媒体使用相对路径。默认静音自动播放，点击“开启音乐”收听。尊重系统减少动态效果偏好，启用时不自动播放。
