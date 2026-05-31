# Voice Calendar Tool

一个基于 Python 的语音日历工具，支持中文自然语言指令、SQLite 本地存储、语音输入、语音播报、到点提醒，以及类似日历看板的多日程视图。

项目目标是让用户用更自然的方式管理日程：可以输入或说出“明天下午三点提醒我开组会”“6月4号9点提醒我上课”等中文指令，系统会自动解析时间和事件标题，并在日历界面中展示。
<img width="1494" height="926" alt="image" src="https://github.com/user-attachments/assets/acd1275a-6446-48d8-b9be-05bd7385aff5" />

演示视频链接：https://www.bilibili.com/video/BV1fHVn6dEtb/?spm_id_from=333.1387.upload.video_card.click&vd_source=d221f9bd167a0dc8486fba6449e8fc6d
## 功能亮点

- 中文自然语言日程解析
- 文字指令添加、查询、删除日程
- 麦克风语音输入，识别后可自动执行指令
- pyttsx3 本地语音播报反馈
- SQLite 本地持久化存储
- 程序启动后自动开启后台提醒扫描
- 到期日程支持弹窗提醒、状态栏提示和语音播报
- 三栏式桌面 GUI
- 左侧“全部提醒”列表，按时间从前到后排序
- 中间 Canvas 日程时间轴，支持单日和最多 7 天范围视图
- 右侧小日历支持选择起始日期和结束日期，再点击 `Apply` 应用范围
- 点击日程卡片可查看详情，并支持在详情弹窗中删除该日程
- 旧版数据库自动迁移，不需要手动删除本地数据库

## 技术栈

- Python 3.10+
- Tkinter
- SQLite
- speech_recognition
- PyAudio
- pyttsx3
- unittest

## 项目结构

```text
Voice_Calendar_Tool/
├── main.py
├── requirements.txt
├── README.md
├── src/
│   ├── app.py
│   ├── config.py
│   ├── database/
│   │   ├── db.py
│   │   └── event_repository.py
│   ├── models/
│   │   └── event.py
│   ├── services/
│   │   ├── calendar_service.py
│   │   ├── command_parser.py
│   │   ├── reminder_service.py
│   │   ├── speech_service.py
│   │   └── tts_service.py
│   └── ui/
│       └── main_window.py
└── tests/
    ├── test_calendar_service.py
    └── test_command_parser.py
```

## 安装依赖

建议先创建并进入虚拟环境：

```bash
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

安装依赖：

```bash
python -m pip install -r requirements.txt
```

当前依赖：

```text
SpeechRecognition
pyttsx3
PyAudio
```

如果 Windows 上安装 `PyAudio` 失败，可以先尝试：

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install PyAudio
```

如果使用 Anaconda 或 Miniconda，推荐：

```bash
conda install -c conda-forge pyaudio
```

如果暂时无法安装 `PyAudio`，文字指令、日历展示、SQLite 存储和提醒功能仍然可以使用，语音输入会提示麦克风或依赖不可用。

## 运行项目

```bash
python main.py
```

启动后会打开桌面日历窗口，并自动启动后台提醒服务。

## 使用方式

### 文字指令

在右侧“文字指令”输入框中输入自然语言日程指令，然后点击执行。

示例：

```text
添加今天 15:00 开会
明天下午三点提醒我开组会
今天晚上八点写论文
6月4号9点提醒我上课
查看今天的日程
明天有什么日程
本周有什么计划
删除开会
删除明天下午三点的会议
```

### 语音输入

点击右侧“语音输入”按钮后，对麦克风说出日程指令。识别成功后，文本会自动填入输入框；如果勾选“识别后自动执行”，系统会立即解析并执行该指令。

### 日历范围选择

右侧小日历支持类似范围选择的交互：

1. 点击一个日期作为起始日期。
2. 点击另一个日期作为结束日期。
3. 点击 `Apply` 应用范围。
4. 点击 `Cancel` 取消当前待选择范围。

最多支持连续 7 天。只选择一个日期时，中间区域显示单日视图。

### 中间日程视图

中间区域使用 Canvas 绘制时间轴，时间范围固定为每日 `06:00` 到次日 `06:00`。

刻度包括：

```text
06:00
08:00
10:00
12:00
14:00
16:00
18:00
20:00
22:00
00:00
02:00
04:00
06:00
```

单日视图显示一列，多日视图显示多列。每列对应一天，日程卡片会根据事件时间绘制到对应位置。

### 日程详情和删除

点击中间日程卡片后，会弹出日程详情窗口，展示：

- 标题
- 时间
- 距离今天还有多少天
- 是否已提醒

详情窗口中提供“删除”按钮，可以精确删除当前选中的日程。

## 提醒功能

程序启动后会自动运行提醒线程：

- 每 30 秒检查一次数据库
- 如果事件时间小于等于当前时间，且尚未提醒，会触发提醒
- 提醒方式包括 GUI 弹窗、状态栏提示和语音播报
- 提醒后会将该事件标记为已提醒，避免重复提醒
- 程序关闭时提醒线程会安全退出

测试提醒示例：

```text
添加今天 14:31 测试提醒
```

等待到点后，程序会在 30 秒扫描周期内触发提醒。也可以添加一个已经过去的时间，快速验证提醒逻辑。

## 数据库说明

本地数据存储在：

```text
data/calendar.db
```


程序启动时会自动检查数据库结构：

- 如果缺少 `notes` 字段，会自动补充
- 如果缺少 `reminded` 字段，会自动补充

因此旧版数据库可以平滑升级，不需要手动删除。

## 运行测试

```bash
python -m unittest discover -s tests
```

当前测试覆盖：

- 中文添加指令解析
- 中文查询指令解析
- 中文删除指令解析
- 日期、时间边界解析
- SQLite 日程增删查
- 06:00 到次日 06:00 的单日窗口
- 最多 7 天范围视图查询
- 到期未提醒事件查询和提醒标记
- 旧数据库字段迁移

## 当前限制

- 日期范围选择采用“点击起始日期 + 点击结束日期 + Apply”，暂未实现拖拽选择
- 最多显示连续 7 天
- 7 天视图在较窄窗口下每列会比较紧凑
- 日程支持删除，但暂不支持编辑
- 提醒只支持一次性到点提醒，不支持提前提醒和重复日程
- 语音识别基于 `speech_recognition`，默认使用 Google Web Speech 接口，识别时需要网络连接
- 提醒扫描间隔为 30 秒，因此提醒可能存在几十秒延迟

## 后续计划

- 支持编辑日程
- 支持提前提醒
- 支持重复日程
- 优化 7 天视图下的横向展示体验
