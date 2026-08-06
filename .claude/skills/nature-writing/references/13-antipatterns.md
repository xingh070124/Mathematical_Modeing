# 13 · 反模式

（v4 SKILL Part XII：craft + AI-specific + taste 反模式；总索引见 `../SKILL.md`）

## 15. AI 论文常见反模式

### 15.1 Craft 反模式

1. **Abstract 写成 Methods 摘要**  
   堆 architecture，没有 headline result。

2. **Intro 从 AI hype 开始**  
   "Recently, deep learning…" 是无 antagonist 的开头。

3. **GAP 只说 existing methods are limited**  
   不说 limited by what。

4. **Results 标题全部 task-neutral**  
   读者扫不出结论。

5. **Discussion 第一段 limitation-first**  
   除非你故意采用 RetroExplainer 那种 frank concession，否则容易显得主 claim 弱。

6. **Closing 写 future work list**  
   换成 boundary + outlook。

7. **空心化 novel**  
   "A novel method…" 没有信息。

8. **To the best of our knowledge 用三次以上**  
   一篇最多一次，且只在 first / largest / first demonstration 真需要时用。

### 15.2 AI-specific 反模式

9. **单 seed 单 run 报 SOTA**

10. **Cherry-picked benchmark / metric**

11. **Compute cost 不报告**

12. **Baseline 不公平**

13. **Data leakage 不查**

14. **Foundation model 论文只有一个下游任务**

15. **Closed-source API 论文不报 prompt / version / date**

16. **LLM-as-judge 无 expert / rule-based sanity check**

17. **没有公开 code / weights，却写 democratizes**

18. **Interpretability 论文只有 saliency map**

19. **Clinical AI 无外部验证却写 clinical-grade**

20. **Discovery 论文无实验闭环却写 discovery**

21. **SI black hole**（v5 新加）  
   主文声称 "reproducible" / "agentic" / "API-based" / "deployed"，但 SI 缺 prompt、API 精确版本、access date、decoding params、retry policy 或 tool schema。Reviewer 一查 SI 发现"该有的都没有"——属于诚信问题，不是格式问题。修法：主文显式指向 SI 的具体 section，且 SI 真的有完整内容。详见 `references/06-methods.md` §6.2 主文/SI 分工。

22. **Law-title without law evidence**（v5 新加）  
   标题 / abstract 用 "scaling law" / "X law" / "unlock" / "general scale" 等强词，但实际只在 1–2 个 model family、1 个时间点、有限任务集上验证。不构成 law。修法：要么改弱（"a metric for…"），要么补跨模型 / 跨时间 / 跨任务的趋势证据。

### 15.3 Taste 反模式

21. **所有实验同等重量**  
   没有 climax，像项目报告。

22. **Fig. 1 是零件清单**  
   读者看完不知道故事。

23. **形容词堆叠**  
   powerful / robust / novel / efficient / general 一起出现，通常说明 noun 没写准。

24. **每段都 "Furthermore"**  
   连接词变成机械推进。

25. **最强结果配最吵句子**  
   有时最强结果需要最安静的句子。

26. **过度防御**  
   每个 claim 后面都加 caveat，读者会觉得你也不信。

27. **过度营销**  
   没有 boundary，reviewer 会替你写 boundary。

28. **把 reviewer 的问题留给 reviewer**  
   你不主动处理，审稿意见会更重。

---

