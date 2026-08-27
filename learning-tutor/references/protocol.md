# 学习记录协议 v1：PostgreSQL 后端与传输

状态：PostgreSQL 记录后端已在 hx470 部署，使用现有 SSH 执行 JSON RPC，客户端支持同步／回执／查询恢复。公网 HTTPS 网关未部署；下列路径是 RPC 中的逻辑路径，不是已开放的网站。部署与数据库结构见 [record-backend.md](record-backend.md)，图片通路见 [assets.md](assets.md)。本协议独立于 personal_context API。

## 部署边界

单学习者；当前以 SSH 登录认证，服务端私有配置固定 profile 并检查请求身份，不由客户端任意指定学习者。未部署每设备 HTTP 令牌；现有 SSH 登录也不是受限 HTTP 身份层。未来网关需独立令牌、撤销、限流和日志脱敏。PostgreSQL 建单个 `learning` schema，通过 topic／concept／session ID 组织，不建嵌套 schema。

技能与采集组件不持有数据库账号，不直写个人记忆内部表。教学事件和图片分别使用 SSH 服务端命令，未来可接入统一 HTTPS 身份层。Embedding、memory 摘要是后续可重建派生层；当前不接入。

## 端点

- `GET /v1/identity` → `{v:1, profile, server_id}`。server_id 为服务数据集的稳定标识；数据库回滚重建需变更它，防止客户端沿用失效游标。
- `POST /v1/events`，body `{v:1, profile, events:[...]}`，每批最多 100 事件且序列化请求体不超过 4 MiB；单事件上限 1 MiB。
- `GET /v1/events?after=CURSOR&limit=100&max_bytes=4194304` → `{profile,server_id,events,cursor,more}`。
- `GET /v1/topics/TOPIC_ID/events?after=CURSOR&limit=100&max_bytes=4194304` → 同样结构，仅用于该主题缓存恢复，其 cursor 不覆盖全局同步 cursor。

GET 分页同时遵守条数与字节上限，超过预算的下一条留给下一页；避免合法大消息形成永远超限的批次。

v1 的 hash 为 `scripts/ledger.py` 中 canonical(event) 的 UTF-8 SHA-256：JSON 键排序、无空白分隔、保留非 ASCII、拒绝 NaN/Infinity。当前 Python 客户端与已部署服务端使用相同规范化规则，跨语言实现需通过浮点数／Unicode 测试向量后再接入。

POST 成功仅在整批事务提交后返回：

```json
{
  "profile": "personal",
  "server_id": "DATASET_ID",
  "receipts": [
    {"id": "EVENT_ID", "hash": "CANONICAL_EVENT_SHA256", "status": "accepted"}
  ]
}
```

重试返回 `duplicate`，被删除主题的迟到事件返回 `deleted`。客户端遇 deleted 重新拉取持久 tombstone 后处理，不仅凭回执删除任意本地记录。回执覆盖整批每个 ID，hash 必须匹配。内容相同但 ID 不同的事件是两次发生，不进行文本去重。同 ID 不同内容返回冲突。

全局 cursor 为服务端提交序号，不是设备时间戳。分页可以包含已删除内容留下的序号空洞；`more=true` 时游标必须推进。断联重连先拉取（应用删除）再上传。客户端有页数／批数／响应大小限制，积压超出单次上限时下次继续。

## 必须满足的不变量

1. 原文事件与去重 receipt 在同一事务中持久化，网络 ACK 丢失后重试不重复写入。
2. 身份、数据格式、大小、kind 验证先于写入。评估引用真实用户消息；被引用证据属于同一主题的一次来源 session。仅助手自述不算用户掌握证据。
3. checkpoint parent 和 assessment supersedes 必须指向已存在的同主题对应事件，不创建环；两台设备的证据都保留。
4. 删除标记持久保存，清除主题原文和历史变更流中的原文副本；迟到事件不复活主题。备份保留／删除 SLA 在部署时明确，不把逻辑 tombstone 宣称为所有物理副本已擦除。
5. 按 profile 隔离 GET/POST、快照、删除，日志不保存 Authorization、问题或回答原文。
6. GET 只能返回已提交事件；回执前进行所需持久化。服务端恢复备份后改变数据集身份，避免沿用旧高水位。
7. SQLite 本地采用原文事件和 cursor 同事务提交；同步消息和评分不是同一种事件，漏评保持未评估。

## 当前实现与后续验收

`scripts/server/records.sql` 定义事件表和可查询视图；`record_service.py` 与本地账本共用 `record_refs.py` 验证引用。每次写入锁定 profile 行，整批分配 cursor，提交后返回回执；并发写入不会把未提交 cursor 暴露给读取者。GET 使用只读可重复读事务，使事件页和高水位来自同一快照。事务机制参见 [PostgreSQL row-level locks](https://www.postgresql.org/docs/17/explicit-locking.html#LOCKING-ROWS) 与 [Psycopg transactions](https://www.psycopg.org/psycopg3/docs/basic/transactions.html)。

服务端 `envelope` 保留原始规范化 JSON，`data` JSONB 只是 SQL 查询投影；包含 NUL 时投影视为可见 `\u0000` 并标记 `projection_escaped`，恢复和 hash 均使用 envelope，不将有损投影当原文。

真实 PostgreSQL 已验证提交、重试、回执丢失、回滚、删除、并发、字节分页、双独立客户端恢复；测试边界见 [validation.md](validation.md)。后续仍需 HTTPS 路径／反代、每设备令牌发放撤销、备份恢复、磁盘告警／限流，以及主题与图片删除的补偿队列。

`tests/fixture_api.py` 只绑定 127.0.0.1，使用固定测试令牌和 SQLite 模拟事务，缺少生产身份管理与运维能力，勿作为公网服务启动。
