---
name: "uheg"
description: "UHEg项目模板仓库的正文写作与编译规范:make 编译、内容/ 章节与独立页入口、配置.typ(导入/导航/元素数据/网页模板)、元素系统 CSV、中文模板函数与站点参数、Markdown 导入、Git LFS 图片、网页发布、白描直陈语法与常见坑。在写或改 内容/ 下 .typ、配置.typ、附件/元素系统.csv,或编译、发布网页时调用。"
---

# UHEg 正文写作规范

UHEg 是基于[地狱之下](https://typst.app/universe/package/underhell)模板（UnderHell Template）
整理的项目模板仓库,用于快速创建设定集/冒险/规则文档项目。仓库没有子模块,模板以 Typst 包
`@preview/underhell:<版本>` 形式引入(版本号见 `配置.typ`,当前 `0.6.1`)。模板函数实现细节见
模板包自身,本技能只讲**用这套结构写正文**。模板本身的开发规范见模板仓库的 `.skills/SKILL.md`。

## 文件结构

| 路径 | 说明 |
|------|------|
| `配置.typ` | 站点配置。`#import "@preview/underhell:<版本>": *` 再导出模板;定义 `导入`(重定义,见下)、`元素数据`(读 CSV)、`网页模板 = 地狱之下模板.with(...)`、`站点链接`(页脚导航)、`导航` |
| `内容/index.typ` | 全量入口:`#show: 网页模板` + `#outline` + 各章 `#include` |
| `内容/<名>.typ` | 各章正文,**自带 `#import "../配置.typ": *`**;路径即 URL 段 |
| `内容/<目录>/index.typ` | 目录页正文 → URL `/<目录>/` |
| `脚本/页面.typ` | 网页各独立页的统一入口,`make` 传 `--input 页=<路径> --input 源=<路径>` |
| `脚本/web_post.sh` | 网页后处理:抽公共 CSS 到 `/assets/underhell.css`、把定义在别页的元素连成链接、注入目录/评论开合脚本 |
| `附件/元素系统.csv` | 元素系统宽表(首列=元素 id,其后每列=一个系统) |
| `图片/` | 图片素材,已配置 Git LFS |
| `.webfonts/` | 自托管网页字体源目录(默认隐藏),默认只有说明文件;放入 4 个 `.woff2` 后 `make web` 会拷到产物 `dist/webfonts/`(见 `.webfonts/README.md`) |
| `Makefile` | 编译脚本 |
| `.github/workflows/web.yml` | 推送 `main` → 构建并强推 `web` 分支 |

## 配置.typ 里的项目约定

- **`导入(路径, 偏移: 1)`** —— 重定义模板同名函数。模板版用 `include "/" + 路径`,而包内文件的
  `/` 以*包根*为基准(Typst 沙箱),会去包缓存里找本项目文件而报错;项目版改在 `配置.typ` 内定义,
  `/` 即以 `--root`(项目根)为基准。调用处照旧写仓库根相对路径,如 `#导入("内容/地理/主行星.typ")`,
  默认把被导入文件的标题层级整体 +1。被导入文件自行 `#import` 所需函数,不继承作用域。
- **`导航`** —— 项目自定义的站内导航表(`((显示名, 路径), …)`)。当前未被任何页面引用;
  需要时自己在正文(通常在 `#if is_web() [ … ]` 内)取用,或按 README 提示修改/禁用。
- **`网页模板`** —— `地狱之下模板.with(title: …, subtitle: …, author: …, lang: "zh", paper: "a4", 品牌名: …, 备案号: "", 元素系统数据: 元素数据)`。
  封面/logo 走模板默认;要加图就把图片放进本项目,再 `cover: image("…")` / `logo: image("…")`。

## 编译

```sh
make pdf    # 内容/ 下全部 .typ → dist/*.pdf(逐页经 脚本/页面.typ 套模板)
make web    # 多页站点 → dist/(含 /assets/underhell.css)
make watch  # 监听 内容/index.typ,自动重编 dist/index.pdf
make clean  # rm -rf dist
```

直接 typst(关键:`--root .` 让项目根成为路径基准):

```sh
typst compile --root . 内容/index.typ dist/index.pdf
typst compile --root . --features html --input web=true --format html 内容/index.typ dist/index.html
typst compile --root . --input 元素系统=学术 内容/index.typ dist/index.pdf   # 切换元素系统
```

网页是多页站点:入口 `内容/index.typ` → `dist/index.html`;其余 `内容/<路径>.typ` 经
`脚本/页面.typ` 套模板 → `dist/<路径>/index.html`;目录页 `内容/<目录>/index.typ` →
`dist/<目录>/index.html`。逐页导出后由 `sh 脚本/web_post.sh dist` 收尾。

PDF 走同一套页面集合:入口 `内容/index.typ` 直接编译 → `dist/index.pdf`(整本,自带封面与目录);
其余各页经 `脚本/页面.typ` 套模板 → `dist/<路径>.pdf`,**目录页也同名**:`内容/<目录>/index.typ` →
`dist/<目录>.pdf`(非 `dist/<目录>/index.pdf`)。章节是片段、不自己 `#show`,直接单独编译
会没有模板样式,故必须经 `页面.typ`。

网页每页右上角的「PDF」链接指向本页同名 `.pdf`(如 `/世界纲要/` → `/世界纲要.pdf`、
`/地理/` → `/地理.pdf`),由 `配置.typ` 的 `站点链接(本页PDF)` 生成,各页入口按自身路径传入。

## 章节写法

- 每章必须以 `#import "{具体的相对路径}/配置.typ": *` 开头——模板成员经 `配置.typ` 再导出,**正文只引
  `配置.typ`,不直接引 `@preview/underhell`**,站点配置也走同一出口。
- 标题直接用 `= / == …`;新增章节后在 `内容/index.typ` 里加 `#include "新章.typ"`。
- 章节是"只管正文"的片段,不自己 `#show`——模板由 `脚本/页面.typ` 统一套用,这样同一份正文
  既能被整份 `#include`,也能单独成一页。
- 需要引入另一份 `.typ` 并整体降一级标题时,用 `配置.typ` 的 `#导入("内容/….typ")`(见上)。

## 元素系统(`附件/元素系统.csv`)

- 宽表:首行是系统名(如 `id,默认,别名,学术`),首列是元素 id,单元格为该元素在该系统下的
  名词,**留空则回退到 id 本身**。
- `配置.typ` 用 `csv("附件/元素系统.csv")` 读入,作为 `元素系统数据` 传给模板。
- 正文引用用 `#元素[id]`(如 `#元素[古龙]`);正文中直接写 `#元素(…)`,**不要用 `[ ]` 包裹**;
  仅在函数参数位置(如 `#表格(...)`、`name:`)用 `[...]` 包成 content。
- 定义某概念的章节标题用 `#设定元素(level: n)[名]`(标题 + 锚点),`@名` 可交叉引用。
- 只要用了 `#元素("xxx")`,就必须把 `xxx` 写进 CSV 的 id 列;未定义的 `#元素` 在 PDF 编译时告警,
  网页里渲染成悬停"未定义"的 `span`(`web_post.sh` 会把定义在别页的元素连成链接)。
- `#元素总表()` 列出全部元素;文档内可用 `#设置元素系统("别名")` 动态切换。
- 编译时用 `--input 元素系统=<列名>` 切换系统(如 `--input 元素系统=学术`)。
- 元素化范围:仅核心概念(地名、生物类别、专有系统名)用 `#元素`;描述性文本保持普通文本。

## 模板函数(调用中文名)

调用一律用中文名,勿用英文旧名。示例见 `内容/概述.typ`(表格、提示框、元素总表)与
`内容/示例.typ`(属性框、人物框、法术)。

| 中文名 | 用途 |
|--------|------|
| `地狱之下模板` | 文档初始化/网页模板(入口用 `#show: 网页模板`) |
| `元素` | 当前元素系统下的深红名词,自动链接到定义标题 |
| `设定元素` | 普通模式=深红文本;传 `level:` 生成带 `<id>` 锚点的编号标题 |
| `设置元素系统` | 文档内切换元素系统 |
| `元素总表` | 列出当前系统下全部元素 |
| `导入` | `#include` 另一 `.typ` 并整体加深标题层级(默认 +1) |
| `表格` | 格式化表格,默认 2 列 1:4 |
| `提示框` | 彩色背景方框,可选标题 |
| `属性框` | D&D 风格属性块(字典参数) |
| `人物框` | NPC 卡片(字典参数) |
| `法术` | 法术卡片(字典参数) |
| `属性表` | 六维属性名/数值表(属性框、人物框内部亦用) |
| `侧标框` | 带黄色左右侧边的文本框(标题 + 内容) |
| `引用` | 左深红侧边条引用块,可选 `出处:` |
| `目录` | 目录(网页=浮动目录,PDF=居中目录页) |
| `世界纲要` | 单栏居中页;默认打印/网页隐藏,`--input 纲要=true` 可显示 |
| `网格` | 整数格对齐容器,`显示网格: true` 画格线 |
| `附录` | 文末附录,标题编号切字母(A.1…) |
| `顶部图` / `底部图` | 页面顶部/底部大图,跨两栏并抑制页脚 |
| `品牌` | 小型大写品牌名(取自 `品牌名`) |
| `版权声明` | 文末版权声明文本 |
| `评论` | 灰色注释(标题字体),`--input 隐藏评论=true` 可隐藏 |
| `TODO` / `TODO表格` | 待办标记 |

## 站点参数(`地狱之下模板.with(...)`)

除上面 `网页模板` 已用的 `title` / `subtitle` / `author` / `lang` / `paper` / `品牌名` /
`备案号` / `元素系统数据`,模板还接受:

- `cover`(封面 `image`)、`logo`、`fancy-author`(作者名火焰装饰)、`add-title`(首页是否打印标题)
- `font-size`(默认 12pt)、`bg`(内容页背景:`"default"` 羊皮纸 / `none` 打印白底 / `image(...)`)
- `元素系统`(缺省取 `--input 元素系统`,再回退 `"普通"`)、`页标题`(网页每页标题,缺省回退 `title`)
- `网址前缀`(自托管字体 URL 前缀,子路径部署时改)、`页脚链接`(`((标签:, 网址:, 提示:), …)`,网页右上角导航;本项目用 `配置.typ` 的 `站点链接(本页PDF)` 生成,PDF 项指向本页同名 `.pdf`)
- `备案链接`(`备案号` 设 `""` 则不渲染页脚)
- `主题`(`标题色`/`强调色` 影响 PDF 与网页,`纸色`/`墨色` 仅网页;值为 Typst 颜色或 CSS 色字符串)
- `阅读器`(`默认字号`/`默认字体` + `字号`/`字体` 档位列表,驱动网页阅读器面板)

`lang: "zh"` 加载模板包内的 `languages/zh.toml`:本地化 `属性框`/`人物框` 标签、中文标点替换、
字体(`[fonts]`:正文/标题/斜体/评论/目录)与自托管网页字体(`[web]` 段,生成 `@font-face`)。

## Markdown 导入

`内容/关于.typ` 演示把 Markdown 渲染进正文:`cmarker` 负责转译,`mitex` 让 `$…$` / `$$…$$`
里的 LaTeX 公式也能渲染,`scope` 把 Markdown 图片变成带题注的 `figure`。仓库根 `README.md`
即由它渲染进文档,故改动 README 会同步反映到「关于」页。

## 图片与 Git LFS

- `图片/` 下常见图片格式(png/jpg/jpeg/gif/webp/bmp/tif/tiff/avif/heic/heif/ico/psd)
  由根目录 `.gitattributes` 配置了 Git LFS(`svg` 一行已注释掉)。
- clone 前需装 `git lfs`,否则拿到的是指针文件;新图放进 `图片/` 即自动走 LFS。
- 引用图片用 `image("图片/xxx.png")`(路径相对当前 `.typ` 文件解析)。

## 字体(`.webfonts/`)

- 模板包 `languages/zh.toml` 的 `[web]` 段引用四个自托管 `.woff2`(正文/标题/粗体/评论),
  **文件名固定**;包内不含字体,由项目提供。
- 本项目默认不放字体(模板仓库不便用 Git LFS),`.webfonts/` 下只有说明;需要时按
  `.webfonts/README.md` 放入四个文件。缺字体不影响构建,网页回退系统字体。
- 源目录以 `.` 开头(默认隐藏),与对外路径**不同名**:`make web` 把 `.webfonts/*.woff2`
  拷到 `dist/webfonts/`(产物目录名固定为 `webfonts`,对应 `/webfonts/…` URL,勿改);
  `.github/workflows/web.yml` 在有字体时按页面实际用字子集化后再发布。

## 语法规范

中文:以直陈、白描为基本写法。少用状语、补语和副词,只保留有实际信息的修饰。
优先保留原本自然的语言习惯,不为深刻、优美、完整而润色。保持自然的长短句变化,
拒绝套用总分总结构,不强行总结或升华。

反例:「这个方法值得继续研究」不要写成「这个方法还有值得深入挖掘的空间」。

English: Use direct statements and plain prose. Minimize adverbials, complements,
and adverbs; use them only when they add concrete information. Preserve the
writer's natural voice. Do not polish simple language to sound deeper, more
elegant, or more complete. Keep natural variation in sentence length. Avoid rigid
summary structures and forced conclusions.

## 发布网页

`make web` 的 `dist/` 是纯静态站点(`.webfonts/` 有字体时,产物含 `webfonts/`)。推送 `main` 后
`.github/workflows/web.yml` 会重建、按页面用字子集化字体,并强推 `web` 分支;托管平台
(Cloudflare Pages / EdgeOne Pages)绑定 `web` 分支并**关闭平台侧构建**即可。分平台步骤见
根 `README.md`「部署网页」。

## 已知坑

1. `--root .` 必需——`配置.typ` 在项目根,正文以 `../配置.typ` 引用。
2. `#include` 的相对路径以**被 include 文件所在位置**解析(非调用处),且**不继承父文件作用域**,
   故每个 `内容/<路径>.typ` 必须自带 `#import "…/配置.typ": *`。
3. 正文顶层不能出现裸 `#p`——`#` 后必须是已定义符号,否则编译失败。
4. Typst 函数参数/变量名用简体中文(如 `基础层级`),勿混繁体。
5. 交叉引用标签用中文名或名词元素(id),`@标签` 需与 `<标签>` 一致。
6. 网页专属内容用 `#if is_web() [ … ]` 包裹(模板导出),PDF 编译时整段跳过。
7. `set heading(offset:)` 只对标记标题(`= ×N`)生效,不作用于 `#heading(level: N)`,且只接受非负值。
8. `导入` 的 `路径` 以 `--root`(项目根)为基准,且只能加深层级;被导入文件需自行 `#import`,
   并写得比目标层级浅一档(目标 `===` 则源文件写 `==`)。
9. 只要用了 `#元素("xxx")`,就必须把 `xxx` 写进 `附件/元素系统.csv` 的 id 列,否则 PDF 告警、
   网页显示「未定义」。
