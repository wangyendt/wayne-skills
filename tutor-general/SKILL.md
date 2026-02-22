---
name: tutor-general
description: |
  通用的知识教学视频制作技能，生成带配音的 Motion Canvas 动画视频。
  核心工作流：内容分析 → 分镜脚本 → TTS音频 → 验证更新 → Motion Canvas代码 → 渲染验证
  触发条件：需要制作任何主题的教学视频、科普讲解、技术原理演示
---

# Tutor General - 通用知识教学视频

> ⚠️ **重要声明**：本技能受 tutor-math-geometry 启发，用 Motion Canvas 替代 Manim，适配更广泛的知识点讲解。

## 与 tutor-math-geometry 的区别

| 维度 | tutor-math-geometry | tutor-general |
|------|---------------------|--------------|
| 主题 | 数学几何 | 任何知识点 |
| 渲染引擎 | Manim | Motion Canvas (TypeScript) |
| 代码风格 | Python | TypeScript |
| 动画类型 | 数学公式/图形 | 流程图/示意图/动画 |

## 核心工作流

```typescript
WORKFLOW = [
    // 步骤1: 内容分析
    {
        "step": 1,
        "name": "analyze_content",
        "input": "主题/文本/URL",
        "output": "content_analysis.md",
        "tasks": ["提炼核心概念", "确定讲解结构", "规划可视化方式"]
    },

    // 步骤2: 分镜脚本
    {
        "step": 2,
        "name": "storyboard",
        "input": "content_analysis.md",
        "output": "{日期}_{主题}_分镜.md",
        "tasks": ["定义幕结构", "设计画面/字幕/读白", "规划动画类型"]
    },

    // 步骤3: TTS生成
    {
        "step": 3,
        "name": "generate_tts",
        "input": "分镜脚本",
        "output": "audio/audio_{三位幕号}_{幕名}.wav + audio_info.json",
        "command": "python scripts/generate_tts.py audio_list.csv ./audio --voice xiaoxiao"
    },

    // 步骤4: 验证更新
    {
        "step": 4,
        "name": "validate_audio",
        "input": "分镜.md + audio/",
        "output": "更新后的分镜.md(填充时长) + audio_info.json",
        "command": "python scripts/validate_audio.py 分镜.md ./audio",
        "check": ["音频存在性", "时长>0", "数量匹配"]
    },

    // 步骤5: Motion Canvas 脚手架
    {
        "step": 5,
        "name": "scaffold",
        "input": "分镜.md + audio_info.json",
        "output": "src/scene.ts (伪代码框架)",
        "template": "templates/scene_scaffold.ts",
        "must_include": [
            "createScene() - 场景创建",
            "COLORS - 颜色定义",
            "SCENES[] - 幕信息数组(从audio_info.json加载时长)",
            "Motion Canvas API 调用"
        ]
    },

    // 步骤6: 生成代码
    {
        "step": 6,
        "name": "implement",
        "input": "脚手架 + 分镜.md + audio_info.json",
        "output": "完整的 Motion Canvas 代码",
        "rules": [
            "根据分镜实现每幕动画",
            "使用 @motion-canvas/2d 库",
            "画面时长 >= 音频时长",
            "TypeScript 类型正确"
        ]
    },

    // 步骤7: 检查与渲染
    {
        "step": 7,
        "name": "check_and_render",
        "input": "Motion Canvas 项目",
        "output": "视频文件",
        "command": "npm run export",
        "check": ["TypeScript 编译", "动画同步", "导出成功"]
    }
]
```

---

## 步骤1：内容分析

**目标**：理解主题，提炼核心概念，规划可视化方案。

### 输出格式
```markdown
## 内容分析

### 主题
{主题名称}

### 核心概念（3-5个）
1. 概念1：...
2. 概念2：...
3. 概念3：...

### 讲解结构
- 引入：...
- 展开：...
- 总结：...

### 可视化方案
- 概念1 → 流程图
- 概念2 → 示意图
- 概念3 → 动画演示
```

---

## 步骤2：分镜脚本

**目标**：定义视频结构，结尾预留音频文件名（时长为空）。

### 文件命名
`{日期}_{主题}_分镜.md`

### 分镜脚本结构
```markdown
# 分镜脚本 - {主题名称}

## 分镜设计

### 第1幕：{幕名}
**画面**: ...
**字幕**: ...（简洁，≤20字）
**读白**: ...（详细，口语化）
**动画类型**: 淡入/移动/缩放/高亮
**时长**: {音频时长}

---

### 第2幕：{幕名}
...

## 音频生成清单

| 幕号 | 文件名 | 读白文本 | 时长 | 说话人 | 情感 |
|------|--------|----------|------|--------|------|
| 1 | audio_001_{幕名}.wav | "读白文本" | | xiaoxiao | 热情 |
| 2 | audio_002_{幕名}.wav | "读白文本" | | xiaoxiao | 平和 |
```

### Motion Canvas 动画类型
- `fade-in` - 淡入
- `fade-out` - 淡出
- `move` - 移动
- `scale` - 缩放
- `rotate` - 旋转
- `highlight` - 高亮
- `draw` - 绘制（用于流程图）

---

## 步骤3：TTS生成

**命令**：
```bash
python scripts/generate_tts.py audio_list.csv ./audio --voice xiaoxiao
```

**输出**：
- `audio/audio_001_{幕名}.wav`
- `audio_info.json`

---

## 步骤4：验证更新

**命令**：
```bash
python scripts/validate_audio.py 分镜.md ./audio
```

**检查项**：
- [ ] 音频文件存在
- [ ] 时长 > 0
- [ ] 数量匹配

---

## 步骤5：Motion Canvas 脚手架

**模板**：`templates/scene_scaffold.ts`

**必须包含**：
```typescript
// 颜色定义
const COLORS = {
  background: '#0f172a',
  primary: '#4ecca3',
  secondary: '#e94560',
  highlight: '#ffc107',
  text: '#ffffff',
};

// 幕信息（从 audio_info.json 加载）
const SCENES = [
  { id: 1, name: '开场', duration: 5.0 },
  { id: 2, name: '概念', duration: 10.0 },
  // ...
];

// 场景创建
export function createScene() {
  // ...
}
```

---

## 步骤6：Motion Canvas 代码实现

### 核心 API

```typescript
import { 
  Scene, 
  Circle, 
  Rect, 
  Line, 
  Text, 
  VGroup, 
  layout,
  fadeIn,
  any,
  all,
  waitFor
} from '@motion-canvas/2d';

// 创建圆形
const circle = new Circle({ radius: 50, fill: '#4ecca3' });

// 创建文字
const text = new Text({ 
  text: 'Hello', 
  fontSize: 32, 
  fill: 'white' 
});

// 动画序列
circle.fill('red', 1);

// 等待音频
yield* waitFor(audioDuration);
```

### 常用动画模式

```typescript
// 淡入
new Rect().opacity(0).fadeIn(1);

// 移动
new Circle().position([100, 0]).move([200, 0], 1);

// 高亮
new Circle().stroke('#ffff00', 0.5).back(0.5);

// 流程图
new Layout({ direction: 'row', spacing: 50 })
  .add(new Rect())
  .add(new Arrow())
  .add(new Rect());
```

---

## 步骤7：渲染

### 开发模式（实时预览）
```bash
npm run serve
```

### 导出视频
```bash
npm run export
```

### Motion Canvas 优势
- ✅ 实时预览，调试快
- ✅ TypeScript 类型安全
- ✅ 可交互预览
- ✅ 适合流程图/示意图

### 对比 Manim
| 维度 | Manim | Motion Canvas |
|------|-------|---------------|
| 语言 | Python | TypeScript |
| 实时预览 | 需渲染 | 即时预览 |
| 适合 | 数学图形 | 流程/演示 |
| 输出 | 视频 | 视频/可交互 |

---

## 依赖

- Node.js 16+
- npm
- @motion-canvas/core
- @motion-canvas/2d
- @motion-canvas/ui
- edge-tts (用于TTS)
- ffmpeg (用于视频导出)

## 安装

```bash
npm install
```

## 使用示例

```bash
# 1. 复制模板
cp -r templates/* ./my-project/

# 2. 生成分镜脚本
# 编辑 {主题}_分镜.md

# 3. 生成 TTS
python scripts/generate_tts.py audio_list.csv ./audio

# 4. 验证音频
python scripts/validate_audio.py 分镜.md ./audio

# 5. 实现动画
# 编辑 src/scene.ts

# 6. 开发预览
npm run serve

# 7. 导出
npm run export
```

---

## 目录结构

```
tutor-general/
├── SKILL.md              # 本文件
├── README.md             # 说明文档
├── scripts/
│   ├── generate_tts.py       # TTS生成脚本
│   ├── validate_audio.py      # 音频验证脚本
│   └── audio_list.example.csv # 示例
├── templates/
│   ├── scene_scaffold.ts     # 脚手架模板
│   └── package.json         # 项目模板
├── references/
│   └── storyboard_sample.md # 分镜示例
└── assets/
    └── (静态资源)
```

---

## 注意事项

1. **动画同步**：画面时长必须 >= 对应音频时长
2. **TypeScript**：确保类型正确，Motion Canvas 需要编译
3. **实时预览**：开发时用 `npm run serve` 实时查看效果
4. **导出时间**：视频导出需要较长时间，请耐心等待
