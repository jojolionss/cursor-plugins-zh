# cursor-plugins-zh

[cursor/plugins](https://github.com/cursor/plugins) 里 pstack 与 thermos 两个插件的本地汉化版。只汉化 description,也就是技能选择器悬浮卡片里的那段介绍,以及插件管理页的简介。技能名称和正文保持英文原样。

## 目录结构

- `plugins/pstack`、`plugins/thermos` 是汉化后的插件,安装时选这两个目录。它们由 `sync.py` 全量重建生成,不要手改,重跑同步会覆盖。
- `translations/pstack.json`、`translations/thermos.json` 是翻译映射表,也是这个仓库里唯一需要人维护的文件。键是插件内的文件路径,值是 `{en, zh}`。`en` 存翻译时的原文,用来检测上游后来有没有改过这段话。
- `sync.py` 是同步脚本。拉取上游仓库,重建 `plugins/`,套用翻译,再做完整性校验。
- `refresh_cursor_cache.py` 把当前 `plugins/` 拷进 Cursor 钉死的本地 marketplace 缓存。`sync.py` 和 `git commit` 不会让已装插件跟进新 SHA,要靠这个脚本,然后新开对话。
- `upstream/` 是上游仓库的稀疏克隆,已被 git 忽略,不入库。

## 安装

1. 在 Cursor 的插件管理里卸载或停用商店版的 pstack 和 thermos。不卸载的话,每个技能会出现英文、中文两份。
2. 确认本仓库至少有一次 git commit(`git rev-parse HEAD` 能打出 SHA)。Cursor 加载本地 marketplace 时会解析 `plugin@HEAD`;仓库还没有 commit 时会报 `Failed to resolve version for plugin *@HEAD`,界面显示「加载插件错误」,并可能拖慢插件重载。
3. 用插件面板的本地安装入口,选中仓库根目录 `~/cursor-plugins-zh`(不是 `plugins/` 子目录)。Cursor 要求所选文件夹带有 `.cursor-plugin/marketplace.json`,本仓库根目录已按上游同款格式配好,里面挂了 pstack 和 thermos 两个插件。
4. 在弹出的列表里安装这两个插件。
5. 重新打开聊天输入框的技能选择器,悬浮介绍应显示为中文。

## 跟上游更新

```bash
cd ~/cursor-plugins-zh
python3 sync.py
```

脚本会 git pull 上游,整体重建 `plugins/`,套用翻译,并校验除 description 之外所有内容与上游逐字节一致。断网时加 `--offline` 跳过拉取。

同步完记得 `git commit`,然后跑:

```bash
python3 refresh_cursor_cache.py
```

在插件面板添加这个本地 marketplace 时,Cursor 把它钉在一个 commit 上,把这个 commit 克隆到 `~/.cursor/plugins/marketplaces/_/users/<你>/<sha>/`,再把每个插件拷进 `~/.cursor/plugins/cache/cursor-plugins-zh/<插件>/<sha>/`,两处目录都按这个 SHA 命名。

钉住的通常是添加时的 HEAD,但三次添加里有一次钉的是更早的 commit,原因不明。添加或重加之前先 `git commit`,否则没有 commit 可钉。加完不要假设钉的就是 HEAD,按下面的方法核对版本号。

`refresh_cursor_cache.py` 把当前 `plugins/` 拷进正在生效的 SHA 目录,不改钉住的 commit。这是日常更新的快路径。拷完后**新开一个对话**,斜杠菜单才会出现新技能。Cursor 之后若重新克隆,会还原成钉住的 commit 的内容,所以改动要落在 commit 里才算数。

要让 Cursor 钉到新 commit,或者缓存已经被还原回旧内容,到插件面板把整个本地 marketplace(不是两个插件)移除,再选 `~/cursor-plugins-zh` 加一次。验证:pstack 版本应等于 `plugins/pstack/.cursor-plugin/plugin.json` 的 version,技能列表里应有 `/bro` 和 `/no-comments`。`comment-sicko` 是子代理,斜杠入口是 `/no-comments`,菜单里显示为 Comment Sicko,没有 `/comment-sicko` 这条命令。

上游新增技能或改了原文时,终端会列出这些条目,同时写入 `translations/pending.json`。把它们补译进 `translations/*.json`,再跑一次 `sync.py` 即可。也可以直接把这句话交给 agent:

> 把 translations/pending.json 里的条目补译进 translations/*.json(风格对齐已有条目),然后重跑 python3 sync.py,确认校验通过。

想备份到自己的 GitHub,这个目录本身就是 git 仓库,`git remote add origin <你的仓库>` 后 push 即可。

## 汉化范围

只译 frontmatter 和 plugin.json 里的 description。这段文字有两个读者:技能选择器里的你,以及靠它判断何时触发技能的模型。译文保留了英文触发词(如 `/swarm`、"arena this"),所以英文触发不受影响。正文不译,因为正文是给 agent 执行的指令,翻译会引入行为偏差,而且平时也不需要看。译文第三人称、不超过 1024 字符,符合 Cursor 对 description 的要求。

在保留英文触发词的基础上,常用技能的译文还补充了中文触发短语,统一用『』标注,例如『打擂台』(arena)、『蜂群』(swarm)、『说人话』(bro)、『复盘』(reflect)、『poteto 模式』(poteto-mode)。斜杠命令(`/swarm` 这类)来自技能目录名,不能翻译,保持英文;principle-* 等仅供内部引用的技能不加触发词。

注意触发词的实际生效范围。pstack 里只有 how、why、unslop、setup-pstack、typescript-best-practices 五个技能允许模型按 description 自动触发,对它们说中文即可命中。其余 pstack 技能(arena、swarm、bro 等)和 thermos 的三个技能都带 `disable-model-invocation: true`,这是上游设计:入口是斜杠命令手动附加,或由 poteto-mode 等流程在会话内部调用;对这些技能,中文触发短语的作用是悬浮卡说明,以及进入 poteto 会话后的路由提示。子代理(poteto-agent、Comment Sicko、thermos 两个评审)始终按 description 被路由,中文描述直接生效。

## 技能速查表

以插件内实际 description 为准,此表只作快速索引。

### pstack 工作流技能

| 技能 | 一句话 |
|---|---|
| poteto-mode | poteto 整套代理风格的入口(`/poteto-mode`) |
| how | 讲清"X 是怎么工作的",改代码前的走读 |
| why | 讲清"为什么这样设计",带证据引用 |
| teach | 结合 how 与 why,把一段工作给人讲懂 |
| architect | 先设计类型、签名、模块结构,再写代码 |
| arena | N 个候选实现打擂台,选基底再嫁接优点 |
| swarm | 扇出 N 个并行 worker,汇总成一份报告 |
| interrogate | 多模型对抗式评审 |
| reflect | 三个子代理复盘当前会话,把经验落到技能修改 |
| recall | 重建"我做到哪了"的现状简报 |
| figure-it-out | 没有现成 playbook 时,为任务定制可审计方案 |
| blast-radius | 找出 diff 之外的连带破坏点并用真实代码证明 |
| tdd | 明确要求或有廉价测试标的时,测试先行 |
| create-verification-skill | 为项目生成像用户一样驱动应用的验证技能 |
| maintain-verification-skill | 周期巡检验证技能与功能地图是否失真 |
| show-me-your-work | 长任务留一份可审查的决策日志 |
| automate-me | 把个人偏好与工作风格沉淀成 -mode 技能 |
| setup-pstack | 配置 pstack 各角色用什么模型 |
| typescript-best-practices | TypeScript 最佳实践,读写 .ts/.tsx 时生效 |
| unslop | 去除文字里的 AI 腔,始终应用 |
| bro | 把上一条消息用大白话重讲,『说人话』 |
| no-comments | 评审前清剿注释,派 Comment Sicko 执行 |
| technical-writing | 文档、RFC、PR 描述、commit message 的分层写作标准 |

### pstack 原则技能(principle-*)

| 技能 | 一句话 |
|---|---|
| laziness-protocol | 最小改动,偏向删除 |
| foundational-thinking | 先定数据结构,再写逻辑 |
| redesign-from-first-principles | 新需求当作第一天就有,重新设计而非打补丁 |
| subtract-before-you-add | 先做减法,再做加法 |
| minimize-reader-load | 降低读代码的心智负担 |
| outcome-oriented-execution | 直奔目标架构,不留一次性兼容代码 |
| experience-first | 体验优先于实现方便 |
| exhaust-the-design-space | 无先例的决策先做 2-3 个原型比较 |
| build-the-lever | 造工具去做事,而不是手工做 |
| model-the-domain | 用结构为领域建模,替代散落的条件判断 |
| boundary-discipline | 校验收口在系统边界,内部信任类型 |
| type-system-discipline | 让非法状态在类型上无法表示 |
| make-operations-idempotent | 操作重复执行也收敛到同一终态 |
| migrate-callers-then-delete-legacy-apis | 迁完调用方,同一波删掉旧 API |
| separate-before-serializing-shared-state | 先消除共享状态,再考虑串行化 |
| prove-it-works | 对真实产物验证,不信代理指标 |
| fix-root-causes | 修根因,不糊症状 |
| sequence-verifiable-units | 拆成小单元,步步可验证地推进 |
| guard-the-context-window | 守住上下文窗口,大块内容交给子代理 |
| never-block-on-the-human | 可逆的事直接做,不停下来问 |
| encode-lessons-in-structure | 把重复的教训固化成结构而非文字 |

### pstack 其他

| 条目 | 一句话 |
|---|---|
| poteto-agent(子代理) | `/poteto-mode` 请求的路由目标 |
| comment-sicko(子代理) | 注释仇视者,由 no-comments 派出的执行体 |
| benny 三个技能 | 随插件附带的自动化模板(分诊、复现修复、安装配置),不出现在技能选择器 |

### thermos

| 条目 | 一句话 |
|---|---|
| thermos | 并行跑两种 thermo-nuclear 评审再汇总 |
| thermo-nuclear-review | 分支变更的安全与正确性深度审计 |
| thermo-nuclear-code-quality-review | 极严苛的可维护性评审 |
| 两个 subagent | 供 Task 调用的上述两种评审执行体 |

## 出处与许可

整个 `plugins/` 目录由 `sync.py` 从 [cursor/plugins](https://github.com/cursor/plugins) 生成。上游 pstack 与 thermos 都是 MIT 许可,pstack 版权归 Lauren Tan,thermos 版权归 Cursor。`plugins/pstack/LICENSE` 与 `plugins/thermos/LICENSE` 就是上游的许可文件,原样保留。

本仓库自己的代码,即 `sync.py`、`refresh_cursor_cache.py`、`translations/` 映射表和这份 README,以 MIT 许可发布,许可文件是根目录的 `LICENSE`。

只译 description 字段。技能正文与上游逐字节一致,不一致时 `sync.py` 会直接报错。

这是非官方的社区汉化,与 Cursor 和上游作者没有关联,也没有获得他们的背书。翻译问题请在本仓库反馈,不要报给上游。
