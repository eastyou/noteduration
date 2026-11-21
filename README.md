# noteduration

[![CI](https://github.com/eastyou/noteduration/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/noteduration/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

音符时值与小节补全练习：从全音符到十六分音符，支持附点与 4/4、3/4、6/8 等拍号。

## 特性

- 五种基本音符时值，附点自动乘 1.5
- 拍号统一换算成四分音符拍数，6/8 与 2/2 都正确
- 题目给出不完整小节，问“还差几拍”，答案可用整数或分数
- SVG 手绘音符：空心/实心符头、符干、符尾与附点
- 练习纸附带音符时值对照表，答案单独分页
- 纯标准库，零依赖，跨平台

## 安装

```bash
python -m pip install -e .
```

## 用法

```bash
noteduration notes
noteduration note "dotted half"
noteduration sheet --signature 4/4 --count 8 --seed 3 --answers -o sheet.html
noteduration sheet --signature 6/8 --count 6 --seed 3 -o six-eight.html
```

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `--signature` | 拍号，例如 `4/4`、`3/4`、`6/8` | `4/4` |
| `--count` | 题目数量 | 8 |
| `--seed` | 随机种子 | 无 |
| `--answers` | 追加答案页 | 关闭 |

## 时值表

| 音符 | 拍数（4/4） |
| --- | --- |
| 全音符 | 4 |
| 二分音符 | 2 |
| 四分音符 | 1 |
| 八分音符 | 0.5 |
| 十六分音符 | 0.25 |

## 示例

[examples/noteduration.html](examples/noteduration.html) 是 8 道 4/4 拍补全题，带答案页。

## 测试

```bash
python -m unittest discover -s tests -v
```

## 协议

MIT © 2026 eastyou
