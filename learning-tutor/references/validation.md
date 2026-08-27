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
