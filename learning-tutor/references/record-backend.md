# hx470 记录后端

## 已部署结构

部署日期：2026-08-27。客户端通过已有 SSH 认证启动一次服务进程，stdin 输入 JSON，stdout 返回固定结构回执；服务端不额外监听端口。

```text
本机 SQLite outbox
    → OpenSSH → hx470 record_service.py
    → 127.0.0.1:5432 / personal_knowledge / learning
    → 事务提交回执 → 本机确认
```

- 服务入口：`/home/wayne/.local/share/learning-tutor/service/scripts/server/record_service.py`。
- 服务 Python：`/home/wayne/.local/share/learning-tutor/asset-venv/bin/python`；与图片服务共用现有独立 venv。
- 服务端配置：`/home/wayne/.config/learning-tutor/record-database.json`，文件 `0600`，目录 `0700`，含固定 profile、数据库连接参数和服务专用密码。
- 数据库：现有 `wayne-postgresql` 容器中的 PostgreSQL 17；只连接本机 loopback，不扩大数据库网络暴露范围。
- 日常账号：`learning_tutor_records`，非超级用户，无建库／建角色／复制权限；对记录表授予所需权限，不额外授予图片表和 personal_context 表权限。
- 传输：现有 `wayne@hx470` SSH 登录。此方式继承该 SSH 账户权限，并非只允许教学操作的专用 SSH 账户；后续可配置专用账户／受限命令或 HTTPS 网关。

新电脑仅按 [setup.md](setup.md)配置 SSH 主机和程序路径，无需 OSS／PostgreSQL 密码。不复制旧设备的 SQLite、device ID 和游标。

## PostgreSQL 中在哪里查

| 对象 | 含义 |
|---|---|
| `learning.profiles` | 学习者、服务数据集身份、已提交 cursor |
| `learning.topics` | 主题 key 和标题 |
| `learning.events` | 对话／评分／进度等不可变事件，canonical envelope 为原文 |
| `learning.receipts` | 已接收事件 ID、hash、设备序号；重试去重 |
| `learning.tombstones` | 已删除主题，阻止迟到记录复活 |
| `learning.messages` | 原始用户／助手消息查询视图 |
| `learning.assessments` | 理解程度、证据 ID、提示次数等评估视图 |
| `learning.checkpoints` | 所有续学 checkpoint，保留历史 |
| `learning.checkpoint_heads` | 每个主题尚未被后续 checkpoint 合并的分支 |
| `learning.assets` | 独立图片服务管理的图片含义、oss_key、hash 等 |

使用已有数据库管理入口执行只读 SQL，例如：

```sql
SELECT kind, count(*) FROM learning.events
WHERE profile = 'personal' GROUP BY kind ORDER BY kind;

SELECT t.key, h.at, h.next
FROM learning.checkpoint_heads h
JOIN learning.topics t USING (profile, topic)
WHERE h.profile = 'personal' ORDER BY h.at DESC;

SELECT concept, dimension, level, evidence, reason
FROM learning.assessments
WHERE profile = 'personal' ORDER BY at;
```

事件 `envelope` 的 hash 是同步依据；SQL `data` JSONB 是便捷投影。NUL 在投影中显示为 `\u0000`，以 `projection_escaped` 标记，避免 PostgreSQL 的 NUL 限制影响原文恢复。读取原文、导出和核验时使用 envelope。

## 后端重新部署／更新

本节是管理员维护步骤，不会由安装 skill 自动执行：

1. 保留原目录结构，复制 `scripts/ledger.py`、`scripts/record_refs.py`、`scripts/server/record_service.py` 和 `scripts/server/records.sql`。服务端只需 Psycopg；依赖版本见 `scripts/server/requirements.txt`。
2. 在目标数据库中以管理员事务执行 `records.sql`。首次部署生成独立记录账号密码，直接写入服务器私有配置，不放客户端、Git、命令行或日志。
3. 为固定 profile 创建一行 `learning.profiles`，server_id 为新 UUID。正常更新保留已有 server_id/cursor，不重建数据集身份。
4. 对运行角色授予以下最小业务表权限；不要使用管理员执行日常同步：

```sql
GRANT CONNECT ON DATABASE personal_knowledge TO learning_tutor_records;
GRANT USAGE ON SCHEMA learning TO learning_tutor_records;
GRANT SELECT, UPDATE ON learning.profiles TO learning_tutor_records;
GRANT SELECT, INSERT, DELETE ON learning.events, learning.topics TO learning_tutor_records;
GRANT SELECT, INSERT ON learning.receipts, learning.tombstones TO learning_tutor_records;
GRANT SELECT ON learning.messages, learning.assessments,
  learning.checkpoints, learning.checkpoint_heads TO learning_tutor_records;
```

5. 私有 JSON 配置字段：`host`、`port`、`dbname`、`user`、`password`、`profile`。服务拒绝软链接配置或组／其他用户可读的配置文件；私有配置 root 应由同一服务账户持有。
6. 通过 `configure-ssh`、`sync` 验证；先使用独立测试 profile，再接真实学习状态。部署文件是仓库的副本，更新仓库不会自动更新 hx470。

`records.sql` 是首版建表／视图定义，不是通用版本迁移器；已有结构变更须先备份并明确迁移。服务每次调用重新启动，无常驻进程要重启。

## 测试、故障和恢复

真实 PostgreSQL 测试位于 `tests/test_postgres_records.py`。默认跳过；管理员先准备以 `learning-tutor-test-` 开头的隔离 profile 和私有配置目录，再在同布局目录中运行：

```sh
LEARNING_RECORD_TEST_CONFIG=/absolute/path/to/private-test-config \
  /absolute/path/to/venv/bin/python -m unittest discover \
  -s /absolute/path/to/learning-tutor/tests -p test_postgres_records.py -v
```

测试不会清理凭据或 profile；管理员测试后只清理该测试 profile 的 events、topics、receipts、tombstones、profiles 和私有测试目录，不操作个人数据。

- SSH／数据库断联：本机已落盘数据继续保留为 pending，检查网络、主机密钥、登录、容器和服务配置后重试 `sync`。仅配置成功不代表上传成功。
- 服务身份改变：客户端停止同步，不静默重置游标；需明确迁移或创建全新本地状态拉取。
- 原始学习记录长期保留，直到主动删除；本机同步成功的非活跃主题缓存可按 30 天策略清理并恢复。
- 数据库恢复旧备份：停同步、核对事件和 receipts、分配新 server_id，再制定客户端迁移方案；不要沿用旧高水位假装没有回滚。备份恢复演练和自动备份／告警尚未配置。
- 主题删除目前只保证记录原文删除和防复活。OSS 图片仍按 [assets.md](assets.md)先逐张删除；跨图片的统一补偿队列尚未实现。本机显式备份／导出／下载及服务器备份不会自动擦除。
- 不将聊天正文写入服务日志；错误只返回固定代码，不回显 SQL、密码或数据库原始异常。

尚未部署公网 HTTPS 网关、每设备 HTTP 令牌、个人记忆写入、embedding 或自动复习。
