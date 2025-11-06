<img width="1113" height="878" alt="QQ截图20250915181648" src="https://github.com/user-attachments/assets/2ca60107-3e7d-42b3-9286-9ee2957327b2" />

# OSR-VRChat

[English Version](README_EN.md)

一个基于 Python Flask 的 OSR 设备控制程序，实现 OSR 机器人与 VRChat 的实时动作同步。通过 OSC 协议接收 VRChat 的 SPS 插件数据，并转换为 OSR 设备控制指令。

## 项目特性

- 🎮 **VRChat集成**: 通过OSC协议实时接收VRChat中的动作数据
- 🤖 **OSR设备支持**: 支持OSR2/2+设备的串口控制
- 🌐 **Web界面**: 提供直观的Web配置和监控界面
- 📊 **实时监控**: 实时数据图表显示和设备状态监控
- ⚙️ **灵活配置**: 支持多种工作模式和详细参数调节
- 🔧 **设备控制**: 支持手动位置控制和设备测试功能

## 系统要求

- Windows 10/11 (推荐)
- Python 3.8+ (如果从源码运行)
- OSR2/2+设备
- VRChat + SPS插件
- Chrome浏览器 (用于设备测试)

## 快速开始

### 方式一：使用预编译版本 (推荐)

1. 从 [Releases](../../releases) 下载最新的 `.exe` 文件
2. 双击运行程序，首次运行会生成配置文件并退出
3. 编辑生成的 `settings-advanced-v0.1.2.yaml` 配置文件
4. 再次运行程序即可开始使用

### 方式二：从源码运行

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd OSR-VRChat
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行程序**
   ```bash
   python osr_vrchat.py
   ```

## 设备准备

### 1. OSR设备设置

1. 连接OSR2设备到电脑USB端口
2. 打开OSR2电源开关
3. 使用Chrome浏览器打开 [Mosa控制器](https://trymosa.netlify.app/)
4. 选择 "Serial" 并在弹窗中选择对应串口
5. 测试L0轴控制，记录适合的最大值和最小值
6. **重要**: 测试完成后必须关闭网页以释放串口

### 2. VRChat设置

1. 确保VRChat中已开启OSC功能
2. 安装并配置SPS插件
3. 确认模型的吸附功能已正常工作
4. 确保使用的是基于SPS制作的模型 (不支持DPS/TPS)

## 配置说明

程序首次运行会生成 `settings-advanced-v0.1.2.yaml` 配置文件，主要配置项说明：

### OSR设备配置 (`osr2`)

```yaml
osr2:
  com_port: "COM4"              # 串口号，根据设备管理器中的实际端口填写
  objective: "inserted_pussy"    # 工作模式，见下表
  max_pos: 500                  # 最大位置 (0-999)
  min_pos: 1                    # 最小位置 (0-999)
  max_velocity: 2000            # 最大速度 (单位/秒)
  updates_per_second: 50        # 更新频率 (Hz)
  vrchat_max: 700               # VRChat中SPS数据最大值
  vrchat_min: 200               # VRChat中SPS数据最小值
  l0_axis_invert: false         # L0轴反转
```

### 工作模式 (`objective`)

| 模式 | 说明 |
|------|------|
| `inserting_others` | 使用自己的插头插入别人的插座 |
| `inserting_self` | 使用自己的插头插入自己的插座 (测试用) |
| `inserted_ass` | 自己的肛门插座被别人插入 |
| `inserted_pussy` | 自己的小穴插座被别人插入 |

### 网络配置

```yaml
web_server:
  listen_host: "127.0.0.1"      # Web界面监听地址
  listen_port: 8800             # Web界面端口

osc:
  listen_host: "127.0.0.1"      # OSC监听地址
  listen_port: 9001             # OSC监听端口
```

## 使用方法

### 1. 启动程序

运行程序后，会自动：
- 连接OSR设备
- 启动OSC监听服务
- 启动Web服务器
- 进行设备自检

### 2. 访问Web界面

在浏览器中打开 `http://127.0.0.1:8800` 访问控制界面：

- **首页**: 实时数据监控和图表显示
- **配置页面**: 参数配置和设备控制
- **数据页面**: 详细的数据分析

### 3. 设备控制功能

在配置页面中提供以下控制功能：
- **位置控制**: 手动移动设备到最大/最小位置
- **轴反转**: L0轴方向反转开关
- **参数调节**: 实时调整各项参数
- **设备状态**: 查看连接状态和运行信息

### 4. 数据校准

1. 在VRChat中进行动作测试
2. 观察Web界面中的 "Raw Level" 数据变化
3. 根据实际数据范围调整 `vrchat_max` 和 `vrchat_min` 参数
4. 程序会自动进行线性映射优化运动范围

## API接口

程序提供以下REST API接口：

### 设备控制
- `POST /api/osr/move-max` - 移动到最大位置
- `POST /api/osr/move-min` - 移动到最小位置
- `POST /start` - 启动OSR服务
- `POST /stop` - 停止OSR服务
- `POST /restart` - 重启OSR服务

### 配置管理
- `GET /api/config` - 获取当前配置
- `POST /api/config` - 保存配置
- `GET /api/status` - 获取设备状态

### 数据获取
- `GET /api/data` - 获取实时图表数据
- `GET /check_alive` - 检查服务状态

## 项目结构

```
OSR-VRChat/
├── osr_vrchat.py              # 主程序文件
├── requirements.txt           # Python依赖
├── settings-advanced-v0.1.2.yaml  # 配置文件
├── src/                       # 源码目录
│   ├── connector/
│   │   └── osr_connector.py   # OSR设备连接器
│   └── handler/
│       ├── base_handler.py    # 基础处理器
│       └── stroke_handler.py  # 动作处理器
├── templates/                 # Web模板
│   ├── index.html            # 首页模板
│   └── config.html           # 配置页面模板
└── wearable/                 # 可穿戴配件3D模型
    ├── base V1.stl
    └── shoulder V1.stl
```

## 故障排除

### 常见问题

**Q: 设备连接失败**
A: 检查串口号是否正确，确保没有其他程序占用串口

**Q: VRChat数据接收不到**
A: 确认VRChat OSC功能已开启，检查OSC端口配置

**Q: 设备移动范围不正确**
A: 重新校准 `max_pos`, `min_pos`, `vrchat_max`, `vrchat_min` 参数

**Q: Web界面无法访问**
A: 检查防火墙设置，确认端口8800未被占用

### 日志查看

程序运行时会在控制台输出详细日志，包括：
- 设备连接状态
- OSC数据接收情况
- 错误信息和调试信息

## 可穿戴套装

为了更好的使用体验，项目提供了可穿戴套装的3D打印文件和安装指南。

### 物品清单

**1. 2个可调节长短的魔术贴背带**
- 可调长度在90-155cm为佳，宽度为5cm

**2. 腰封**
- 外圈固定腰带的宽度为5cm

**3. 3D打印套件**
- 请将[wearable目录](wearable)下的两个`.stl`文件发给代打印商家
- `base V1.stl` - 底座固定件
- `shoulder V1.stl` - 肩带连接件

**4. 4个M4 10mm长的螺丝以及螺丝刀**

### 安装方法

1. 把套件的上下两个部分安装到OSR2的底座，并固定到腰带上
2. 安装肩带，一端穿过套件的肩带环，另一端固定至腰带的背面
3. 调整腰带的位置，并尽量拉紧腰带
4. 背上肩带，安装杯子
5. 调整螺丝滑轨，确定杯子和腰带之间的最佳距离
6. 调整肩带的长度，选择最适合自己的角度
7. 连接OSR2至电脑

### 推荐链接

请参考[wearable目录](wearable)下的购买链接图片获取相关配件。

## 开发说明

### 依赖库

- **Flask**: Web服务器框架
- **pyserial**: 串口通信
- **python-osc**: OSC协议支持
- **loguru**: 日志记录
- **PyYAML**: 配置文件解析

### 扩展开发

项目采用模块化设计，可以轻松扩展：
- 添加新的设备连接器 (`src/connector/`)
- 实现新的数据处理器 (`src/handler/`)
- 自定义Web界面 (`templates/`)

## 致谢

- 感谢 [Shocking-VRChat](https://github.com/VRChatNext/Shocking-VRChat) 项目提供的框架参考
- 感谢 [OGB](https://osc.toys/) 项目提供的OSC数据接口
- 感谢 [SPS](https://github.com/SenkyDragon/SPS) 插件作者的技术支持

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 测试QQ群: 1034983762
- GitHub Issues: [提交问题](../../issues)

---

**注意**: 本项目仅供学习和研究使用，请遵守当地法律法规。
