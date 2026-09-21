# 工程、字幕与导出

## 新工程才用模板

已有工程优先继续使用。模板采用已验证组合 Motion Canvas 3.17.2、Three.js 0.180.0、Vite 5.4.21，不声称是最新版。

~~~bash
python3 SKILL_DIR/scripts/scaffold.py /absolute/path/to/video-project
cd /absolute/path/to/video-project
npm ci
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-video.txt
.venv/bin/python scripts/prepare_audio.py
npm run check
npm run stills
npm run render
npm run verify
~~~

需要 Node.js、Python、ffmpeg/ffprobe 和 Chrome 或 Playwright Chromium。这些 npm 命令是模板提供的脚本，修改已有工程前先看它的 package.json。复制脚本不覆盖非空目录；初始静音只用于排版，不作为正式带配音交付。

## 显示文字与口播文字

scenes.json 的每幕保留连续 id、title、narration、min_duration，可增加人工分句的 segments：

~~~json
{
  "id": 1,
  "title": "取平均值",
  "narration": "三个测量值分别是二、四、六。相加后除以三，平均值是四。",
  "min_duration": 8,
  "segments": [
    {"text": "3 个测量值分别是 2、4、6。", "speech": "三个测量值分别是二、四、六。"},
    {"text": "相加后除以 3，平均值是 4。", "speech": "相加后除以三，平均值是四。"}
  ]
}
~~~

narration 必须与所有 speech 按顺序拼接一致。text 显示阿拉伯数值，speech 负责读法；例如 1.0 是版本还是测量值必须先辨明。没有 segments 时保留旧的自动分句方式；新数字密集文案优先显式分句。字幕与口播语义一致，不另写摘要。

默认 edge-tts 7.2.8；在线生成只发送旁白文本。要求离线或不宜外发时，用用户音频、本地 TTS 或有来源的强制对齐。音频缓存签名包含口播、声音和速度；每段最多重试 3 次。prepare_audio.py --cached-only 只读取有效缓存，缺失或过期会报错。

词边界采用 offset、duration（100 ns）及 text。先规范化并核对边界文字与口播，再按每段 speech 的范围取首尾词时刻，给对应的 text。不要按字数均分时间、自动丢字或把猜测标成真实边界。若同一个词跨字幕边界，调整分句/对齐。

导入其他服务音频时适配其真实边界来源，不伪造缓存签名。每幕时长从音频实际时长、留白和最低展示时间求出，再统一按帧取整。字幕的开头、结尾、连续性和整片范围均须检查。

## 动画和排版

- 所有动作由可寻址时间或幕进度决定，不使用墙钟或独立无限自转。随机数据固定种子。抽任意帧应可复现。
- 按语音分句边界或明确词锚点触发高亮与计算。口播改变后更新锚点，禁止静默退回旧时刻。
- 模板使用 src/scenes/film.tsx、src/space3d.ts、src/project.ts；timing.json 和 subtitles.json 由音频准备脚本生成。
- LaTeX 的反斜线使用可靠的字符串转义；缓存静态公式，避免每帧解析复杂 TeX。检查上下标、矩阵、长分式是否裁剪。
- 3D 几何、端点、标签统一应用显示变换。复用 WebGLRenderer、几何和材质；半透明对象注意绘制顺序和 depthWrite。
- 1080p 可从约 38–42 px 字幕起步，左右留 100 px、底部独立安全区；按实际字体测宽，超长按语义拆句，不仅凭字符数估算。
- 画内字幕与外挂轨避免双重显示。SRT/VTT 用于剪辑；模板不依赖 ffmpeg 的 libass 烧字幕。

## 验证与交付

1. 检查本题的数值不变量、单位、符号、边界、近似条件、坐标转换和聚合顺序。
2. 类型检查和渲染日志通过；ffprobe 检查最终尺寸、帧率、时长、音轨，尾句未截断。
3. 最终 MP4 解码后抽查 3D、投影、公式密集、2D 计算和结论画面；关键连续动作逐步抽查。实际视听抽查配音与字幕，明确已检查范围。
4. 模板 verify 检查每条字幕中点底部白色像素和预计字体宽度，验证无外挂轨时仍有画内字幕。该启发式不是 OCR，也不验证语义或发音；改布局/主题后同步调整。
5. 可比对成片与新旁白音频以确认没有误用旧配音，但不能将该比对称为人工发音审校。

最终工程保留源文件、依赖锁、案例、旁白/边界、字幕、MP4 和必要验证记录；不打包 node_modules、虚拟环境、临时大帧、敏感配置和无许可素材。skill 只留通用规则与可复用工具，具体工程留在任务输出目录。预览只绑定本地地址，只关闭自己启动的服务，不把本地预览声称为已发布网站。
