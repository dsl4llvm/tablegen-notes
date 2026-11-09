# figs

文章里的示意图（手写 SVG，用 cairosvg 渲染成 2000 px PNG）。

| 文件 | 用在哪篇 | 画的是什么 |
|---|---|---|
| `corpus-by-ecosystem` | 《91 万行 .td》§0 | 三家语料的份额，条长按行数 |
| `dsl-three-layers` | 《如何设计一门 DSL》§1 | 三层各自的产物/主人/出错症状，以及「动几张表」 |
| `tablegen-four-layers` | 《一台什么都不做的机器》§2 | 文本 → AST → 记录图 ‖ 领域语义，语义从第 4 格开始 |
| `recordkind-tables` | 《元层没有固化》§2 | 同名 `TB` 在两张表里各一条，`:` 只查 Classes |
| `ternary-52-lines` | 《写死的 parser》§4 | 52 行补丁逐行摊开：17 行语法，35 行不是 |
| `escape-hatch-density` | 《逃生舱经济学》§0 | 两个子系统的 `code` / `dag` 密度，共用一条轴 |
| `two-backends-signature` | 《两个后端，一份真相》§0 | 一份 `.td` → 三个后端 → 归一化成一个签名 |
| `three-exits` | 《同一种架构，三个切点》§0 | 同一个三段式，三种交接物 |
| `ninety-six-account` | 《那 96 个手写》§4 | 4,473 行切成 1,962 块，4,647 行切成 94 块 |

重新渲染：

```bash
python3 -c "import cairosvg,sys; cairosvg.svg2png(url=sys.argv[1], write_to=sys.argv[2], output_width=2000, background_color='#F8FAFC')" \
  figs/three-exits.svg figs/three-exits.png
```

字号按 1000 px 画布定，最小组件 13 px；知乎正文栏约 690 px，缩到那里仍可读。
