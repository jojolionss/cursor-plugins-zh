# cursor-plugins-zh

[cursor/plugins](https://github.com/cursor/plugins) 里 pstack 与 thermos 两个插件的本地汉化版。只汉化 description,也就是技能选择器悬浮卡片里的那段介绍,以及插件管理页的简介。技能名称和正文保持英文原样。

## 目录结构

- `plugins/pstack`、`plugins/thermos` 是汉化后的插件,安装时选这两个目录。它们由 `sync.py` 全量重建生成,不要手改,重跑同步会覆盖。
- `translations/pstack.json`、`translations/thermos.json` 是翻译映射表,也是这个仓库里唯一需要人维护的文件。键是插件内的文件路径,值是 `{en, zh}`。`en` 存翻译时的原文,用来检测上游后来有没有改过这段话。
- `sync.py` 是同步脚本。拉取上游仓库,重建 `plugins/`,套用翻译,再做完整性校验。
- `upstream/` 是上游仓库的稀疏克隆,已被 git 忽略,不入库。

## 安装

1. 在 Cursor 的插件管理里卸载或停用商店版的 pstack 和 thermos。不卸载的话,每个技能会出现英文、中文两份。
2. 用插件面板的本地安装入口,选中仓库根目录 `~/cursor-plugins-zh`(不是 `plugins/` 子目录)。Cursor 要求所选文件夹带有 `.cursor-plugin/marketplace.json`,本仓库根目录已按上游同款格式配好,里面挂了 pstack 和 thermos 两个插件。
3. 在弹出的列表里安装这两个插件。
4. 重新打开聊天输入框的技能选择器,悬浮介绍应显示为中文。

## 跟上游更新

```bash
cd ~/cursor-plugins-zh
python3 sync.py
```

脚本会 git pull 上游,整体重建 `plugins/`,套用翻译,并校验除 description 之外所有内容与上游逐字节一致。断网时加 `--offline` 跳过拉取。

如果 Cursor 安装本地插件时是把目录拷贝走而不是原地引用,更新后还需在插件面板重新安装一次这两个目录。装完第一次更新时留意一下即可。

上游新增技能或改了原文时,终端会列出这些条目,同时写入 `translations/pending.json`。把它们补译进 `translations/*.json`,再跑一次 `sync.py` 即可。也可以直接把这句话交给 agent:

> 把 translations/pending.json 里的条目补译进 translations/*.json(风格对齐已有条目),然后重跑 python3 sync.py,确认校验通过。

想备份到自己的 GitHub,这个目录本身就是 git 仓库,`git remote add origin <你的仓库>` 后 push 即可。

## 汉化范围

只译 frontmatter 和 plugin.json 里的 description。这段文字有两个读者:技能选择器里的你,以及靠它判断何时触发技能的模型。译文保留了英文触发词(如 `/swarm`、"arena this"),所以模型触发不受影响。正文不译,因为正文是给 agent 执行的指令,翻译会引入行为偏差,而且平时也不需要看。译文第三人称、不超过 1024 字符,符合 Cursor 对 description 的要求。

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
| benny 三个技能 | 随插件附带的自动化模板(分诊、复现修复、安装配置),不出现在技能选择器 |

### thermos

| 条目 | 一句话 |
|---|---|
| thermos | 并行跑两种 thermo-nuclear 评审再汇总 |
| thermo-nuclear-review | 分支变更的安全与正确性深度审计 |
| thermo-nuclear-code-quality-review | 极严苛的可维护性评审 |
| 两个 subagent | 供 Task 调用的上述两种评审执行体 |
