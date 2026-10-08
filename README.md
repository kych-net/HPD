# UHEg

基于地狱之下模板（UnderHell Template）整理的项目模板仓库，用于快速创建设定集/冒险/规则文档项目。

## 项目结构

- `配置.typ` —— 站点配置：标题、作者、品牌名、元素系统数据
- `Makefile` —— 编译命令（`pdf` / `web` / `watch` / `clean`）
- `内容/` —— 分章正文，每个 `.typ` 都会编译出一份文档；`index.typ` 是入口
- `脚本/` —— 独立页入口 `页面.typ` 与网页后处理 `web_post.sh`
- `附件/` —— 元素系统数据 `元素系统.csv`
- `图片/` —— 图片素材，已配置 Git LFS（见 `.gitattributes`）
- `.webfonts/` —— 自托管网页字体目录（`.` 开头，默认隐藏），默认只有说明文件；字体由使用者自行放入（见 `.webfonts/README.md`）
- `SKILL.md` —— AI 写作与编译规范（技能说明）
- `.github/workflows/web.yml` —— 已启用的网页构建与发布工作流
- `LICENSE` —— 许可证，创建项目后请改成你的名字
- `README.md` —— 本文件，同时被 `内容/关于.typ` 渲染进正文

## 快速开始

```sh
make pdf    # 内容/ 下全部 .typ → PDF（逐页套用模板）
make web    # 多页站点：各页共用一份 CSS，跨页元素连成链接
make watch  # 监听入口，自动重编
```

## 创建项目后清单

- [ ] 检查最新版本[地狱之下](https://typst.app/universe/package/underhell),我有可能忘了更新
- [ ] 修改 `配置.typ` 中的标题、副标题、作者、品牌名等项目信息
- [ ] 按需要增删 `内容/` 下章节，并在 `内容/index.typ` 调整 `#include`
- [ ] 替换 `附件/元素系统.csv` 为你的项目素材
- [ ] 需要自托管网页字体时，把四个 `.woff2` 放进 `.webfonts/`（见 `.webfonts/README.md`）
- [ ] 按需修改或者禁用`配置.typ` 中的 `导航`
- [ ] 在仓库 Settings → Actions 中确认允许工作流运行
- [ ] 推送到 `main` 触发 `.github/workflows/web.yml`，确认 `web` 分支产物更新
- [ ] 在托管平台绑定 `web` 分支并关闭平台侧构建
- [ ] 把 `LICENSE` 中版权改成你的名字

## 元素系统

同一概念在不同系统下叫不同名字：

| 元素 | 普通 | 别名 | 学术 |
| --- | --- | --- | --- |
| 古龙 | 龙 | 龙 | 古代龙 |
| 巨人 | 巨人 | 石头人 | 巨怪 |

## 字体

网页的自托管字体放在 `.webfonts/`（`.` 开头，默认隐藏），默认不含字体文件（模板仓库不便用
Git LFS 托管大字体）。需要时按 `.webfonts/README.md` 放入四个 `.woff2`，`make web` 会把它们
拷到产物的 `dist/webfonts/`，CI 再按用字子集化；没放字体也能正常构建，只是网页回退到系统字体。

## 注意

- 引用概念用 `#元素[古龙]`，取词见 [元素系统](#元素系统)

> 本仓库也包含「导入 Markdown」示例：
> `内容/关于.typ` 会把这个 `README.md` 渲染进文档。

详见 <https://typst.app/docs/>。

## 部署网页

`make web` 产出的 `dist/` 是纯静态站点，可直接托管。仓库已内置并启用 GitHub Actions
工作流 `.github/workflows/web.yml`：推送 `main` 后会把产物强制推到 `web` 分支；然后
在托管平台绑定 `web` 分支并关闭平台构建即可。

### Cloudflare Pages

1. 进入 Cloudflare 控制台 → **Workers & Pages** → **创建** → **Pages** → **连接到 Git**，授权并选择本仓库。
2. **生产分支** 选 `web`（即工作流产出的静态分支）。
3. 构建设置保持不构建：
   - 框架预设：`None`
   - 构建命令：留空
   - 构建输出目录：`/`
4. 保存并部署。之后每次推送 `main`，工作流更新 `web` 分支，Cloudflare 会自动重新部署。
5. 在 **自定义域** 中绑定自己的域名即可。

### EdgeOne Pages

1. 进入 [腾讯云 EdgeOne 控制台](https://console.cloud.tencent.com/edgeone/pages) → **创建项目** → **导入 Git 仓库**，授权 GitHub 并选择本仓库。
2. **生产分支** 选 `web`。
3. 构建设置保持不构建：
   - 框架预设：其他 / 无
   - 构建命令：留空
   - 输出目录：`/`（根目录）
4. 点击 **开始部署**。之后推送 `main` 触发工作流更新 `web` 分支，EdgeOne 会自动重新部署。
5. 在 **域名管理** 中绑定自定义域名（关联大陆加速区域需完成备案）。
