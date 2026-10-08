// 站点配置:模板成员再导出 + 网页模板。
// 各章只写 #import "../配置.typ": *(模板成员经它再导出),不直接引 lib.typ。
// / Site config: re-exports the template and defines the web template.
// Chapters only write #import "../配置.typ": * — the template is re-exported here.

#import "@preview/underhell:1.0.0": *

// 重定义 导入:模板包里的同名函数用 include "/" + 路径,但包内文件的 "/" 以*包根*
// 为基准(Typst 沙箱),会去包缓存里找本项目文件而报错。改在项目内定义,"/" 即以
// --root 为基准,调用处照旧写仓库根相对路径(如 "内容/地理/主行星.typ")。
#let 导入(路径, 偏移: 1) = {
  set heading(offset: 偏移)
  include "/" + 路径
}

// 元素系统数据:宽表 CSV,首列是元素 id,其后每列是一个元素系统,
// 单元格为该元素在对应系统下的名词(留空则回退)。列名可自行增删。
// / Element-system data: wide CSV, first column = element id, each further
// column = one element system; empty cells fall back.
#let 元素数据 = csv("附件/元素系统.csv")

// 网页模板:入口 内容/index.typ 用 #show 套用。
// 封面/logo 走模板默认;要加图就把图片放进本项目,再 cover: image("…") / logo: image("…")。
// / Web template: applied by the entry point via #show.
#let 网页模板 = 地狱之下模板.with(
  title: "我的设定集",
  subtitle: "一个崭新的世界",
  author: "你的名字",
  lang: "zh",
  paper: "a4",
  品牌名: "我的世界",
  备案号: "",
  元素系统数据: 元素数据,
)

// 网页右上角导航(模板的 页脚链接: 参数):PDF 一项指向本页同名 .pdf(如 /概述.pdf),
// 其余为仓库外链。传入本页 PDF 的站点路径——各独立页由 脚本/页面.typ 按自身路径算出,
// 入口页 内容/index.typ 传 "/index.pdf"。
// / Site nav (页脚链接:): the PDF entry points at this page's own .pdf.
#let 站点链接(本页PDF) = (
  (标签: "PDF", 网址: 本页PDF, 提示: "下载本页 PDF"),
  (标签: "GitHub", 网址: "https://github.com/kych-net/UHEg", 提示: "GitHub 仓库"),
  (标签: "GitCode", 网址: "https://gitcode.com/CrossDark/UHEg", 提示: "GitCode 仓库"),
)

#let 导航 = (
  ("示例", "示例"),
  ("关于", "关于"),
  ("概述", "概述")
)
