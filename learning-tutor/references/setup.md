# 安装、配置和宿主适配

## 当前交付边界

本包实现本地 SQLite 账本、查询／续学、同步客户端、显式 transcript 采集、Codex/Claude hook 配置安装器，以及 OpenClaw 插件桥接。用户确认后已在 hx470 部署 PostgreSQL [记录后端](record-backend.md)和独立的 [OSS 图片服务](assets.md)，均通过 SSH 调用，不新增公网端口。`tests/fixture_api.py` 只是回环模拟服务；正式记录入口是 `scripts/server/record_service.py`。公网 HTTPS 网关与个人记忆集成仍未部署。

三套 transcript parser 已通过合成数据测试；本机 Codex 的一次显式绑定学习试用已核对记录，其他真实 UI 的逐条覆盖、各宿主异常退出、Windows/Linux 客户端实机尚待验收。旧版 OpenClaw JSONL 与新版 SQLite 历史存储分开适配；当前 parser 仅处理 JSONL，遇到未知格式报错，不声称通用兼容。

## 一次性准备

Python 3.9+。核心脚本不需要 pip 安装；OpenClaw 插件另使用宿主已有 Node.js。将完整 `learning-tutor` 文件夹安装到各宿主的 skill 目录，保留 `scripts` 和 `references`。脚本路径取安装后的绝对路径。

这是一个 skill；`/learn-start`、`/learn-stop` 是采集控制标记，不是额外的 skill。新电脑可让 AI“按 learning-tutor 安装指南配置本机，先预览 hooks，再确认应用”，但仅输入 `/learning-tutor` 或复制 SKILL.md 不会自动安装 hooks。记录和图片客户端另需现有 OpenSSH 连接；OSS／数据库依赖只安装在服务端。

下文 POSIX 示例先设本机路径，Windows PowerShell 用 `$SkillRoot` 和 `python` 调用同一脚本：

```sh
SKILL_ROOT="/absolute/path/to/learning-tutor"
python3 "$SKILL_ROOT/scripts/learn.py" init
python3 "$SKILL_ROOT/scripts/learn.py" doctor
```

默认数据目录：macOS 用户 Library/Application Support、Windows LOCALAPPDATA、Linux XDG_STATE_HOME（缺省为用户 .local/state）下的 `learning-tutor`。可通过 `LEARNING_TUTOR_HOME` 或全局参数 `--home` 指定独立目录。不同机器使用相同 `--profile personal`，每台机器保留独立 device ID；复制 skill 不复制运行数据库。勿把运行目录放入 Git 或共享同步盘。

数据 SQLite 采用 WAL、FULL synchronous；事务提交才算本地保存。默认无应用层加密：使用个人设备账户、文件权限和磁盘加密。复制运行目录会连同凭据、游标和 device ID 一起复制，不适合当作新设备安装方式。

## Codex 与 Claude Code

安装器只预览，`--apply` 才写入用户指定的文件；保留其他 hooks，写前创建独立备份。首次安装先检查预览，不覆盖整个配置文件。

```sh
# Codex：使用其实际读取的 hooks.json 路径
python3 "$SKILL_ROOT/scripts/learn.py" install-hooks --host codex --config "/absolute/path/to/.codex/hooks.json"
# 确认后，将同一命令加 --apply

# Claude Code：使用其实际读取的 settings.json 路径
python3 "$SKILL_ROOT/scripts/learn.py" install-hooks --host claude --config "/absolute/path/to/.claude/settings.json"
```

原配置先备份再原子替换；卸载时删除新增的 learning-tutor command entries，保留后来新增的其他配置。备份适合在确认没有后续编辑时回滚。Skill 文件移动后，应重建配置并移除旧路径项。

重载宿主后，用户发送：

```text
/learn-start optics/vergence 辐辏角与目标距离
```

hook 根据宿主提供的 `session_id` 与 `transcript_path` 绑定；开始边界之前的历史不导入。首次命令可能被宿主当作普通文本而不是原生 slash command，实际分发必须验收。脚本自行识别该精确标记，不依赖模型记得调用工具。

hook 覆盖 SessionStart、UserPromptSubmit、PostToolUse、Stop、SessionEnd。记录来源只采用主 transcript，避免同时收 prompt、Stop 文本造成重复；完整性仍取决于该宿主是否把消息写进已绑定 transcript。`codex exec --json` 通常只输出助手事件，不包含完整用户输入，因此不是双向完整采集的替代品。

在独立终端启动持续采集与补传：

```sh
python3 "$SKILL_ROOT/scripts/learn.py" worker
```

status 输出 worker PID 与最近心跳，30 秒内的新鲜心跳只表示最近有活动，不保证进程此刻存活；长时间同步或扫描期间也可能显示过期。worker 为前台进程，Ctrl-C 停止；本版不注册操作系统自启动服务。hooks 提供阶段性落盘，worker 负责消息尾部及时采集和故障补传。SessionEnd 不执行网络请求，保留会话绑定以补齐最后一段输出。显式 `/learn-stop` 才关闭学习录制；终止 worker 并不撤销活动绑定。

用户说“这段不记录”时，先执行 stop，再进行不记录的交流。重新开始同一宿主会话会创建新的学习 session，从新边界开始。即使 transcript 已损坏，stop 仍停止录制并保留缺口说明。

可不用 hooks，显式绑定已有宿主会话：

```sh
python3 "$SKILL_ROOT/scripts/learn.py" start optics/vergence "辐辏角" --host codex --host-session SESSION_ID --transcript "/absolute/path/to/transcript.jsonl"
python3 "$SKILL_ROOT/scripts/learn.py" capture --host codex --host-session SESSION_ID
python3 "$SKILL_ROOT/scripts/learn.py" stop --host codex --host-session SESSION_ID
```

必须确认 transcript 确实属于指定会话；程序不扫描整个用户历史目录寻找聊天。绑定错误会采集所选文件的新内容。转录文件改写／轮转／截断后暂停导入，先检查缺口，再显式关闭旧绑定并重新绑定；不默默从头导入。

## OpenClaw

插件目录为本 skill 的 `scripts/openclaw`，入口 `index.mjs`，manifest 为 `openclaw.plugin.json`。在 OpenClaw 配置的 `plugins.load.paths` 中注册入口文件的绝对路径，并在 `plugins.entries.learning-tutor` 中启用、设置 `python`（解释器绝对路径）、`home`（私有状态目录）、可选 `profile`。本轮未替用户修改 Gateway 配置。插件在完整 skill 内就地加载；单独复制 openclaw 子目录会缺少上一级 Python 脚本。Gateway 的授权发送者范围应仅包含你的账户。

配置合并示例（保留原有 plugins 字段；不要整段覆盖已有配置）：

```json
{
  "plugins": {
    "load": {"paths": ["/absolute/path/to/learning-tutor/scripts/openclaw/index.mjs"]},
    "entries": {
      "learning-tutor": {
        "enabled": true,
        "config": {"python": "/absolute/path/to/python3", "home": "/absolute/path/to/private-learning-state", "profile": "personal"}
      }
    }
  }
}
```

如果配置了 plugins allowlist，还需显式加入 learning-tutor；随后重载 Gateway 并检查 worker 心跳。不要改动其他插件的启停或访问范围。

插件使用实查版本 2026.2.26 的 `registerCommand` 与 `registerService`；service 管理上述 worker 子进程，不依赖异步 `agent_end` 充当持久队列。命令要求宿主已授权的发送者。

```text
/learn {"action":"start","session":"SESSION_ID","key":"optics/vergence","title":"辐辏角","transcript":"/absolute/path/to/session.jsonl"}
/learn {"action":"status"}
/learn {"action":"stop","session":"SESSION_ID"}
```

会话 ID 与 transcript 路径取实际 Gateway 元数据，显式提供；避免把 channel/account/conversation 当作同一个 session。新版采用 SQLite 历史时需要新的读取适配器，当前 JSONL 组件不自动读取数据库文件。用户使用 `/new`、reset 或换 channel 后需重新绑定。

## 配置服务器

本地不配置服务器也可保存、查询本机内容；其他电脑暂时看不到未上传记录。

### 当前 hx470：每台电脑配置 SSH 连接

无需在新电脑配置 OSS／PostgreSQL 密码，也不用重新部署数据库。先配置该电脑的 OpenSSH 登录和 known_hosts；连接使用非交互认证并严格检查主机密钥。`hx470` 是 SSH 主机名／alias，不保证在每个网络直接可达；需要已有内网连接、VPN 或自己的跳板配置。

```sh
python3 "$SKILL_ROOT/scripts/learn.py" configure-ssh \
  --ssh wayne@hx470 \
  --python /home/wayne/.local/share/learning-tutor/asset-venv/bin/python \
  --service /home/wayne/.local/share/learning-tutor/service/scripts/server/record_service.py
python3 "$SKILL_ROOT/scripts/learn.py" sync
python3 "$SKILL_ROOT/scripts/learn.py" search 辐辏
python3 "$SKILL_ROOT/scripts/learn.py" resume optics/vergence
```

文字配置保存在本机私有 `config.json`，仅含 SSH 主机和服务端程序路径。图片连接按 [assets.md](assets.md)单独配置，使用同一 SSH 登录。`configure-ssh` 只保存配置；`sync` 的服务端回执才确认记录已入库。

新电脑仍需单独配置采集 hooks／worker，连接后端不自动开启录制。查询／续学前先 `sync`；本版 `search`／`resume` 命令自身只读本地缓存。录制保持停止时也能补传已有记录；`sync` 不扫描新的聊天。

### 可选 HTTPS 接口（网关尚待部署）

后续链路：客户端 HTTPS → 公网入口 → 内网学习服务 → PostgreSQL。数据库端口保持内网；现有 Context URL 或任意 URL 不等于学习接口。

```sh
# 环境变量由用户的终端／凭据管理工具提供；不要把真实令牌写进示例。
export LEARNING_TUTOR_TOKEN="TOKEN"
python3 "$SKILL_ROOT/scripts/learn.py" configure --url "https://HOST/learning"
python3 "$SKILL_ROOT/scripts/learn.py" sync
```

Windows PowerShell 对应 `$env:LEARNING_TUTOR_TOKEN = "TOKEN"`。配置文件仅保存 URL 和环境变量名，不保存令牌值。worker、hooks 与宿主需使用同一 home/profile；插件启动的 worker 也需继承令牌环境变量。

API 必须实现 [protocol.md](protocol.md)，不是任意 URL。同步校验 profile、server_id、回执 hash；跨域重定向被拒绝。换服务器／换学习身份使用独立状态目录或经过设计的数据迁移，不复用旧游标。

错误区分：未配置、本地存储失败、认证失败、连接失败、协议不符、采集格式变化。服务断联时本地记录继续积压；worker 有界退避，用户检查服务后也可手动 `sync`。本版没有桌面通知；诊断输出在宿主 hook／worker 终端，AI 应读取 status 向用户解释。

## 官方接口依据（核查日期 2026-08-27）

- [Codex hooks](https://learn.chatgpt.com/docs/hooks)：transcript 格式非稳定接口；Stop 不是所有可见消息的逐条拦截点。
- [Claude hooks](https://code.claude.com/docs/en/hooks)：用户打断不保证触发 Stop，需独立的尾部采集与重启补账。
- [OpenClaw plugin hooks](https://docs.openclaw.ai/plugins/hooks)、[session storage](https://docs.openclaw.ai/reference/session-management-compaction)：runtime 与版本影响事件和存储接口。

本地曾只读检查 Codex CLI 0.149.1、桌面 bundled binary 0.150.0-alpha.8、Claude Code 2.1.233、OpenClaw 2026.2.26；这不是插件已经在这些宿主实跑成功的声明。
