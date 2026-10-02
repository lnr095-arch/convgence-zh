# CONVRGENCE 中文汉化包 · 人工校对版 v1.0

**中文 | [English](#english)**

《CONVRGENCE》（Steam AppID 2609610，VR 生存射击）没有官方中文。
本包基于开源机翻工具 [apocalyptic_translatorZ](https://github.com/peurKe/apocalyptic_translatorZ) 的成果，
对全部译文做了一遍人工重写，并补上了机翻工具结构上碰不到的 233 条文本。

> 本包与 apocalyptic_translatorZ 作者无关，不是官方移植，也不隶属于任何商业发行。

**下载**：[`CONVRGENCE_中文汉化包_人工校对_v1.0.zip`（17.66 MB）](https://github.com/lnr095-arch/convgence-zh/releases/latest)

---

## 和「直接跑机翻」的差别

游戏内共 1700 条唯一文本、7726 个显示槽位。

| | 机翻版 | 本包 |
|---|---|---|
| 人工重译 / 确认 | 0 | **1549 条（91%）** |
| 覆盖显示槽位 | 7726 | **6322（82%）** |
| 未翻译（俄文原样） | 全部 | 3 块制作名单（按需求保留） |
| 工具够不着的文本 | 漏 | 已补 **233 条** |

「工具够不着的 233 条」具体是：

- 场景文件里 175 处开发者占位标题（`НАЗВАНИЕ 3` → `标题 3`）和两条前身作品《Paradox of Hope》的提示；
- `global-metadata.dat` 里 58 条硬编码 C# 常量——PDA 的物品描述、价格状态、计量单位、皮肤/款式名、计时器标签。
  这些是代码里的字符串字面量，不是被序列化的文本，机翻工具的扫描器看不到它们。

剩下 148 条机翻本来就译对了的短标签（`钱包`、`扳手`、`肥皂` 之类）直接保留，没有为了改而改。

## 安装

1. 解压，把**包内全部内容**复制到游戏根目录（与 `CONVRGENCE.exe` 同级），不要多套一层文件夹。
2. 双击 `安装汉化.bat`。它会先启动翻译器向导（一路确认即可，首次会备份原文件），
   完成后自动接着执行 `tools\apply_extra.ps1`，补上上面那 233 条。
3. 进游戏。

**适用版本**：1.0 / buildid 25630966。脚本会做字节预检，版本不符时 `refused>0`，
此时**不会写入任何内容**，等更新即可——不会把游戏写坏。

## 卸载 / 还原

双击 `卸载还原.bat`：233 条补充文本按包内保存的原始字节精确还原；
其余文本用 apocalyptic_translatorZ 自带的还原方式（从 `BACKUP` 恢复），
兜底是 Steam「校验游戏文件完整性」。

## 翻译说明

- 原文是**俄语**（开发者为俄国人），译文从俄语原文直译，未走英语中转。
- 术语对齐国内《潜行者》圈：`Зона`=特异区、`артефакт`=神器、`аномалия`=异常、`выброс`=喷发、
  `изменённый`=异化、`разлом`=裂隙、`сталкер`=潜行者、`хабар`=货。
- 武器型号保留拉丁写法（VSS / PPSh-41 / AKM / SVD / Saiga-12 / Groza / VOG-17 / MON-50），
  中文玩家认的是型号，不是音译。
- 第二人称统一「你」；俄式俚语按语气分级保留，没有做净版化。
- 多行文本保持与原文相同的换行位置；`{0}`、`{1:0}` 这类格式占位符原样保留。
- **字节约束**：本工具链是等长原地覆写，每条中文的 UTF-8 字节数不能超过俄文原文，
  所以个别标签是压缩过的（「光棒」「夜视」「Saiga 消音」），这不是漏译。

## 已知未译

1. 片尾制作名单 3 块（约 9 KB，人名 / handle / sketchfab 链接）——只译职务名才有意义，整块保留原文。
2. 模型与贴图的内部引用名 11 处（`Молотов_Бутылка_BaseColor`、`Цилиндр.001`）——改了会断引用，
   它们的显示文本本身已经是中文。
3. 开发者调试输出 20 条——正常游玩不会显示。
4. 烤在场景贴图上的俄文（`НЕ КУРИТЬ!`、门上的 `…ЩИТ`）——属于纹理不是文本，要汉化得改图。

## 常见问题

**重跑机翻工具后中文没了？**
本包 1549 条人工稿写进了工具的 DB（`_____peurKe` 覆盖字段），正常重跑不会丢。
但那 233 条不在 DB 里，重跑后需再执行一次：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\apply_extra.ps1 -Mode apply
```

如果你之前跑过旧版机翻，请先删除
`apocalyptic_translatorZ\25630966\translations\auto_to_zh\`（陈旧的机翻结果 + `done.txt` 短路标记，
它会让工具跳过重译并把旧文件复制回来）。

**某个名字显示挤在一起没有空格？**
TMP 字体的西里尔回退字形把空格渲染成零宽，属于原版显示问题；换成中文后自然消失。

**会不会封号？**
本包只改游戏目录内的本地文件，不触碰网络、内存和服务端。该游戏为单机 VR。

## 本仓库内容

| 路径 | 说明 |
|---|---|
| `CONVRGENCE_ZH/` | 发布包源文件。**不含** `apocalyptic_translatorZ.exe`——那是上游工具，只随 Release 的 zip 分发 |
| `CONVRGENCE_ZH/apocalyptic_translatorZ/DB/json/zh_CONVRGENCE.json` | 翻译库，已 stamped 1549 条人工稿（1569 个源文 / 2667 行） |
| `CONVRGENCE_ZH/tools/apply_extra.ps1` | 233 条补丁的执行端（PowerShell 5.1，无需安装任何东西） |
| `CONVRGENCE_ZH/tools/data/` | 补丁数据表（`placeholders.json` 175 条 / `meta_literals.json` 58 条） |
| `work/fixes.json` | 1549 条人工稿，以 DB id 为键（只含中文，不含游戏原文） |
| `work/glossary.md` | 术语与语气规范 |
| `work/*.py` | 语料抽取、字节预算校验、等长覆写、DB 合并、打包与端到端测试脚本 |

`work/*.py` 是一次性的加工脚本，路径写死为本机的默认 Steam 目录（`D:\steam\steamapps\common\CONVRGENCE`），
仅作「译文是怎么来的」的存证，不作为工具维护；玩家不需要运行它们。

## 许可与致谢

- 上游机翻工具 **apocalyptic_translatorZ** 由 peurKe 开发，MIT 许可，许可全文见
  [`LICENSE-apocalyptic_translatorZ.txt`](LICENSE-apocalyptic_translatorZ.txt)。本包按原样分发其可执行文件，未做任何修改。
- 游戏、俄文原文与全部素材版权归 **Nikita Zhuravlev / Monkey-With-a-Bomb**。
  本包不含任何游戏原始文件，分发的只是译文文本与补丁数据表。
- 本包的人工译文：**免费粉丝作品，欢迎署名后转发、二次校对、并入其他汉化工程；请勿用于商业用途**。
  商业使用请先联系作者。（上游工具是 MIT，但译文本身不套用 MIT，因为 MIT 不允许附加非商业限制。）
- 如开发者或版权方认为应当下架，请开 issue，我会立即删除并把仓库转为归档状态。

---

## English

A human-proofed Simplified-Chinese translation of **CONVRGENCE** (Steam AppID 2609610,
VR survival shooter by Nikita Zhuravlev / Monkey-With-a-Bomb). The game ships Russian text
and has no official Chinese. The open-source tool
[apocalyptic_translatorZ](https://github.com/peurKe/apocalyptic_translatorZ) (MIT) machine-translates
it in place, but the raw output reads badly. This package keeps that tool as the engine and
replaces its output: **1549 of 1700 unique strings (91%) retranslated by hand, covering 6322 of
7726 display slots (82%)**, plus **233 strings the MT tool structurally cannot reach**
(175 developer placeholder titles in the scene files, 58 hardcoded C# string literals in
`global-metadata.dat` — PDA item descriptions, price states, units, skin names).

- Translated from the Russian source, not via English. Terminology follows the Chinese
  STALKER convention (Zone / artifact / anomaly / emission / breach). Weapon designations
  stay in Latin (VSS, PPSh-41, Saiga-12…). Credits are left untouched.
- Requires game version 1.0 / buildid 25630966. The patcher byte-preflights every offset and
  writes nothing if the version does not match, so it cannot corrupt a mismatched install.
- Install: copy the release zip's contents next to `CONVRGENCE.exe`, run `安装汉化.bat`.
  Uninstall: run `卸载还原.bat`, or verify game file integrity in Steam.
- Local files only — no network hooks, no memory injection.
- The upstream exe is redistributed under its MIT license (full text included); it is only in
  the release zip, not in git. Fan translation, non-commercial.
