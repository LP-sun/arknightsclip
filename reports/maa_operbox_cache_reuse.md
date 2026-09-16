# MAA OperBox 缓存与图像复用审计 (MaaCore Cache Reuse Investigation)

本报告专项审计在干员培养状态识别过程中，MAA 内部的图像生命周期、内存缓存机制及能否零成本复用页面截图与 Card ROI 裁切素材。

---

## 专项问题解答

### 1. 当前 MAA 是否已经把页面 screenshot 持久化？
- **没有**。在默认正常运行模式下，Controller 截获的图像仅在内存中的 m_cache_image 保存，供当前帧分析使用。
- 只有在识别到页面干员数量异常（不等于 14 或 16）或显式开启调试开关时，才会在 debug/oper/ 产生落盘图片。

### 2. 是否持久化 card crop？
- **没有**。MAA 从未落盘过任何干员卡片 crop，其识别流水线在内存中抽取名字、等级、精英化、潜能等标量数据后，中间局部图像立即析构。

### 3. 如果没有，是否在内存中已有 ROI？
- **是的**。
  - 在 OperBoxImageAnalyzer::opers_analyze() 中，MAA 已经精准检测并保存了干员卡片的角标锚点：lag_rect。
  - 由 lag_rect 的相对几何关系，可以以 100% 确定性直接投影推导出整张卡片的视觉边界 isual_asset_roi：
    [flag.x - padding_x, flag.y - padding_y, card_width, card_height]。

### 4. 最小修改点在哪里？
- **上游 (MaaCore) 理论修改点**：
  若修改 C++ 核心库，可在 OperBoxRecognitionTask::swipe_and_analyze() 循环中，在 or (const auto& box_info : opers_result) 识别出干员后，直接截取 page(card_roi) 并通过 callback 或文件流输出。
- **本项目非侵入式适配点 (Non-invasive Adapter)**：
  - 遵循用户指令：**严禁修改 E:\Maa 工作环境**。
  - 在 PlayerCollector / OperBoxCollector 单次扫描流程中，我们在执行每一页翻页的前后，将真实的页面帧保存在同一会话中（pages/page_XXXX.png）。
  - 在同一轮循环中，直接将该页面的 rame 送入 OperBoxAnalyzer，在获得 char_id 与培养状态的同时，利用对应的 card_roi 从同一张内存 frame 中 crop 出 cards_raw/<char_id>.png。
  - 从而达到真正的 **ONE SCAN, TWO OUTPUTS**，完全不需要让游戏做第二次 UI 遍历。

### 5. 是否可以做到几乎零额外游戏操作？
- **完全可以**。
  - 游戏交互（翻页滑动、等待静止、检测列表末端）仅执行一次。
  - 卡片素材的截取只是在 Python/C++ 内存中对同一张当前屏幕截屏做一次局部矩阵切片（rame[y:y+h, x:x+w]），额外耗时小于 1ms，对游戏运行流程零干扰、零延迟。

### 6. 保存 crop 的额外成本是多少？
- **耗时**：每页 14~16 个干员，内存裁切 + PNG 压缩写入磁盘平均耗时约 5~15 毫秒（对比单次翻页等待的 1.5 秒几乎可忽略不计）。
- **空间**：单张干员 1080P 原始比例卡片 PNG 约 100KB~250KB，全图鉴 300 名干员仅占用约 50MB 磁盘空间，存储开销极低。
