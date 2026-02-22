import { Scene2D, Circle, Rect, Text, VGroup, Layout, all, waitFor } from '@motion-canvas/2d';

// ============ 颜色定义 ============
const COLORS = {
  background: '#0f172a',
  primary: '#4ecca3',
  secondary: '#e94560',
  highlight: '#ffc107',
  text: '#ffffff',
};

// ============ 幕信息（从 audio_info.json 加载） ============
// TODO: 替换为实际的音频时长
const SCENES = [
  { id: 1, name: '开场', duration: 5.0 },
  { id: 2, name: '概念', duration: 10.0 },
  { id: 3, name: '总结', duration: 5.0 },
];

// ============ 场景 ============
export class MyScene extends Scene2D {
  constructor() {
    super({ background: COLORS.background });
  }

  // 动画序列
  *flow() {
    // 第1幕：开场
    yield* this.intro();

    // 第2幕：概念
    yield* this.concepts();

    // 第3幕：总结
    yield* this.summary();
  }

  *intro() {
    const title = new Text({
      text: '主题名称',
      fontSize: 48,
      fill: COLORS.primary,
    });

    this.add(title);
    title.opacity(0);
    
    // 淡入
    yield* title.opacity(1, 1);
    
    // 等待音频
    yield* waitFor(SCENES[0].duration - 2);
    
    // 淡出
    yield* title.opacity(0, 0.5);
  }

  *concepts() {
    const concepts = new VGroup({
      layout: { direction: 'column', spacing: 30 },
      y: -50,
    });

    const items = ['概念1', '概念2', '概念3'];
    for (const item of items) {
      concepts.add(
        new Text({ text: item, fontSize: 32, fill: COLORS.text })
      );
    }

    this.add(concepts);
    concepts.opacity(0);

    // 依次淡入
    for (const child of concepts.children()) {
      yield* child.opacity(1, 0.5);
      yield* waitFor(0.5);
    }

    yield* waitFor(SCENES[1].duration - 4);

    yield* concepts.opacity(0, 0.5);
  }

  *summary() {
    const summary = new Text({
      text: '总结内容',
      fontSize: 36,
      fill: COLORS.highlight,
    });

    this.add(summary);
    summary.opacity(0);

    yield* summary.opacity(1, 1);
    yield* waitFor(SCENES[2].duration - 2);
  }
}
