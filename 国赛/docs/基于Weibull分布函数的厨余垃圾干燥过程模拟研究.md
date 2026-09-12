# 转换失败记录：基于Weibull分布函数的厨余垃圾干燥过程模拟研究.pdf

**结论：`mcp__markitdown__convert_to_markdown` 对该 PDF 返回**零字节**（空结果），尝试 2 次均如此。**
因此本次未能从文档本身提取任何题录信息，**不填写任何推测字段**。

- 源文件：`docs/基于Weibull分布函数的厨余垃圾干燥过程模拟研究.pdf`（2 499 527 字节，未改动）
- 转换调用：
  - `mcp__markitdown__convert_to_markdown(uri="file:///D:/github/myself/Mathematical_Modeing/国赛/docs/基于Weibull分布函数的厨余垃圾干燥过程模拟研究.pdf")` → 第 1 次：空；第 2 次：空
- 本文件是那次失败转换的派生记录（因为没有任何 Markdown 内容可保存）。

## 这不是「纯扫描件」，但确实取不到文字

对 PDF 原始字节的探测（PowerShell `[System.IO.File]::ReadAllBytes` + 正则计数，命令见下）：

| 标记 | 次数 | 含义 |
|---|---|---|
| `%PDF` | 1 | PDF 1.4，文件头为 `%PDF-1.4` |
| `obj` | 146 | 146 个间接对象 |
| `/Type /Page` | 9 | 至少 9 页 |
| `/Contents` | 8 | 8 条内容流 |
| `/Encrypt` | **0** | **未加密**（排除「加密导致读不出」这一解释） |
| `/Font` | 78 | 有字体资源 |
| `/Type0` | 10 | 复合（CID）字体，10 处 |
| `/FontFile` | 10 | 10 个字体文件被嵌入 |
| `/Encoding` | 10 | 10 处编码字典（按计数推断为 `Identity-H` 一类） |
| `/ToUnicode` | 10 | 10 处 ToUnicode 映射 |
| `/Image` | 8 | 8 个图像 XObject |
| `BT` | 43 | 43 个「开始文本」算符 → **存在真实文本层** |
| `/TrueType`、`/Type1`、`/Type3` | 0 | 非简单字体 |

复现命令（在仓库根目录执行）：

```powershell
$f="docs\基于Weibull分布函数的厨余垃圾干燥过程模拟研究.pdf"
$b=[System.IO.File]::ReadAllBytes((Resolve-Path $f))
$s=[System.Text.Encoding]::ASCII.GetString($b)
foreach($m in @('/Encrypt','/Type0','/TrueType','/Type1','/Type3','/FontFile','/ToUnicode','/Image','BT')){ "{0,-12} {1}" -f $m,([regex]::Matches($s,[regex]::Escape($m))).Count }
```

## 由此可知与不可知

- **可知**：文件未加密；含有 9 页、嵌入 CID 字体与 ToUnicode 映射、并有 43 处文本算符。
  所以「抽不出中文」的原因不是扫描件、也不是加密，而是抽取器（MarkItDown 内部为 pdfminer.six）
  在这份文件上**没有产出任何文本**——具体成因为何，本环境无法进一步定位。
- **不可知**：题名、作者、期刊名、年卷期页、DOI/文章编号**一律未能从文档本身读到**。
  按任务要求，7 篇汇总表中这一行全部记「未找到」。
- **被拒绝的做法**：不从文件名（"基于Weibull分布函数的厨余垃圾干燥过程模拟研究"）反推题名与作者，
  不引用任何外部数据库记录充当「文档本身」的证据。

## 本环境下的能力边界（供后续会话参考）

本会话为受限子代理，**Python 被沙箱拒绝执行**（`python --version` → `Program 'python.exe' failed to run: Access is denied`，
并伴随 `[sandbox: file access denied under workspace-write mode]`），且**审批提示被禁用**，无法提权。
因此 `liteparse` 等本地 OCR/解析工具（需要 Python）在本会话不可用。
若需拿到该文的题录，应在有 Python/OCR 的环境中重新转换，或改用可访问该文献的外部记录（并明确标注为外部来源）。
