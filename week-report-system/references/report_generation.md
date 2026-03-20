# Weekly Report Generation

This document describes how to generate comprehensive weekly work reports from conversation history.

## Report Structure (Total-Part-Total Pattern)

Keep the report **concise and work-focused**. No code line counts. Emphasize project progress, decisions made, and measurable outcomes. Each project section should be 3-6 bullet points at most.

```markdown
# 周工作汇报 - {YYYY}年第{WW}周
> 报告周期: {start_date} 至 {end_date}
> 生成时间: {generation_time}

## 📋 本周工作概览

[2-3 sentences: main projects, key outcomes, overall status. First "Total".]

---

## 📊 分项目工作详情

### {Project Name}

- [Concrete progress: what was completed, what changed, what decision was made]
- [Key outcome with data if available — e.g. "完成X模块开发，已通过集成测试"]
- [Blocker resolved or risk mitigated if any]

### {Project Name}

- [Same pattern — factual, outcome-oriented, no filler]

---

## 🎯 本周亮点

1. **[Achievement]**: [One sentence on impact or significance]
2. **[Achievement]**: [One sentence on impact or significance]
3. **[Achievement]**: [One sentence on impact or significance]

---

## 📝 总结与下周计划

**总结:** [1-2 sentences on overall progress and any outstanding items.]

**下周计划:**
- [ ] [Plan 1]
- [ ] [Plan 2]
- [ ] [Plan 3]

---

*本报告由AI自动生成并整理*
```

### Writing guidelines

- **Project sections**: factual bullet points about what actually happened — features shipped, bugs fixed, decisions finalized, integrations completed. Avoid vague phrases like "进行了开发" or "做了优化".
- **Data if available**: completion percentage, number of issues resolved, API response time improvement — anything concrete from the conversation logs.
- **No code metrics**: do not include lines of code written, number of commits, or files changed — these are not meaningful for a work report.
- **Length**: the whole report should fit comfortably on one screen. If there are many projects, summarize minor ones in a single line each.

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
from scripts.git_operations import create_git_manager

git = create_git_manager()
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

本周重点推进用户认证系统重构和数据报表性能优化。JWT认证已完整落地并通过安全审计，报表查询耗时降低约40%，整体进度符合预期。

---

## 📊 分项目工作详情

### 用户认证系统重构

- 完成JWT Token生成与验证，支持自动静默刷新，用户无感知续期
- 实现多设备登录管理与强制下线功能
- 安全审计发现并修复2个高危漏洞（RS256非对称加密 + Token黑名单机制）

### 数据报表优化

- 针对慢查询添加复合索引，查询耗时从平均8s降至4.8s（↓40%）
- 引入查询结果缓存，数据库压力显著下降
- 修复报表导出在大数据量下的超时问题

---

## 🎯 本周亮点

1. **JWT认证上线**: 无状态认证架构落地，为后续多区域扩展打好基础
2. **报表性能提升40%**: 用户侧加载体验明显改善，投诉工单清零
3. **安全漏洞闭环**: 2个高危问题在本周内发现并修复，未影响线上用户

---

## 📝 总结与下周计划

**总结:** 认证重构和性能优化两条线均达成阶段目标，核心功能通过验收。下周重点转向灰度发布和监控体系建设。

**下周计划:**
- [ ] 完成认证系统灰度发布（覆盖10%流量）
- [ ] 设计监控告警方案并完成接入
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
