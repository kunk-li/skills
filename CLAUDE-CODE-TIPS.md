# 用 Claude Code 把项目维护好:一些实战方法(持续更新)

这是一份活文档。我们用 Claude Code 长期维护这套 skill 库,攒了一批让 Claude Code 更好用、更少掉链子的方法和小工具。发现新的好用法,就往这里补、再推上来。

每条都是「解决什么问题 + 怎么做 + 可直接抄的最小示例」。

---

## 1. 用 SessionStart hook 自动注入项目上下文(开工不用重新解释)

**问题**:每开一个新会话,Claude 不记得上次干到哪、项目背景是什么,你得一遍遍重讲。

**做法**:配一个 `SessionStart` hook,会话一启动就自动读项目的几个上下文文件(项目说明 / 当前状态 / 最近一次总结)注入进去。这样每个会话开局就有全量上下文。

**怎么做**:在 `.claude/settings.json` 里注册 hook,指向一个小脚本;脚本读文件、拼成一段文本,以 JSON 输出。

```json
// .claude/settings.json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          { "type": "command",
            "command": "python",
            "args": [".claude/load_context.py"],
            "timeout": 10 }
        ]
      }
    ]
  }
}
```

```python
# .claude/load_context.py —— 最小示例
import json, pathlib
ROOT = pathlib.Path(__file__).parent.parent
files = ["CLAUDE.md", "STATUS.md"]           # 按需增减:项目说明、当前状态…
parts = []
for f in files:
    p = ROOT / f
    if p.exists():
        parts.append(f"# {f}\n\n{p.read_text(encoding='utf-8')}")
context = "\n\n---\n\n".join(parts)
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": context
    }
}))
```

**效果**:每次开局 Claude 自动知道「这是什么项目、现在到哪了」,你直接说「继续」就行。

---

## 2. 用 Stop hook 做「收尾自动检验」(防止忘记留档)

**问题**:干完一波活,人和 AI 都容易忘记更新「现状文档」、忘记写总结。下次开会话就断片。

**做法**:配一个 `Stop` hook,在 Claude 每轮回复结束时**自动检验**该留的档留了没——比如「现状文档今天更新过吗」「这次会话的总结写了吗」——没做就打印一句提醒。相当于给收尾动作加了个自动巡检。

**怎么做**:

```json
// .claude/settings.json 里加一段
"Stop": [
  { "matcher": "*",
    "hooks": [
      { "type": "command", "command": "python",
        "args": [".claude/stop_check.py"], "timeout": 5, "async": true }
    ]
  }
]
```

```python
# .claude/stop_check.py —— 最小示例:检查现状文档今天有没有更新
import datetime, pathlib
ROOT = pathlib.Path(__file__).parent.parent
status = ROOT / "STATUS.md"
today = datetime.date.today().isoformat()
if not status.exists() or today not in status.read_text(encoding="utf-8"):
    print(f"⚠️ 提醒:STATUS.md 今天({today})还没更新,别忘了收尾留档。")
```

**效果**:这就是「自动检验」——收尾纪律不靠人记,靠 hook 兜底。被提醒到,就说明这次差点漏了,当场补上。

---

## 3. 一套「跨会话记忆」文件约定(上下文不丢、决策不反复)

光有 hook 还不够,得有几份**约定好职责的文件**让 hook 去读、让人去维护:

- **项目说明**(`CLAUDE.md`,开工第一份读):角色、目标、规矩、绝不做的事。
- **当前状态**(`STATUS.md`,覆盖式快照,永远 ≤ 一屏):现在做什么、卡在哪。**关键是覆盖、不是追加**——旧状态挪走,别往下堆,否则越读越长。
- **决策记录**(`DECISIONS.md`,只增不改):做过的决定记下来,下次别重新吵同一件事。
- **会话总结**(按日期一个文件):这次干了什么的完整细节,历史留这儿,别塞进「当前状态」。

**效果**:上下文跨会话不丢;已经拍过的板不会被反复推翻。

---

## 4. 把重复的工作流打包成 skill

**问题**:同一类活(生成 PRD、设计表、写测试、做复盘)每次都要把要求重讲一遍。

**做法**:把这类可复用的工作流固化成一个 skill(一段专门指令 + 配套模板/检查清单),Claude Code 会在合适的时候自动调用。这正是本仓 157 个 skill 的由来——见 [README](README.md)。

**效果**:重复的判断和步骤沉淀下来,不用每次口述;质量也更稳定。

---

## 5. 让 Claude 先摸真实状态,再动手(别拍脑袋)

**问题**:AI 容易凭印象改代码、下结论,结果对不上真实情况。

**做法**:在项目说明里定成规矩——改文件前先读它、先 `grep`、先看 `git status`;下任何结论都要带代码/数据证据,而不是「我觉得」。本仓的实践是:审代码前先核对工作树和目标分支是否一致,不一致就用 `git show <sha>` 对准,绝不信可能过期的本地行号。

**效果**:少一批「看着对其实错」的改动和误判。

---

## 6. 在项目说明里写死「红线 / 绝不做的事」

**问题**:有些操作代价很大(改了不该改的仓、删了不该删的东西、把内部内容推到公开仓)。

**做法**:把这些**明确写进 `CLAUDE.md` 的红线区**,并声明「子任务 / 子 agent / workflow 一律生效,不能绕过」。让每个会话开局就守住。

**效果**:高代价操作有硬边界,不靠临场判断。

---

## 7. 用可回归的验证兜住每次改动

**问题**:改了一个 skill / 一段代码,怎么知道没把别处弄坏?

**做法**:准备一组固定的验证用例(本仓用 `_eval/` 那套),改动前后各跑一遍,对比有没有回归。生成的代码尤其要过静态检查 + 针对性测试(并发、幂等、边界)——因为人眼单点复核一定会漏。

**效果**:改进有「改前 < 改后」的证据,不是凭感觉说「变好了」。

---

## 更新记录

- 2026-07-08 · 初版,7 条(SessionStart/Stop hook、记忆文件约定、skill 化、先摸实况、红线、可回归验证)。后续发现好用法继续往这补。
