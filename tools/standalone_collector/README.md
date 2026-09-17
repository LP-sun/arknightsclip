# 明日方舟干员仓库独立采集工具包 (Operbox Standalone Collector)

这是一个专门设计用于**单独打包分发**的轻量化数据采集工具包。  
玩家电脑上**无需克隆本项目，无需安装 PyTorch / EasyOCR / OpenCV 等复杂环境**，仅需基础 Python 3 即可一键运行并打包干员仓库素材。

---

## 📐 架构职责边界 (Architectural Boundary)

* **`tools/standalone_collector` = 便携式采集前端 (Capture Frontend Only)**
  * **职责单一**：仅负责 ADB 设备探测、分辨率自适应、无依赖截屏、滑动手势控制、MD5 重复画面停止检测与 ZIP 压缩打包。
  * **零第三方依赖**：纯 Python 标准库实现。严禁在 collector 内引入 EasyOCR、OpenCV、OperatorRegistry 或第二套干员识别/切片逻辑。
* **`src/arknightsclip/maa/operbox_analyzer.py` = 权威识别与规范化核心 (Canonical Recognizer / Normalizer)**
  * **全功能解析**：负责接收导入的截图页，执行 720p 锚点对齐、名字条 2x 双三次插值超分、EasyOCR 识别、字形纠错、消歧、多候选择优、卡片裁切与 SceneManifest 生成。

---

## 📦 工具包包含文件

```text
tools/standalone_collector/
├── collector.py          # 纯 Python 标准库采集脚本 (零第三方依赖)
├── start_collector.bat   # Windows 一键启动批处理
├── start_collector.ps1   # PowerShell 启动脚本
└── README.md             # 本说明文档
```

> **可选自带 adb**：如果分发对象电脑未安装任何模拟器且没有 ADB，可以在本目录下直接放入官方 `adb.exe` + `AdbWinApi.dll` + `AdbWinUsbApi.dll`，脚本会自动优先使用当前目录下的 ADB。

---

## 🎮 玩家使用指南（发送给协助采集的小伙伴）

### 第一步：游戏内准备
1. 打开电脑上的安卓模拟器（推荐 **MuMu 模拟器 12** 或 **雷电模拟器 9**）。
2. 启动《明日方舟》并登录游戏。
3. 点击主界面下方的【干员】，进入干员仓库。
4. **重要设置**：
   - 界面右上角排序点击切换为 **【稀有度】**（6 星干员排在最前）。
   - 将干员列表手动滑到 **【最左侧第一页】**。

### 第二步：运行采集工具
- **双击运行 `start_collector.bat`**。
- 按控制台提示输入您的**昵称或代号**（例如：`wyf`、`P2`、`老王` 等）。
- 脚本会自动检测并连接模拟器（支持 MuMu、雷电、夜神、逍遥等主流模拟器）。
- 连接成功后，工具将**全自动截屏并自动翻页**，并在检测到到达仓库末尾时自动停止。

### 第三步：发送生成的文件
- 采集完成后，工具会在同级目录自动生成一个形如 `Arknights_Operbox_<昵称>_<时间>.zip` 的压缩包。
- 窗口会自动在文件资源管理器中高亮显示该 ZIP 压缩包。
- **直接将该 ZIP 压缩包发送给视频制作者 / 项目维护者即可！**

---

## 🛠️ 项目维护者导入指南（接收数据后）

当项目维护者收到玩家传回的 ZIP 压缩包后：

1. 将压缩包解压或直接将内部的 `pages/` 目录放置到目标玩家目录，例如：
   ```text
   data/raw/P2/operbox/pages/
   ```
2. 运行工程自带的离线重放命令进行 OCR 识别与卡片精细切片：
   ```powershell
   python -m arknightsclip replay-operbox data/raw/P2/operbox/pages --player P2
   ```
   > 系统将自动进行 16:9 视口适配、MAA 720p 锚点检测、MAA 级字形纠错与干员卡片自动裁剪落盘。

---

## ⚙️ 常见问题排查 (FAQ)

1. **提示“未在您的电脑上检测到 Python 环境”？**
   - 前往 [Python 官网](https://www.python.org/downloads/) 安装 Python，安装界面务必勾选底部 `Add python.exe to PATH`。
2. **提示“未能连接到模拟器设备”？**
   - 确认模拟器已开启并在运行《明日方舟》。
   - 检查模拟器设置中是否开启了 ADB 调试：
     - MuMu 12：设置中心 -> 问题诊断 -> ADB调试（端口通常为 `127.0.0.1:16384`）。
     - 雷电 9：软件设置 -> 其他设置 -> ADB调试开启本地连接（端口通常为 `127.0.0.1:5555`）。
   - 在控制台中根据提示直接手动输入端口地址。
