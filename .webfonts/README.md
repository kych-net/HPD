# .webfonts

自托管网页字体的放置目录。**本目录默认不含字体文件**——模板仓库不便用 Git LFS 托管大字体,
字体由使用者自行放入。没放字体也能正常构建,网页会回退到系统字体。

目录名以 `.` 开头,在文件管理器中默认隐藏,避免干扰正文;它与产物里的 `dist/webfonts/`
**不同名**:源目录是 `.webfonts/`,网页上对外访问的路径仍是 `/webfonts/…`(由模板包的
`languages/zh.toml` 固定,不要改产物目录名)。

## 需要哪些文件

模板包 `@preview/underhell` 的语言配置(`languages/zh.toml`)的 `[web]` 段引用了下面四个
`.woff2`。**文件名固定**,缺一个即对应字族回退到系统字体:

| 文件 | 字族 | 用途 |
|------|------|------|
| `lxgw-wenkai-mono.woff2` | `uh-lxgw-mono` | 正文 |
| `duan-kaixiao-full.woff2` | `duan-kaixiao` | 标题 |
| `zhenkai-gb.woff2` | `uh-zhenkai` | 粗体 |
| `zhaoji-shoujin.woff2` | `zhaoji-shoujin` | 评论 |

## 怎么用

1. 把四个 `.woff2` 放进本目录(`.webfonts/`)。
2. `make web` 会把 `.webfonts/*.woff2` 拷到 `dist/webfonts/`;本目录没有字体时自动跳过,
   不影响构建。
3. 推送到 `main` 后,`.github/workflows/web.yml` 会在有字体时按页面实际用字做子集化,
   再把产物推到 `web` 分支。

## 字体从哪来

这四个文件取自地狱之下模板仓库 `kych-net/UnderHellTemplate` 的 `webfonts/` 目录。该仓库用
Git LFS 托管,取用前需装 `git lfs` 并 `git lfs pull`。

## 关于 Git LFS

模板仓库不启用 LFS(克隆/模板场景下容易拿到指针文件)。若你的项目要长期托管这些大字体,
可在**你自己的仓库**里自行配置:

```sh
git lfs install
git lfs track ".webfonts/*.woff2"
git add .gitattributes .webfonts/*.woff2
```

不想把字体提交进 git,也可以只放在本地编译时使用;但这样 CI 构建出的网页不会有字体。
