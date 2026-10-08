// 文档入口:编译本文件即得完整文档(PDF 或 HTML)。
// 正文分文件放在 内容/ 下,标题层级直接用 = / == …,由 #include 合并进来。
// 各章自带 #import "…/配置.typ": *(模板成员经它再导出)。
// / Entry point: compile this file for the whole document. Chapters live in
// separate files under 内容/ and are merged with #include.
#import "../配置.typ": *

#show: 网页模板.with(页脚链接: 站点链接("/index.pdf"))

#outline(title: "目录")

#include "自新世界/我见青山多妩媚.typ"
#include "?原作者没起名字/雾隐青麟.typ"
#include "?原作者没起名字/神龙藏深泉-猛兽步高冈.typ"
#include "?原作者没起名字/广阔天地-大有作为.typ"
