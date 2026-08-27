# 评估、查询与合并

## 最小数据模型

同一学习者各设备使用相同 profile 和主题 key。topic ID 由二者规范化后派生；session ID 每次开启学习产生，device ID 每个安装产生。主题名称可不同，明确 key 才确定同一主题。`alias` 添加可检索别名，不自动合并不同 topic。

事件包含：协议版本、独立 ID、profile、device、本机 sequence、topic、session、带时区时间、kind 和 data。消息的唯一编号是来源身份，不是文本内容；两次都回答“我不知道”应保留两条。

## CLI 调用

所有路径使用安装后的绝对路径；以下 `$SKILL_ROOT` 与 setup.md 相同。`--home`、`--profile` 是子命令之前的全局参数。JSON 写进临时文件或从标准输入传入，避免长文本与 shell 转义混用。

```sh
python3 "$SKILL_ROOT/scripts/learn.py" search "辐辏"
python3 "$SKILL_ROOT/scripts/learn.py" resume optics/vergence
python3 "$SKILL_ROOT/scripts/learn.py" alias optics/vergence "双眼向内转"
python3 "$SKILL_ROOT/scripts/learn.py" hydrate optics/vergence
```

`resume` 返回各次评估、未被替代的评估、checkpoint heads、待判读用户消息 IDs、差异证据和缓存状态，不根据看过几章推算掌握百分比。它不会自行询问模型或生成新分数。

## 提交评估

先执行 capture 或读取 worker 状态，再用 `resume`／`export` 获取实际消息 ID。下例中的 ID 要来自实际账本：

```json
{
  "concept": "vergence-angle",
  "dimension": "reasoning",
  "level": "independent",
  "hints": 0,
  "evidence": ["QUESTION_EVENT_ID", "ANSWER_EVENT_ID"],
  "reason": "独立解释了距离变化的方向，并明确使用小角度近似。",
  "rubric": "vergence-v1",
  "assessor": "HOST_MODEL_VERSION",
  "novel": false,
  "supersedes": []
}
```

```sh
python3 "$SKILL_ROOT/scripts/learn.py" assess --host codex --host-session SESSION_ID --json "/absolute/path/to/assessment.json"
```

- dimension：`explanation`（解释概念）、`reasoning`（因果／假设）、`application`（应用）。不要求每次三个维度都测。
- level：`not_yet`（有作答证据但尚未完成）、`assisted`、`independent`、`transfer`。**没测过是缺评估记录，不是 not_yet。**
- 有提示时独立／迁移等级会被程序拒绝；transfer 需要显式 `novel: true`。这只是格式约束，不代表程序验证了“题目真的陌生”或“回答真的正确”。
- 证据必须含用户回答，并属于同一主题的一次来源 session；允许在后续 session 基于原始记录补评，不把不同来源会话混成一次表现。
- 修订评分时用 `supersedes` 引用旧 assessment；概念和维度须相同。旧事件保留，当前投影排除被替代记录。
- 评价者、rubric 与理由应可追踪；AI 判断不是认知测量的精确概率。

## Checkpoint 与并行合并

```json
{
  "next": "请预测IPD增大而目标距离保持不变时，辐辏角怎样变化，并说明原因。",
  "parents": ["CURRENT_HEAD_ID"],
  "current_question": "距离加倍为什么只能近似说角度减半？",
  "misconceptions": ["曾把近似比例关系当作精确恒等式"],
  "hints_given": ["提示画等腰三角形"],
  "sources": [{"url": "SOURCE_URL", "locator": "section/page/figure", "status": "read"}]
}
```

```sh
python3 "$SKILL_ROOT/scripts/learn.py" checkpoint --host codex --host-session SESSION_ID --json "/absolute/path/to/checkpoint.json"
```

第一次 parents 为 `[]`。继续当前分支时引用当前 head；两台设备离线各自推进后出现两个 head，不按时钟排序覆盖。若两段内容互补，新 checkpoint 的 parents 引用两个 head，AI 根据证据给出统一下一步；真正目标矛盾才请用户选择。程序校验 parents 属于同一 topic 的已有 checkpoint，不自动判断教学内容是否兼容。

## 数据操作

```sh
python3 "$SKILL_ROOT/scripts/learn.py" export optics/vergence --output "/absolute/path/to/private-export.json"
python3 "$SKILL_ROOT/scripts/learn.py" prune --days 30
python3 "$SKILL_ROOT/scripts/learn.py" delete-topic optics/vergence --confirm-key optics/vergence
```

export 拒绝覆盖已有文件；包含原文，当前未加密。prune 仅清理全部已确认、近期无缓存读取写入且无活动会话的旧主题原文，保留最小索引／去重凭据。之后 `hydrate` 重新下载；断联时显示档案已移出本机，不装作仍有证据。

delete-topic 是删除整个主题的显式操作：清除本机原文，加入待同步 tombstone。同步后服务端和其他设备应用删除；服务端尚未确认时仅本机生效。删除优先于迟到的离线消息。恢复同一知识的新学习可使用新 topic key；当前不做撤销删除。宿主本身保存的原始 transcript、手动导出的文件、服务端备份不在这个操作的删除范围，需分别管理。离线设备接收删除前仍可能保有旧副本。

## 手工诊断模式

```sh
python3 "$SKILL_ROOT/scripts/learn.py" start optics/vergence "辐辏角" --host-session MANUAL_SESSION
python3 "$SKILL_ROOT/scripts/learn.py" record --host-session MANUAL_SESSION --source-id UNIQUE_MESSAGE_ID --json "/absolute/path/to/message.json"
```

message.json 形如 `{"role":"user","text":"用户原始回答"}`。这是显式记录／测试入口，自动采集验收不使用它冒充宿主消息已经被捕获。
