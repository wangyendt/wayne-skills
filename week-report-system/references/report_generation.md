# Weekly Report Generation

This document describes how to generate comprehensive weekly work reports from conversation history.

## Report Structure (Total-Part-Total Pattern)

```markdown
# 周工作汇报 - {YYYY}年第{WW}周
> 报告周期: {start_date} 至 {end_date}
> 生成时间: {generation_time}

## 📋 本周工作概览

[3-5 sentences summarizing the week's main themes, achievements, and focus areas. This is the first "Total" section.]

---

## 📊 分项目工作详情

### 项目一: {Project Name}

**工作概述:**
[Brief description of work done in this project]

**关键成果:**
- [Outcome 1 with metrics if available]
- [Outcome 2 with metrics if available]
- [Outcome 3 with metrics if available]

**数据指标:**
- 对话次数: X次
- 主要任务: [task types]
- 耗时估算: ~X小时

**技术亮点:**
- [Technical achievement 1]
- [Technical achievement 2]

---

### 项目二: {Project Name}
[Same structure as above]

---

## 📈 本周数据统计

| 指标 | 数值 |
|------|------|
| 总对话次数 | X |
| 涉及项目数 | X |
| 代码生成次数 | X |
| 文档编写次数 | X |
| 问题解决数 | X |

---

## 🎯 重点工作与贡献

### ⭐ 核心成就

1. **[Achievement 1]**: [Description with impact]
2. **[Achievement 2]**: [Description with impact]
3. **[Achievement 3]**: [Description with impact]

### 💡 创新点

- [Innovation 1]
- [Innovation 2]

### 🔧 解决的关键问题

| 问题描述 | 解决方案 | 影响范围 |
|----------|----------|----------|
| [Problem 1] | [Solution 1] | [Scope] |
| [Problem 2] | [Solution 2] | [Scope] |

---

## 📝 本周总结与下周计划

### 总结
[2-3 sentences summarizing the week's overall contribution and progress. This is the second "Total" section.]

### 下周计划
- [ ] [Plan 1]
- [ ] [Plan 2]
- [ ] [Plan 3]

---

*本报告由AI自动生成并整理*
```

## Report Generation Process

### Step 1: Parse Command

```python
import re
from datetime import datetime, timedelta

def parse_report_request(message: str) -> dict:
    """
    Parse user request to determine year and week.

    Examples:
    - "总结2024年第12周的工作" -> {year: 2024, week: 12}
    - "本周工作总结" -> {year: current, week: current}
    - "写周报" -> {year: current, week: current}
    - "上周周报" -> {year: current, week: last_week}
    """

    # Pattern 1: "xxxx年第xx周"
    match = re.search(r'(\d{4})年.*?第(\d+)周', message)
    if match:
        return {'year': int(match.group(1)), 'week': int(match.group(2))}

    # Pattern 2: "本周" / "写周报" / "生成周报"
    if any(kw in message for kw in ['本周', '周报', '工作总结']):
        now = datetime.now()
        return {'year': now.year, 'week': now.isocalendar()[1]}

    # Pattern 3: "上周"
    if '上周' in message:
        last_week = datetime.now() - timedelta(days=7)
        return {'year': last_week.year, 'week': last_week.isocalendar()[1]}

    # Default: current week
    now = datetime.now()
    return {'year': now.year, 'week': now.isocalendar()[1]}
```

### Step 2: Pull Latest Data

```python
from scripts.git_operations import GitManager

git = GitManager.from_env()
git.pull()
```

### Step 3: Read Conversation Files

```python
def read_week_conversations(git: GitManager, year: int, week: int) -> list:
    """Read all conversation files for specified week."""

    week_path = f"{year}/week{week:02d}"
    conversations = []

    # List all .txt files in week directory
    for file_path in git.list_files(week_path, pattern="*.txt"):
        content = git.read_file(file_path)
        conversations.append({
            'file': file_path,
            'content': content,
            'timestamp': extract_timestamp(content)
        })

    # Sort by timestamp
    conversations.sort(key=lambda x: x['timestamp'])

    return conversations
```

### Step 4: Analyze and Categorize

```python
def analyze_conversations(conversations: list) -> dict:
    """
    Use AI to analyze conversations and extract:
    1. Project categories
    2. Key achievements
    3. Metrics and data points
    4. Technical highlights
    """

    # Combine all conversation content
    combined_text = "\n\n".join([c['content'] for c in conversations])

    # AI analysis prompt
    analysis_prompt = f"""
    Analyze the following work conversations from this week and extract:

    1. **Projects**: Identify distinct projects/areas of work
    2. **Key Achievements**: What was accomplished? Include metrics if available
    3. **Technical Highlights**: Notable technical solutions or innovations
    4. **Problems Solved**: What issues were resolved?
    5. **Work Categories**: Code, docs, debugging, planning, etc.

    Conversations:
    {combined_text}

    Output in JSON format:
    {{
        "projects": [
            {{
                "name": "Project name",
                "summary": "Brief description",
                "achievements": ["achievement 1", "achievement 2"],
                "metrics": {{"key": "value"}},
                "technical_highlights": ["highlight 1"]
            }}
        ],
        "overall_stats": {{
            "total_conversations": 0,
            "categories": {{"code": 0, "docs": 0, "debug": 0}},
            "key_achievements": ["achievement 1", "achievement 2", "achievement 3"]
        }}
    }}
    """

    # Call AI for analysis
    analysis = call_ai(analysis_prompt)

    return analysis
```

### Step 5: Generate Report

```python
def generate_report(analysis: dict, year: int, week: int) -> str:
    """Generate the final report in markdown format."""

    # Calculate date range for the week
    week_start = datetime.fromisocalendar(year, week, 1)
    week_end = week_start + timedelta(days=6)

    # Build report sections
    report = []

    # Header
    report.append(f"# 周工作汇报 - {year}年第{week}周")
    report.append(f"> 报告周期: {week_start.strftime('%Y-%m-%d')} 至 {week_end.strftime('%Y-%m-%d')}")
    report.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    # Overview (First Total)
    report.append("## 📋 本周工作概览")
    report.append(generate_overview(analysis))
    report.append("")
    report.append("---")
    report.append("")

    # Projects (Part)
    report.append("## 📊 分项目工作详情")
    for project in analysis['projects']:
        report.append(generate_project_section(project))
    report.append("")

    # Statistics
    report.append("## 📈 本周数据统计")
    report.append(generate_stats_table(analysis['overall_stats']))
    report.append("")

    # Key Contributions (Highlight)
    report.append("## 🎯 重点工作与贡献")
    report.append(generate_key_contributions(analysis))
    report.append("")

    # Summary (Second Total)
    report.append("## 📝 本周总结与下周计划")
    report.append("### 总结")
    report.append(generate_summary(analysis))
    report.append("")
    report.append("### 下周计划")
    report.append(generate_next_week_plan(analysis))
    report.append("")

    # Footer
    report.append("---")
    report.append("*本报告由AI自动生成并整理*")

    return "\n".join(report)
```

### 4. Clear Structure

- Use consistent formatting
- Include tables for data presentation
- Add visual markers (emojis) for quick scanning
- Keep summaries concise and impactful

## Example Output

[...示例内容保持不变...]

## Saving Reports

Optionally save generated reports to Git:

```python
def save_report(git: GitManager, report: str, year: int, week: int):
    """Save report to Git repository."""
    reports_path = f"{year}/week{week:02d}/report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    git.write_file(reports_path, report)
    git.commit_and_push(f"Add weekly report for {year}-W{week:02d}")

- **Project/Module names** mentioned in conversations
- **Code repositories** referenced
- **Task types**: development, debugging, documentation, planning
- **Domain areas**: frontend, backend, data, DevOps, etc.

### 2. Data-Driven Metrics

Extract and present:

- **Quantitative data**: lines of code, files modified, features completed
- **Conversation counts**: per project, per category
- **Time estimates**: based on conversation complexity
- **Problem resolution**: issues identified and solved

### 3. Highlight Contributions

Emphasize:

- **Core achievements**: Top 3 most impactful accomplishments
- **Innovations**: New approaches, optimizations, creative solutions
- **Problem-solving**: Critical issues resolved with impact assessment

### 4. Clear Structure

- Use consistent formatting
- Include tables for data presentation
- Add visual markers (emojis) for quick scanning
- Keep summaries concise and impactful

## Example Output

```markdown
# 周工作汇报 - 2024年第51周
> 报告周期: 2024-12-16 至 2024-12-22
> 生成时间: 2024-12-22 18:30:00

## 📋 本周工作概览

本周主要集中在用户认证系统重构和数据报表优化两个重点项目。完成了JWT认证的完整实现，
优化了报表查询性能约40%,并修复了3个生产环境关键Bug。代码提交量较上周增长15%,
整体项目进度符合预期。

---

## 📊 分项目工作详情

### 项目一: 用户认证系统重构

**工作概述:**
将原有的Session认证升级为JWT无状态认证，提升系统可扩展性和安全性。

**关键成果:**
- 完成JWT Token生成和验证逻辑，支持自动刷新机制
- 实现多设备登录管理和强制下线功能
- 通过安全审计，修复2个潜在安全漏洞

**数据指标:**
- 对话次数: 8次
- 主要任务: 开发(60%), 调试(30%), 文档(10%)
- 耗时估算: ~12小时

**技术亮点:**
- 使用RS256非对称加密，提升Token安全性
- 实现Token黑名单机制，支持紧急撤销

---

## 📈 本周数据统计

| 指标 | 数值 |
|------|------|
| 总对话次数 | 23 |
| 涉及项目数 | 3 |
| 代码生成次数 | 45 |
| 问题解决数 | 5 |

---

## 🎯 重点工作与贡献

### ⭐ 核心成就

1. **JWT认证上线**: 完成认证系统升级，支撑未来百万级用户扩展
2. **报表性能优化**: 查询速度提升40%，用户体验显著改善
3. **安全漏洞修复**: 及时发现并修复2个高危漏洞，避免潜在风险

### 💡 创新点

- 设计并实现了Token自动刷新的无感知机制
- 引入查询缓存策略，大幅降低数据库压力

### 🔧 解决的关键问题

| 问题描述 | 解决方案 | 影响范围 |
|----------|----------|----------|
| Token过期后需要重新登录 | 实现静默刷新机制 | 全平台用户 |
| 报表查询超时 | 添加索引+缓存优化 | 数据分析模块 |

---

## 📝 本周总结与下周计划

### 总结
本周在认证系统和性能优化方面取得实质性进展，核心功能已通过测试验收。代码质量保持较高水平，
团队协作顺畅。建议下周重点关注监控告警体系的完善。

### 下周计划
- [ ] 完成认证系统灰度发布
- [ ] 设计监控告警方案
- [ ] 编写系统迁移文档

---

*本报告由AI自动生成并整理*
```

## Saving Reports

Optionally save generated reports to Git:

```python
def save_report(git: GitManager, report: str, year: int, week: int):
    """Save report to Git repository."""

    reports_path = f"{year}/week{week:02d}/report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    git.write_file(reports_path, report)
    git.commit_and_push(f"Add weekly report for {year}-W{week:02d}")
```
