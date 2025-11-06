# OSR-VRChat

[中文版本](README.md)

A Python Flask-based OSR device control program that enables real-time motion synchronization between OSR robots and VRChat. It receives SPS plugin data from VRChat via OSC protocol and converts it into OSR device control commands.

## Features

- 🎮 **VRChat Integration**: Real-time motion data reception from VRChat via OSC protocol
- 🤖 **OSR Device Support**: Serial port control for OSR2/2+ devices
- 🌐 **Web Interface**: Intuitive web-based configuration and monitoring interface
- 📊 **Real-time Monitoring**: Live data charts and device status monitoring
- ⚙️ **Flexible Configuration**: Multiple working modes and detailed parameter adjustment
- 🔧 **Device Control**: Manual position control and device testing functionality

## System Requirements

- Windows 10/11 (Recommended)
- Python 3.8+ (if running from source)
- OSR2/2+ device
- VRChat + SPS plugin
- Chrome browser (for device testing)

## Quick Start

### Method 1: Using Pre-compiled Version (Recommended)

1. Download the latest `.exe` file from [Releases](../../releases)
2. Double-click to run the program. First run will generate configuration file and exit
3. Edit the generated `settings-advanced-v0.1.2.yaml` configuration file
4. Run the program again to start using

### Method 2: Running from Source

1. **Clone the project**
   ```bash
   git clone <repository-url>
   cd OSR-VRChat
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the program**
   ```bash
   python osr_vrchat.py
   ```

## Device Setup

### 1. OSR Device Setup

1. Connect OSR2 device to computer USB port
2. Turn on OSR2 power switch
3. Open [Mosa Controller](https://trymosa.netlify.app/) in Chrome browser
4. Select "Serial" and choose the corresponding port in the popup
5. Test L0 axis control, record suitable maximum and minimum values
6. **Important**: Close the webpage after testing to release the serial port

### 2. VRChat Setup

1. Ensure OSC functionality is enabled in VRChat
2. Install and configure SPS plugin
3. Confirm model's attachment functionality is working properly
4. Ensure using SPS-based models (DPS/TPS not supported)

## Configuration

The program generates `settings-advanced-v0.1.2.yaml` configuration file on first run. Main configuration items:

### OSR Device Configuration (`osr2`)

```yaml
osr2:
  com_port: "COM4"              # Serial port number from Device Manager
  objective: "inserted_pussy"    # Working mode, see table below
  max_pos: 500                  # Maximum position (0-999)
  min_pos: 1                    # Minimum position (0-999)
  max_velocity: 2000            # Maximum velocity (units/second)
  updates_per_second: 50        # Update frequency (Hz)
  vrchat_max: 700               # VRChat SPS data maximum value
  vrchat_min: 200               # VRChat SPS data minimum value
  l0_axis_invert: false         # L0 axis inversion
```

### Working Modes (`objective`)

| Mode | Description |
|------|-------------|
| `inserting_others` | Using your penetrator to insert into others' orifice |
| `inserting_self` | Using your penetrator to insert into your own orifice (for testing) |
| `inserted_ass` | Your anal orifice being penetrated by others |
| `inserted_pussy` | Your vaginal orifice being penetrated by others |

### Network Configuration

```yaml
web_server:
  listen_host: "127.0.0.1"      # Web interface listen address
  listen_port: 8800             # Web interface port

osc:
  listen_host: "127.0.0.1"      # OSC listen address
  listen_port: 9001             # OSC listen port
```

## Usage

### 1. Start the Program

After running the program, it will automatically:
- Connect to OSR device
- Start OSC listening service
- Start web server
- Perform device self-check

### 2. Access Web Interface

Open `http://127.0.0.1:8800` in your browser to access the control interface:

- **Home**: Real-time data monitoring and charts
- **Config Page**: Parameter configuration and device control
- **Data Page**: Detailed data analysis

### 3. Device Control Functions

The configuration page provides the following control functions:
- **Position Control**: Manually move device to maximum/minimum positions
- **Axis Inversion**: L0 axis direction inversion switch
- **Parameter Adjustment**: Real-time adjustment of various parameters
- **Device Status**: View connection status and operation information

### 4. Data Calibration

1. Perform actions in VRChat for testing
2. Observe "Raw Level" data changes in the web interface
3. Adjust `vrchat_max` and `vrchat_min` parameters based on actual data range
4. The program will automatically perform linear mapping to optimize motion range

## API Endpoints

The program provides the following REST API endpoints:

### Device Control
- `POST /api/osr/move-max` - Move to maximum position
- `POST /api/osr/move-min` - Move to minimum position
- `POST /start` - Start OSR service
- `POST /stop` - Stop OSR service
- `POST /restart` - Restart OSR service

### Configuration Management
- `GET /api/config` - Get current configuration
- `POST /api/config` - Save configuration
- `GET /api/status` - Get device status

### Data Retrieval
- `GET /api/data` - Get real-time chart data
- `GET /check_alive` - Check service status

## Project Structure

```
OSR-VRChat/
├── osr_vrchat.py              # Main program file
├── requirements.txt           # Python dependencies
├── settings-advanced-v0.1.2.yaml  # Configuration file
├── src/                       # Source code directory
│   ├── connector/
│   │   └── osr_connector.py   # OSR device connector
│   └── handler/
│       ├── base_handler.py    # Base handler
│       └── stroke_handler.py  # Motion handler
├── templates/                 # Web templates
│   ├── index.html            # Home page template
│   └── config.html           # Configuration page template
└── wearable/                 # Wearable accessory 3D models
    ├── base V1.stl
    └── shoulder V1.stl
```

## Wearable Kit

For better user experience, the project provides 3D printing files and installation guide for wearable kit.

### Parts List

**1. 2 Adjustable Magic Tape Straps**
- Adjustable length 90-155cm preferred, width 5cm

**2. Waist Belt**
- Outer belt width for fixing should be 5cm

**3. 3D Printing Kit**
- Send the two `.stl` files in [wearable directory](wearable) to 3D printing service
- `base V1.stl` - Base mounting component
- `shoulder V1.stl` - Shoulder strap connector

**4. 4 M4 10mm Screws and Screwdriver**

### Installation Method

1. Install the upper and lower parts of the kit to the OSR2 base and fix to the belt
2. Install shoulder straps, thread one end through the kit's shoulder strap ring, fix the other end to the back of the belt
3. Adjust belt position and tighten as much as possible
4. Put on shoulder straps and install the cup
5. Adjust screw rails to determine optimal distance between cup and belt
6. Adjust shoulder strap length to choose the most suitable angle
7. Connect OSR2 to computer

### Recommended Links

Please refer to the purchase link images in [wearable directory](wearable) to get related accessories.

## Troubleshooting

### Common Issues

**Q: Device connection failed**
A: Check if serial port number is correct, ensure no other programs are using the port

**Q: Cannot receive VRChat data**
A: Confirm VRChat OSC functionality is enabled, check OSC port configuration

**Q: Incorrect device movement range**
A: Recalibrate `max_pos`, `min_pos`, `vrchat_max`, `vrchat_min` parameters

**Q: Cannot access web interface**
A: Check firewall settings, confirm port 8800 is not occupied

### Log Viewing

The program outputs detailed logs to console during runtime, including:
- Device connection status
- OSC data reception status
- Error messages and debug information

## Development

### Dependencies

- **Flask**: Web server framework
- **pyserial**: Serial communication
- **python-osc**: OSC protocol support
- **loguru**: Logging
- **PyYAML**: Configuration file parsing

### Extension Development

The project uses modular design for easy extension:
- Add new device connectors (`src/connector/`)
- Implement new data handlers (`src/handler/`)
- Customize web interface (`templates/`)

## Acknowledgments

- Thanks to [Shocking-VRChat](https://github.com/VRChatNext/Shocking-VRChat) project for framework reference
- Thanks to [OGB](https://osc.toys/) project for OSC data interfaces
- Thanks to [SPS](https://github.com/SenkyDragon/SPS) plugin author for technical support

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Contact

- Test QQ Group: 1034983762
- GitHub Issues: [Submit Issues](../../issues)

---

**Note**: This project is for educational and research purposes only. Please comply with local laws and regulations.
