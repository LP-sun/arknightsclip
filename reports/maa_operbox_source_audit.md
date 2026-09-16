# MAA OperBox 源码审计报告 (MaaCore OperBox Source Audit)

- 审计对象：MaaAssistantArknights/MaaAssistantArknights (branch dev-v2, Commit 7e5de9b) 与本地 E:\Maa 运行时
- 核心文件：
  - src/MaaCore/Task/Interface/OperBoxTask.cpp
  - src/MaaCore/Task/Miscellaneous/OperBoxRecognitionTask.cpp / .h
  - src/MaaCore/Vision/Oper/OperBoxImageAnalyzer.cpp / .h
  - src/MaaCore/Vision/VisionHelper.cpp / .h
  - src/MaaCore/Controller/Controller.cpp / .h
  - resource/tasks/tasks.json
  - resource/battle_data.json

---

## 审计问题逐一解答

### 1. 官方 OperBox task 的入口是什么？
- Interface Task 入口：asst::OperBoxTask (TaskType = 'OperBox')。
- 任务链流程：
  1. enter_task: 运行 OperBoxBegin 流程（处理从大厅导航、展开角色筛选等）。
  2. recognition_task: 运行 OperBoxRecognitionTask（负责循环截屏、分析卡片并向右平滑滑动翻页）。

### 2. Core 层真正负责识别的类/函数是什么？
- 任务驱动层：asst::OperBoxRecognitionTask::swipe_and_analyze()。
- 图像视觉分析核心类：asst::OperBoxImageAnalyzer (Vision/Oper/OperBoxImageAnalyzer.h)。
- 核心入口方法：OperBoxImageAnalyzer::analyze()，其内部按序执行：
  - opers_analyze(): 识别职业角标与干员名字 OCR。
  - level_analyze(): 识别等级数字。
  - elite_analyze(): 识别精英度 (Elite 0/1/2)。
  - potential_analyze(): 识别潜能 (Potential 1..6)。

### 3. 每一页什么时候截图？
- 在 OperBoxRecognitionTask::swipe_and_analyze() 的 while (!need_exit()) 循环最开头调用：
  OperBoxImageAnalyzer analyzer(ctrler()->get_image());
  auto future = std::async(std::launch::async, [&]() { swipe_page(); });
- 每次滑动前，通过 ctrler()->get_image() 抓取当前静止页面，随后立即异步发起向右滑动 swipe_page() (OperBoxSlowlySwipeToTheRight)，与当前帧分析并发执行。

### 4. screenshot 以什么对象存在？
- 在 Controller 层以 cv::Mat m_cache_image 存在（BGR 格式，尺寸归一化为 1280x720 坐标系，若 raw=true 则为设备原生分辨率）。
- 在 VisionHelper 中保存为 cv::Mat m_image。

### 5. card ROI 在哪里计算？
- 在 OperBoxImageAnalyzer::opers_analyze() 中：
  - 先在 720p 空间下通过两个基准搜索区域查找 9 种职业角标：
    - OperBoxFlagRoleTopROI: [0, 78, 1145, 50]
    - OperBoxFlagRoleBottomROI: [0, 394, 1145, 50]
  - 匹配得到 flag.rect（角标锚点矩形，通常大小约 20x20 到 30x30）。
  - 根据 flag.rect 和配置的偏移量计算各属性区域：
    - 名字 OCR 区域：flag.rect.move([0, 265, 128, 22])
    - 等级 OCR 区域：box.rect.move([5, 230, 37, 23])
    - 精英度匹配区域：box.rect.move([11, 171, 24, 35])
    - 潜能匹配区域：box.rect.move([99, 194, 24, 24])

### 6. ROI 是否在 analyzer 中已经有 crop？
- 子属性有局部子图 crop：
  - make_roi(m_image, flag.rect.move(name_task->rect_move)) 用于名字分析。
  - 等级、精英度、潜能分析器也是直接对 m_image 传入 roi 进行局部匹配或裁剪。
- 整张 Card 卡片整体没有独立 crop 对象：MAA 只存储了 box.rect = flag_rect 锚点和识别出的属性标量，并未生成整张卡片的截取图像。

### 7. crop 生命周期多长？
- 局部子图 crop（如名字二值化图、等级图）仅存在于 opers_analyze / level_analyze 函数栈内，函数返回即析构释放。
- 循环单页的整页 m_image 在当前循环迭代结束（analyzer 析构）后释放。

### 8. 是否已经落盘？
- 正常流程下默认不落盘。
- 只有在识别到的干员数不是 14 或 16（判定为可能漏扫或异常）时，才会触发 save_img(utils::path('debug') / utils::path('oper')) 保存为调试文件。

### 9. 是否存在 cache/temp/debug 图片？
- 存在内存缓存 m_cache_image（Controller 内单帧持久，下一帧截图会覆盖）。
- 存在调试输出目录 debug/oper/（仅在数量异常或开启 ASST_DEBUG 编译宏时写入）。

### 10. callback/result 中包含哪些 operator fields？
- 在 OperBoxRecognitionTask::callback_analyze_result(bool done) 中，MAA 发送 AsstMsg::SubTaskExtraInfo，JSON 结构如下：
  - all_opers: 游戏内所有干员列表（含 id, name, rarity, own 布尔值等）。
  - own_opers: 玩家已拥有的干员列表，每个元素包含：id, name, own, elite, level, potential, rarity。

### 11. 是否能取得稳定 char_id？
- 可以。MAA 源码通过 BattleData.get_id(name) 或 BattleData.find_first_oper(role, name)->id 直接返回稳定的游戏内部 ID（如 char_103_angel）。
- 同时在 battle_data.json 中完整维护了 chars 字典映射。

### 12. 当前版本到底能识别哪些培养字段？
- 原生支持：
  - own: 已拥有/未拥有
  - elite: 精英化 0 / 1 / 2（基于模板匹配 OperBoxFlagElite1.png, OperBoxFlagElite2.png）
  - potential: 潜能 1..6（基于模板匹配 OperBoxPotential2.png ~ OperBoxPotential6.png）
  - level: 等级数字（通过 OperBoxLevelOCR 区域 OCR 识别字符串转换为整数）
- 不支持原生识别的字段：技能等级/专精（mainSkillLevel, skills）、模组（equips）。在 MAA 官方 GUI 中，这些字段明确标注仅支持通过一图流 OpenAPI 导入，视觉扫描无法获得。

### 13. 哪些字段是 UI export 层额外处理的？
- 在 MaaWpfGui/Models/OperBoxData.cs 中：
  - mainSkillLevel, skills, equips 是通过第三方 OpenAPI（一图流）合并的，非 MaaCore 视觉产物。
  - 多语言名称（name_en, name_jp, name_kr）是在 callback 生成时从 BattleData 静态表补充的。

### 14. 哪些字段需要新增 recognition？
- 本次任务的核心需求是：干员培养状态 + 干员在仓库列表中的卡片截图素材 (Card Screenshot Asset)。
- 培养状态中的 own, elite, level, potential, rarity, char_id 已经在 MaaCore 的识别闭环中原生具备！
- 真正缺失的是：
  1. 将识别到的 char_id 与该帧截图的实际卡片视觉 ROI（visual_asset_roi）关联。
  2. 将该卡片区域的原始像素裁切并保存为 cards_raw/<char_id>.png。
  3. 过滤屏幕边缘不完整卡片，并在相邻页面重叠时进行最佳截图评选。
