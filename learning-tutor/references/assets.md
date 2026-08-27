# 教学图片：OSS 文件 + PostgreSQL 索引

## 已配置的图片存储

用户确认的 hx470 部署（2026-08-27）：

- OSS：`oss://wangye-main-bucket/learning-tutor/`，深圳 region，HTTPS endpoint `https://oss-cn-shenzhen.aliyuncs.com`。
- PostgreSQL：`personal_knowledge.learning.assets`；`learning.asset_tombstones` 保存已删除图片 ID，防止迟到上传复活。
- 服务端凭据：`/home/wayne/.config/learning-tutor/oss.json`、`/home/wayne/.config/learning-tutor/database.json`，目录 `0700`、文件 `0600`。
- 独立运行环境：`/home/wayne/.local/share/learning-tutor/asset-venv`；Python 3.12，依赖见 `scripts/server/requirements.txt`。
- 服务端入口：`/home/wayne/.local/share/learning-tutor/service/scripts/server/asset_service.py`；共享校验模块在上级 `asset_common.py`。
- 图片数据库账号 `learning_tutor_assets`：非超级用户，只额外授予教学图片两张表所需权限；不使用 PostgreSQL 管理员执行日常上传。

这是 **SSH 图片桥接**，不是公网 HTTPS 教学 API；未新开监听端口、修改 bucket 全局 ACL、安装全局 hooks 或改动个人记忆服务。新电脑需要已有的 hx470 SSH 访问路径；公网统一入口尚待部署。

## 对象与索引

对象 key 由服务端生成，不取用户文件名：

```text
learning-tutor/assets/<profile-hash>/<topic-uuid>/<asset-uuid>.png
```

图片二进制只放 OSS。数据库保存：

| 字段 | 内容 |
|---|---|
| `asset_id` | 稳定图片 ID，同一上传的重试复用 |
| `profile`, `topic_id`, `topic_key`, `session_id` | 学习者、领域／概念、会话关联 |
| `caption`, `alt_text` | 图片讲什么、关键关系与无图时的文字解释 |
| `provenance` | 工具、模型、生成提示、引用来源、概念标签等 JSON；不含密钥 |
| `bucket`, `oss_key` | 稳定存储地址；不保存本机路径或临时签名 URL |
| `mime_type`, `width`, `height`, `byte_size`, `sha256` | 格式、尺寸、完整性 |
| `etag`, `version_id`, `state`, timestamps | OSS 回执、上传／删除状态与时间 |

使用静态 PNG/JPEG/WebP，最多 25 MiB、3200 万像素；服务端检查实际解码格式与 SHA-256，拒绝 HTML、SVG、动画及伪装扩展名。上传不会重绘、压缩或删除原图元数据；含敏感 EXIF 的外部图片应先由用户决定是否处理。本功能默认面向新生成的教学图，不自动上传用户所有附件。

每个对象显式设置 `private`，不依赖 bucket 默认权限。服务端回读验证后才将数据库标为 `ready`。同 ID 不同内容报冲突；OSS 写入成功但数据库 ACK 丢失时，重试校验既有对象，不重复写入。当前 bucket 版本控制未启用；代码记录 version_id 并支持按版本删除，但版本控制场景尚未实测。未来若通过 HTTPS 返回临时访问链接，应短时签名，不永久公开图片。[OSS PutObject 官方说明](https://www.alibabacloud.com/help/en/oss/developer-reference/putobject)

## 每台电脑配置一次

安装完整 skill，Python 3.9+、OpenSSH 可用，先验证已有 SSH 登录。客户端 **不配置 OSS AccessKey 或数据库密码**。

```sh
SKILL_ROOT="/absolute/path/to/learning-tutor"
python3 "$SKILL_ROOT/scripts/assets.py" configure \
  --ssh wayne@hx470 \
  --python /home/wayne/.local/share/learning-tutor/asset-venv/bin/python \
  --service /home/wayne/.local/share/learning-tutor/service/scripts/server/asset_service.py
python3 "$SKILL_ROOT/scripts/assets.py" status
```

Windows PowerShell 用本机 Python 与绝对 skill 路径调用相同参数；SSH alias、密钥与 known_hosts 由该电脑的 OpenSSH 配置提供。Linux/macOS 同理。`--home`、`--profile` 在子命令前，必须与 `learn.py` 和 worker 一致；默认 profile 为 `personal`。配置存入私有本地 SQLite，仅含 SSH 主机与程序路径。

`configure` 只保存连接信息，不代表网络已验收。执行主题 `list` 成功，才说明该电脑的 SSH 图片服务可达。

## 生成图片后的工作流

1. 生成图片，检查科学关系、变量和标签；保留本机原始文件。
2. 显式上传，说明它解释什么；如有学习 session，传实际 UUID。

```sh
python3 "$SKILL_ROOT/scripts/assets.py" upload optics/vergence "/absolute/path/to/vergence.png" \
  --caption "辐辏角与目标距离：左右视线在目标处相交" \
  --alt-text "双眼间距 b，目标位于中轴线上距离 d 处，总辐辏角为 2 atan(b/(2d))"
```

可加 `--session SESSION_UUID`、`--provenance /absolute/path/to/provenance.json`，例如文件内容：

```json
{"tool":"imagegen","model":"reported-model-or-unknown","prompt":"生成双眼辐辏几何示意图","concepts":["vergence"],"sources":[]}
```

3. 输出 `queued` 只说明 SQLite 已提交图片 bytes 与描述。检查 `upload.results` 中**该 asset_id** 的 `state=ready`，才算 OSS 和数据库都确认；队列积压时，本次上传可能排在旧图片后面。
4. 将回执的 asset_id、oss_key、sha256 加入学习 checkpoint 的 `sources`，保持 caption／来源说明。不编造这些值。
5. 断网时提示检查 SSH／网络／服务。待上传图片以 BLOB 保存在本地 SQLite，即使原始临时图片消失仍可补传；`learn.py worker` 在已配置图片连接时每轮重试一个，或手动执行：

```sh
python3 "$SKILL_ROOT/scripts/assets.py" retry
```

只有匹配的 `ready` 回执到达才清除队列中的图片 BLOB；元数据收据保留。图片和文字是两条独立通路；文字记录后端已可按 [setup.md](setup.md)配置，但图片成功仍不代表文字／评估已同步。hook 目前只采集图片描述，并不保证每张生成图自动调用 upload；Agent 必须执行上述显式入队步骤。

## 查询、取图与删除

```sh
python3 "$SKILL_ROOT/scripts/assets.py" list optics/vergence
python3 "$SKILL_ROOT/scripts/assets.py" get ASSET_UUID
python3 "$SKILL_ROOT/scripts/assets.py" download ASSET_UUID --output "/absolute/path/to/restored.png"
python3 "$SKILL_ROOT/scripts/assets.py" delete ASSET_UUID --confirm-id ASSET_UUID
```

列表每页最多 100 张，`more=true` 时用返回的 `after` 加 `--after` 继续。下载走 SSH→服务端认证 OSS 读取，校验内容 hash 后创建本机文件，不覆盖现有文件，也不向客户端回传 AccessKey 或签名 URL。

删除先持久排队，成功才标记 `deleted`；服务端删除对象并清空 caption／alt_text／来源，保留最小 tombstone。失败用 `retry` 继续。生成原文件、用户显式下载的文件和数据库备份不被自动擦除。

**当前 `learn.py delete-topic` 尚未统一级联清理远端图片。** 删除整个主题时，先分页查询并逐张删除该主题图片，再删除教学记录；其他设备有待上传图片时也需先停止并处理相应队列。后续统一 HTTPS API 应加入主题级服务端 tombstone 与附件补偿删除，防止离线设备上传新的图片 ID。

## 凭据与运维

- AccessKey 只在服务端私有文件中；不放仓库、命令参数、截图、客户端或表内。服务端错误只返回经过限制的类型／固定说明，不回显 SDK／SQL 原始异常。
- 本次给定 AccessKey 曾出现在聊天中，建议换成仅允许 `learning-tutor/*` 对象操作的专用 RAM 凭据；测试新凭据成功后再撤销旧凭据。不要自动吊销可能仍供其他业务使用的 key。
- 所需对象操作：PutObject、GetObject、GetObjectAcl、DeleteObject；设置私有 ACL 可能还需 PutObjectAcl。首次定位 region 用 GetBucketLocation；若启用版本控制，还需相应版本读删权限。权限模板应由实际 RAM 策略验证，禁止为方便直接扩大到整个 bucket。
- 备份数据库与私有配置时加密；OSS 生命周期不要误删此 prefix。当前没有配置生命周期、跨区域备份或监控告警。
- 服务器部署文件是仓库代码的副本，仓库更新不会自动替换 hx470；更新时同步 `asset_common.py` 与 `server/asset_service.py` 并重跑合成图片验收。服务为每次 SSH 调用启动，无需重启常驻进程。
- 此阶段使用主题列表和图片说明；暂不生成 embedding，也不向 `personal_context` 写入图片或记忆。未来可按需建立 caption／概念的检索索引，保留原始 asset_id 为事实来源。
