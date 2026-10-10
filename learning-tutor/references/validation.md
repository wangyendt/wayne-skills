# 停止后的显式补传与缺口修复（2026-10-10）

增加 `learn.py flush`，只上传指定已停止聊天的停止前完整记录和图片；在内存中固定 ID 清单，不临时 start、不写 active、不读 transcript、不自动重试。默认前台总预算 180 秒、单次 RPC 最多 60 秒。新增 `reconcile` 作为显式离线管理入口，从 Agent 实际取得的 Codex host-read 原始证据恢复停止前缺失完整轮次，保留原始中断轮次；来源标签为 host-read-recovery，不称作自动采集。真实性依赖可信宿主读取，不对任意导入 JSON 作密码学认证。

- 新增 21 项回归：补传不改变完整 capture 行／游标、停止后隐私内容与其他聊天隔离、固定 ID 快照、共享 topic 仅借结构 envelope、旧会话幂等补传、ACK 丢失、图片失败重开本地账本重试、错误回执保留 bytes、缺少 stop 边界、不完整轮次保持、并发锁、预算耗尽无新请求、外部重开撤销权限，以及可信缺失轮次恢复的身份／启停区间／图片入队证明／事务／幂等边界。
- 本机 Python：130 项，121 项通过、9 项 PostgreSQL 独立环境测试按配置跳过；Node 桥接 2 项通过；skill frontmatter 与 diff 检查通过。本次没有修改服务器协议，未冒充重新运行 PostgreSQL 集成测试。
- 当前真实 Codex 聊天的宿主读取接口确实返回文档轮次的 completed 状态、原生消息 IDs、最终回复及 9 张图片的成功入队回执；先在临时 SQLite 副本验证恢复后采集关闭、9 图获得完整轮次资格，副本随测试清理。该核验不等于服务器已收到图片；真实投递仍以 ready 回执为准。
- 全部合成回归在临时本地账本／回环服务中执行并清理，无 personal／远端测试写入；未增加 worker、定时任务或重新安装 hooks。SkillTruck 更新与真实上传回执须另行核验。

# 大型宿主事件回归（2026-10-10）

Codex Desktop 生图产生的 `event_msg/item_completed` 行超过 2 MiB，旧采集器在识别工具元数据前报错，后续轮次留在原 transcript 中待补采。修复把原始事件包上限与可见内容上限分开（64 MiB／2 MiB），不采集工具二进制、不丢弃可见文本或完成回执、不重置游标。

- 新增 6 项回归，先在旧实现复现失败，再通过修复：大型工具事件后的最终回复和完成证明、重复补采与完整前缀 hash、超大半条尾部、完整坏行／未知格式事务回滚、可见正文超限显式错误、图片附件文本与摘要保留、原始事件包硬上限。
- 本机 Python：109 项中 100 项通过，9 项 PostgreSQL 环境测试按配置跳过；Node 桥接 2 项通过，skill frontmatter 验证通过。本次合成测试使用临时本地账本，测试结束自动清理；未写入 personal 或远端测试数据。
- 本条记录为源码回归结果；本机安装与当前真实聊天补采／服务端回执须分别核验，不以测试通过代替上传成功。

# 事件驱动版实机验收（2026-10-09）

本次源码已提交并推送，使用 skilltruck 更新本机 Codex／Claude 的全局 learning-tutor；逐文件 hash 与源码一致。已安装两套 hooks 与 Claude 的原生 `/learn-start`／`/learn-stop` 别名，保留其他 hooks 和默认 skilltruck 的 80 项选择集。全局 hook 配置写前备份；Codex 的新定义仍需按宿主 `/hooks` 流程审核信任，测试只在隔离环境使用单次信任参数，不伪造持久信任。

## 自动化与真实链路

- 本机 Python：103 项中 94 项通过，9 项 PostgreSQL 环境测试在本机跳过；随后在 hx470 独立测试 profile 上运行这 9 项，全部通过。Node 桥接 2 项通过；skill 验证与 diff 检查通过。
- Codex CLI 0.154：真实原生 prompt／Stop／SessionEnd、跨进程 resume、完整轮次回执和 `/learn-stop` 已验证；最后一轮回复在 PostgreSQL 中恰有一条，重复投递不重复入库。使用隔离 CODEX_HOME 与 CLI 内置默认模型绕开本机原有模型配置的不兼容，未修改用户模型设置。桌面 UI 的加载／信任仍应单独确认。
- 真实 SSH／PostgreSQL／OSS：合成图 bytes 在不完整轮次时不发送；故障注入提示去重；停止后冻结；重开同一聊天补传；图片 ready 回执、下载 bytes 的 SHA-256 一致；不完整测试输入在服务器中为 0 条。
- Claude Code 2.1.233：注册后的原生启停确实修改绑定，真实 transcript 新格式能解析。OAuth 登录已过期，因此成功助手回复＋Stop 的完整实机路径仍待重新登录后验收；不把 API 错误或本地命令输出假定为完成的学习轮次。
- OpenClaw 仅完成合成桥接测试，没有真实 Gateway／新版 SQLite 历史验收。Windows／Linux 客户端尚待验收。

## 实机发现与修正

1. Codex 新增 `world_state`／`token_usage_record`，Claude 新增 `attachment`／`mode`：只跳过已识别非可见 metadata；Claude API 错误与 sidechain 排除。
2. Claude 首次 prompt 可能早于 transcript 文件创建：绑定宿主给定的精确路径，不创建／覆盖宿主文件，后续补采。
3. Claude 控制指令需注册原生别名；安装器显式 `--commands-dir` 才写入，保留非本 skill 的既有命令。
4. CLI 退出会取消异步上传：Stop 改为有预算的同步收尾；其他事件异步补传。Stop 在同一个总预算内等待上传锁，不假定两个 handler 按配置顺序执行。真实 SSH 多次 RPC 与图片校验需要余量：Stop 总网络预算 30 秒、handler 35 秒；失败仍留本地。

回归覆盖完整性门控、延迟最终文本、事务回滚、冻结／恢复、跨聊天隔离、ACK 丢失幂等、通知去重与恢复、图片源文件删除后补传、重复回答、并发 Stop、只读历史拉取、分宿主入口、旧队列保守迁移及原生初始化时序。

## 测试数据清理

所有写入均使用独立 `learning-tutor-test-*` profile，不混入 personal。测试结束后删除测试 OSS 对象并核验不存在；删除该 profile 的 events、topics、receipts、tombstones、assets、asset_tombstones、profiles，七张表的剩余数量全部为 0；删除远端私有测试配置与临时测试代码。本机隔离状态、测试会话／图片、日志及临时 skilltruck 配置／缓存清理。个人账本保留原 47 个事件、pending=0、录制 inactive。

以下保留旧版历史验收，不代表 worker 仍是当前使用方式。

---

# 验证记录

日期：2026-08-27。对象：learning-tutor 本地首版、PostgreSQL 记录后端与独立图片存储。自动化测试使用合成数据；另经用户明确要求完成一次真实 Codex 学习试用、记录审计及后端补传。真实记录只保存在用户私有状态和 hx470，不写入仓库。OSS／数据库凭据保存在 hx470 私有配置中。

## 环境与命令

基线 commit：`5b8ccdf`；本轮新增代码与文档尚未提交。开发与测试环境为 macOS、Python 3.9.13、Node.js v25.5.0。核心无新增 Python 依赖。运行命令（仓库根目录）：

```sh
python3 -m unittest discover -s learning-tutor/tests -v
LEARNING_TEST_PYTHON="$(command -v python3)" node --test learning-tutor/tests/test_openclaw.mjs
python3 /absolute/path/to/skill-creator/scripts/quick_validate.py learning-tutor
```

本地 Python 发现 79 项测试：**70 项离线测试通过、9 项需独立数据库配置的测试按预期跳过**。这 9 项在 hx470 独立合成 profile 上全部通过（约 0.9 秒）。另有 **2 项 Node 插件桥接测试通过**。Skill frontmatter 验证通过。Node 测试模拟插件 API 并实际启动临时 worker，不等于真实 OpenClaw Gateway 已接入。

## 覆盖内容

- SQLite 落盘、重开后读取、重复 source ID 去重、相同文字的独立回答保留。
- 原始用户证据、提示次数、陌生题标记、后补评估、评分修订与 checkpoint 分支合并。
- 三种 JSONL 合成格式、开始前／停止后不导入、分析／工具内容排除、附件仅摘要描述。
- 半条写入、完整坏行、未知嵌套类型、文件截断、停止优先与缺口记录。
- 回环服务的双设备同步、ACK 丢失／损坏、删除优先、缓存清理与恢复。
- 大消息的字节预算、分页失败的原子恢复、并发 source 重放、worker 心跳。
- 双语清单、Markdown 本地链接、辐辏角解析例子与边界。
- 图片队列离线重开、收据身份／hash 校验、ACK 丢失重放、上传／删除并发、无覆盖下载、SSH 参数与错误脱敏。
- 记录 SSH 配置／参数边界、协议整数版本、服务身份变化、错误脱敏、空 query 默认分页、引用共享验证、NUL 原文／投影处理。

## hx470 PostgreSQL 记录链路

用户明确要求接通记录后端后，增加记录表／查询视图和非管理员 `learning_tutor_records` 账号，通过已有 SSH 调用，无新增监听端口。与图片账号分离，不写个人记忆表。

真实 PostgreSQL 17、Psycopg 3.3.4、服务端 Python 3.12 上的 9 项测试覆盖：

1. 入库与 hash 回执、相同事件重放、同 ID 改内容冲突。
2. 无效评分引用使整批事件／receipt／cursor 回滚。
3. 同设备重复序号冲突。
4. 带 NUL 原文逐字节恢复，JSONB 投影显式标记。
5. 批内删除优先、原文移除、迟到上传不复活。
6. profile／协议版本／路径边界。
7. 提交后丢失 ACK、重试、第二独立账本续学、清理缓存后恢复。
8. 两个并发 writer 串行分配 cursor，读取只见已提交数据。
9. 大消息按字节分页，预算不足明确报错。

测试使用单独的 `learning-tutor-test-…` profile，运行后删除其记录、去重凭据、profile 和临时私有配置；不混入 personal。

## 本次真实学习记录审计

审计对象为用户显式开启后的一次 Codex transcript 区间，停止边界后不采集。原有 46 个事件：主题 1、会话起止 2、对话 24、评估 9、checkpoint 10；ID／hash／引用和分支关系通过校验。

- 9 条学习回答都有证据评估：独立完成 7、有提示完成 1、首次未通过 1。普通采集指令不作为知识题评分。
- 原始错误和提示后纠正同时保留；未把提示后答对写成独立掌握，未声称长期保持或真实生理模型掌握。
- 发现最新 checkpoint 含历史“仍录制／未接通”运行状态。补充一个维护 checkpoint 清理这类过期措辞，保留旧记录、学习事实、评估和图片引用，总计 47 个事件。
- PostgreSQL 最终确认 47 个事件、47 条去重凭据，11 个 checkpoint 仅剩一个最新 head；本机 pending 为 0。真实后端补传以事件 ID／hash 回执确认；另用全新临时本地状态读取同一档案核对恢复，非第二台物理电脑验收。
- 用户停止录制后保持 inactive，测试与同步不重新绑定 transcript；未将后续工程讨论导入学习原文。此次试用临时 worker 已停止。
- 一张真实教学图保存在私有 OSS，并在 PostgreSQL 图片索引和 checkpoint sources 中关联；合成图片测试与它分开。

## hx470 图片链路实测

经用户明确确认，创建 `personal_knowledge.learning.assets` 与 `learning.asset_tombstones`、专用非管理员数据库账号，保存服务端私有凭据，安装独立 Python 3.12 虚拟环境与固定版本依赖。OSS 根 prefix 为 `learning-tutor/`，实查 region 为深圳，版本控制未启用。

用 69 字节、1×1 像素的合成 PNG 实测：

- 客户端先 SQLite 入队，再通过 SSH 调用 hx470，OSS 上传、私有 ACL、服务器回读 SHA-256、PostgreSQL ready 回执均成功。
- 同一台 macOS 上第二个独立临时客户端目录，成功从远端查询并下载；下载与原文件逐字节一致。这是跨状态／会话测试，不是第二台物理电脑验收。
- 匿名 OSS GET 返回 **403**；未向客户端提供密钥或永久公开 URL。
- 同 ID 相同请求重放返回原记录；同 ID 不同说明被拒绝。
- 删除后查询为空、对象 GET 返回 **404**；删除后重放旧上传、先删除 ID 再迟到上传均被拒绝。
- 测试对象与两条诊断 ID 的数据库记录已清理；根目录保留私有空目录标记，方便 OSS 控制台显示。运行测试未访问其他业务对象或修改 bucket 全局策略。

本地图片客户端仍为标准库；OSS SDK、Psycopg、Pillow 只安装在服务器独立目录。真实生成工具到显式入队这一步依赖 Agent 执行，未将其描述成 hook 自动保证。

## 独立检查

独立测试者在临时目录走通：A 开始学习／采集／评分，B 续学，两台设备断联继续，本地记录补传，双分支合并后 B 恢复，结束后停止采集。独立审查发现并促成修复：畸形字段异常、停止时半条记录缺口、按条数分批导致大消息阻塞、评估测试 helper 参数冲突、纸面数值的小数误差。测试从不通过手工录入冒充真实宿主已自动捕获。

本轮独立审查新增 23 项离线记录协议／SSH 测试，促成协议布尔版本误接受、PostgreSQL NUL 投影和 Python 3.9 空 query 处理修复；未访问真实学习状态或服务器凭据。

## 仍待验证／未实现

- 除本次显式绑定试用外，Codex CLI／桌面、Claude Code 和 OpenClaw 各入口的完整消息覆盖、显示文本一致性、steering、工具问答、强退和历史轮转；全局 hooks 未安装。
- Windows、Linux、WSL2 客户端实机；Linux 服务器端已实测，不等于这些系统的宿主采集已验收。
- 教学事件公网 HTTPS 网关、令牌撤销、反代、备份恢复与远端删除 SLA。
- 新版 OpenClaw SQLite transcript 适配、自动发现生成图片、图片 HTTPS 入口、Windows 图片客户端与多台物理设备验收。
- OSS 版本控制开启后的读删恢复、整主题跨设备图片级联删除、运行监控与备份恢复。
- Embedding 与个人记忆适配；首版没有自动复习或提醒。

已部署明确确认的记录／图片 SSH 服务及数据库对象，未安装全局 hooks、注册开机任务、发布仓库或变更许可证。公网网关及其他真实宿主接入仍按实际验收结果更新本文件。
