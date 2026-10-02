CONVRGENCE 中文汉化包（人工校对版）v1.0
=====================================

游戏：CONVRGENCE（Steam AppID 2609610，VR 生存射击）
适用版本：1.0 / buildid 25630966（其他版本会被预检拦下，不会写坏文件）
汉化基础：apocalyptic_translatorZ（作者 peurKe，MIT 许可）
人工校对：本包作者


这个包里有什么
--------------
  apocalyptic_translatorZ.exe        机翻工具本体（MIT，见 LICENSE-apocalyptic_translatorZ.txt）
  apocalyptic_translatorZ\DB\json\   已写入 1549 条人工校对的翻译库（离线可用，不会再联网机翻）
  tools\apply_extra.ps1              补上机翻工具碰不到的 233 条文本
  tools\data\                        补丁数据表
  安装汉化.bat / 卸载还原.bat


安装（三步）
------------
1. 把本包【全部内容】复制到游戏根目录，也就是与 CONVRGENCE.exe 同级的那层：
       <Steam 库>\steamapps\common\CONVRGENCE\
   不要多套一层文件夹，工具是靠自身所在路径去找游戏的。

2. 双击「安装汉化.bat」。
   - 它会先启动 apocalyptic_translatorZ，按提示点确认即可（首次会备份原文件到
     apocalyptic_translatorZ\25630966\BACKUP，务必别删这个目录）。
   - 它跑完后，脚本会自动接着执行 apply_extra.ps1，补上两类工具够不着的文本：
       · 场景文件里 175 处开发者占位标题（НАЗВАНИЕ → 标题）与两条前身《Paradox of Hope》提示
       · il2cpp 代码常量里 58 条硬编码文案（PDA 物品描述、价格状态、单位、皮肤/款式名等）

3. 进游戏。若某处仍是英文/俄文，见下方"已知未译"。

只要第 2 步的窗口里出现 refused>0 或 [SKIP]，说明游戏版本与本包不一致，
此时不会写入任何内容，请等本包更新。


卸载 / 还原
-----------
双击「卸载还原.bat」：
  - 233 条补充文本由 apply_extra.ps1 -Mode restore 精确还原（原始字节来自包内数据表，
    并在首次运行时把 global-metadata.dat 原件存为 tools\global-metadata.dat.orig）；
  - 其余文本请再跑一次 apocalyptic_translatorZ.exe，或用它自己生成的
    "apocalyptic_translatorZ (restore).lnk" 从 BACKUP 还原；
  - 兜底：Steam 库 → 本游戏 → 属性 → 本地文件 → 校验游戏文件完整性（会还原全部文件，
    之后想再用本包，重新执行安装即可）。


翻译说明
--------
· 原文是俄语（开发者为俄国人），译文按俄语原文直译，未走英语中转。
· 术语对齐国内《潜行者》圈：Зона=特异区、артефакт=神器、аномалия=异常、
  выброс=喷发、изменённый=异化、разлом=裂隙、сталкер=潜行者、хабар=货。
· 武器型号保留拉丁（VSS / PPSh-41 / AKM / SVD / Saiga-12 / Groza / VOG-17 / MON-50 …），
  因为中文玩家认的是型号而不是音译。
· 第二人称统一「你」；俄式俚语按语气分三级保留，脏话按原文密度处理（原文 мат 很少，
  俚语很多），没有做净版化。
· 多行文本保持与原文相同的换行位置；{0}、{1:0} 这类格式占位符原样保留。
· 字节约束：本工具链是等长原地覆写，每条中文必须不超过俄文原文的 UTF-8 字节数，
  所以个别标签是压缩过的（如「光棒」「夜视」「Saiga 消音」），并非漏译。


已知未译
--------
1. 片尾制作名单 3 块（约 9 KB，内容为人名、handle 与 sketchfab 链接）——只译职务名才有意义，
   整块保留原文。
2. 模型/贴图内部名 11 处（如 Молотов_Бутылка_BaseColor、Цилиндр.001）——是引擎引用名，
   改了会断引用，其显示文本已是中文。
3. 开发者调试输出 20 条（EmeraldAISystem / RestrictedIntersectionCheck / SlotMachine3Reel /
   地形编辑器 / 服务器同步日志）——正常游玩不会显示。
4. 贴在场景贴图上的俄文（如「НЕ КУРИТЬ!」、门上的「…ЩИТ」）——属于纹理，不是文本，
   需要改图才能汉化。


版权与致谢
----------
· 机翻工具 apocalyptic_translatorZ 版权归 peurKe 所有，MIT 许可，原文见
  LICENSE-apocalyptic_translatorZ.txt；本包按其许可条款随附该程序与许可全文。
· 游戏文本与素材版权归 Monkey-With-a-Bomb / Nikita Zhuravlev 所有。
· 本包为免费粉丝翻译，不含任何游戏原始文件，不作商业用途。
· 如权利方认为不妥，联系下架即可；官方若推出中文，本包随即停止分发。
