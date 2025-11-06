import asyncio
import yaml, uuid, os, sys, traceback, time
from threading import Thread
from loguru import logger
import traceback
import random

from flask import Flask, jsonify, render_template, render_template_string, request

from src.connector.osr_connector import OSRConnector
from src.handler.stroke_handler import StrokeHandler                                                                                                                                                                                                                  
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from collections import deque
import webbrowser

app = Flask(__name__, template_folder='templates')

CONFIG_FILE_VERSION  = 'v0.2.2'
CONFIG_FILENAME = f'settings-advanced-{CONFIG_FILE_VERSION}.yaml'
CONFIG_FILENAME_BASIC = f'settings-{CONFIG_FILE_VERSION}.yaml'
MAX_LINECHART_POINTS = 100
charts_data = [
    deque(maxlen=MAX_LINECHART_POINTS) for _ in range(6)
]
timestamps = deque(maxlen=MAX_LINECHART_POINTS)
connector = None
stop_flag = False
transport = None
main_future = None
th = None
handlers = None

SETTINGS = {
    'SERVER_IP': None,
    'osr2':{     
        'objective': 'inserting_others', #self or others (inserting_self, inserting_others, inserted_pussy, inserted_ass)
        'max_pos':900,
        'min_pos':100,
        'vrchat_max':1000,
        'vrchat_min':0,
        'max_velocity': 1400,
        'l0_axis_invert': False,
        # 'max_acceleration':5000,
        'updates_per_second': 50,
        'com_port':'COM4',
        'use_udp': False,
        'udp_server_ip': '192.168.1.100',
        'udp_server_port': 8000,
        # 'ema_filter' : 0.7,
        'inserting_self': "/avatar/parameters/OGB/Pen/*",
        'inserting_others': "/avatar/parameters/OGB/Pen/*",
        'inserted_ass':"/avatar/parameters/OGB/Orf/Ass/PenOthers",
        'inserted_pussy': "/avatar/parameters/OGB/Orf/Pussy/PenOthers"
    },
    'version': CONFIG_FILE_VERSION,
    'osc':{
        'listen_host': '127.0.0.1',
        'listen_port': 9001,
    },
    'web_server':{
        'listen_host': '127.0.0.1',
        'listen_port': 8800
    },
    'log_level': 'INFO',
    'general': {
        'auto_open_web_page': True,
        'local_ip_detect': {
            'host': '223.5.5.5',
            'port': 80,
        }
    }
}
SERVER_IP = None

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

async def async_main():
    global connector, transport, main_future
    main_future = asyncio.Future()
    # handlers[0].start_background_jobs()
    if (SETTINGS['osr2']['use_udp'] == True):
        try:
            connector = OSRConnector(ip=SETTINGS['osr2']['udp_server_ip'], port=SETTINGS['osr2']['udp_server_port'])
            await connector.connect()
            await connector.write_to_udp("L0100I500")
            time.sleep(1)
            await connector.write_to_udp("L0500I500")
            time.sleep(1)
            await connector.write_to_udp("L0900I500")
            logger.success("OSR设备自检指令已发送")
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error("OSR设备自检指令发送失败")
            return
    else:
        try:
            connector = OSRConnector(port=SETTINGS['osr2']['com_port'])
            await connector.connect()
            await connector.write_to_serial("L0100I500")
            time.sleep(1)
            await connector.write_to_serial("L0500I500")
            time.sleep(1)
            await connector.write_to_serial("L0900I500")
            logger.success("OSR设备自检成功")
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error("OSR设备连接失败，请检查串口地址是否正确，设备是否插紧")
            return

    for handler in handlers:
        handler.set_connector(connector)
    try: 
        server = AsyncIOOSCUDPServer((SETTINGS["osc"]["listen_host"], SETTINGS["osc"]["listen_port"]), dispatcher, asyncio.get_event_loop())
        logger.success(f'OSC Listening: {SETTINGS["osc"]["listen_host"]}:{SETTINGS["osc"]["listen_port"]}')
        transport, protocol = await server.create_serve_endpoint()

        try:
            await main_future
        except asyncio.CancelledError:
            pass
        finally:
            if transport:
                transport.close()
                logger.info("transport.close()")
            if connector:
                # 使用同步方式关闭串口连接
                if connector.ser and connector.ser.is_open:
                    connector.ser.close()
                    logger.info(f"Disconnected from {connector.port}.")

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("OSC UDP Recevier listen failed.")
        logger.error("OSC监听失败，可能存在端口冲突")
        return

    transport.close()

def async_main_wrapper():
    """Not async Wrapper around async_main to run it as target function of Thread"""
    asyncio.run(async_main())

def config_save():
    with open(CONFIG_FILENAME, 'w', encoding='utf-8') as fw:
        yaml.safe_dump(SETTINGS, fw, allow_unicode=True)
    
class ConfigFileInited(Exception):
    pass

def config_init():
    logger.info(f'Init settings..., Config filename: {CONFIG_FILENAME}, Config version: {CONFIG_FILE_VERSION}.')
    global SETTINGS, SETTINGS_BASIC, SERVER_IP
    if not (os.path.exists(CONFIG_FILENAME)):
        config_save()
        raise ConfigFileInited()

    with open(CONFIG_FILENAME, 'r', encoding='utf-8') as fr:
        SETTINGS = yaml.safe_load(fr)

    if SETTINGS.get('version', None) != CONFIG_FILE_VERSION:# or SETTINGS_BASIC.get('version', None) != CONFIG_FILE_VERSION:
        logger.error(f"Configuration file version mismatch! Please delete the {CONFIG_FILENAME} files and run the program again to generate the latest version of the configuration files.")
        raise Exception(f'配置文件版本不匹配！请删除 {CONFIG_FILENAME} 文件后再次运行程序，以生成最新版本的配置文件。')
    SERVER_IP = SETTINGS['SERVER_IP']# or get_current_ip()

    logger.remove()
    logger.add(sys.stderr, level=SETTINGS['log_level'])
    logger.success("The configuration file initialization is complete. If a firewall prompt appears, please click Allow Access.")
    logger.success("配置文件初始化完成，如弹出防火墙提示，请点击允许访问。")





@app.route('/')
def index():
    return render_template('config.html')

@app.route('/data')
def data_page():
    return render_template('index.html')

@app.route('/config')
def config_page():
    return render_template('config.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取当前配置"""
    return jsonify(SETTINGS)

@app.route('/api/config', methods=['POST'])
def save_config():
    """保存配置"""
    try:
        new_config = request.json
        
        # 更新配置
        if 'osr2' in new_config:
            SETTINGS['osr2'].update(new_config['osr2'])
        if 'osc' in new_config:
            SETTINGS['osc'].update(new_config['osc'])
        if 'web_server' in new_config:
            SETTINGS['web_server'].update(new_config['web_server'])
        if 'general' in new_config:
            SETTINGS['general'].update(new_config['general'])
        if 'log_level' in new_config:
            SETTINGS['log_level'] = new_config['log_level']
            
        # 保存到文件
        config_save()
        
        return jsonify({'success': True, 'message': '配置保存成功'})
    except Exception as e:
        logger.error(f"保存配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取系统状态"""
    global connector, transport, th
    
    if (SETTINGS['osr2']['use_udp'] == False):
        device_connected = connector is not None and connector.ser is not None
    else:
        device_connected = connector is not None and connector.sock is not None
    osc_running = transport is not None
    main_running = th is not None and th.is_alive()
    
    return jsonify({
        'device_connected': device_connected,
        'osc_running': osc_running,
        'main_running': main_running
    })



@app.route('/api/data')
def get_chart_data():

    global handlers
    
    current_time = time.time()
    timestamps.append(current_time)
    if handlers:
        panel_data = handlers[0].get_panel_data()
        # print(panel_data)
        charts_data[0].append(panel_data['raw_level'])
        charts_data[1].append(panel_data['raw_velocity'])
        charts_data[2].append(panel_data['raw_acceleration'])
        charts_data[3].append(panel_data['processed_velocity'])
        charts_data[4].append(panel_data['processed_acceleration'])
        charts_data[5].append(panel_data['output_level'])
    else:
        for chart_deque in charts_data:
            chart_deque.append(random.uniform(0, 10))

    return jsonify({"timestamps": list(timestamps), "lines": [list(i) for i in charts_data]})


@app.route("/start", methods=["POST","GET"])
def start_osr():
    main()
    return "OSR main loop started."


@app.route("/check_alive", methods=["POST","GET"])
def check_alive():
    print(th.isAlive())
    return "OSR main loop stopped."

@app.route("/stop", methods=["POST","GET"])
def stop_osr():
    main_future.cancel()
    th.join(10)
    print(th.isAlive())
    return "OSR main loop stopped."

@app.route("/restart", methods=["POST","GET"])
def restart_osr():
    """重启后端程序"""
    global main_future, th, connector, transport
    try:
        # 停止当前运行的程序
        if main_future and not main_future.done():
            main_future.cancel()
        if th and th.is_alive():
            th.join(10)
        
        # 确保串口连接完全断开
        if connector:
            # 使用同步方式关闭串口连接
            if hasattr(connector, 'ser') and connector.ser and connector.ser.is_open:
                connector.ser.close()
                logger.info(f"Disconnected from {connector.port}.")
            connector = None
        
        # 确保transport关闭
        if transport:
            transport.close()
            transport = None
        
        # 重新启动（不打开浏览器）
        main_without_browser()
        return jsonify({'success': True, 'message': '后端程序重启成功'})
    except Exception as e:
        logger.error(f"重启失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route("/api/osr/move-max", methods=["POST"])
def move_to_max_position():
    """移动OSR设备到最大位置"""
    global connector
    try:
        if not connector or not connector.ser or not connector.ser.is_open:
            return jsonify({'success': False, 'message': 'OSR设备未连接'}), 400
        
        max_pos = SETTINGS['osr2']['max_pos']
        # 发送位置命令，格式为L0XX，其中XX是位置值（0-99对应0-999）
        position_value = int(max_pos / 10)  # 将0-999映射到0-99
        command = f"L0{position_value:02d}"
        
        if (SETTINGS['osr2']['use_udp'] == False):
            connector.write_to_serial(command)
        else:
            connector.write_to_udp(command)
        logger.info(f"发送最大位置命令: {command} (位置: {max_pos})")
        
        return jsonify({'success': True, 'message': f'已发送移动到最大位置命令 ({max_pos})'})
    except Exception as e:
        logger.error(f"移动到最大位置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route("/api/osr/move-min", methods=["POST"])
def move_to_min_position():
    """移动OSR设备到最小位置"""
    global connector
    try:
        if not connector or not connector.ser or not connector.ser.is_open:
            return jsonify({'success': False, 'message': 'OSR设备未连接'}), 400
        
        min_pos = SETTINGS['osr2']['min_pos']
        # 发送位置命令，格式为L0XX，其中XX是位置值（0-99对应0-999）
        position_value = int(min_pos / 10)  # 将0-999映射到0-99
        command = f"L0{position_value:02d}"
        
        if (SETTINGS['osr2']['use_udp'] == False):
            connector.write_to_serial(command)
        else:
            connector.write_to_udp(command)
        logger.info(f"发送最小位置命令: {command} (位置: {min_pos})")
        
        return jsonify({'success': True, 'message': f'已发送移动到最小位置命令 ({min_pos})'})
    except Exception as e:
        logger.error(f"移动到最小位置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

import click
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
def secho(text, file=None, nl=None, err=None, color=None, **styles):
    pass
def echo(text, file=None, nl=None, err=None, color=None, **styles):
    pass
click.echo = echo
click.secho = secho


def main_without_browser():
    """启动主程序但不打开浏览器"""
    global dispatcher, handlers,th
    dispatcher = Dispatcher()
    handlers = []

    insert_params = SETTINGS['osr2'][SETTINGS['osr2']['objective']]

    stroke_handler = StrokeHandler(SETTINGS=SETTINGS)
    handlers.append(stroke_handler)

    target_param = insert_params#[SETTINGS['osr2']['objective']]
    logger.success(f"Listening：{target_param}")
    dispatcher.map(target_param, handlers[0].osc_handler)

    if SETTINGS['osr2']['objective'] not in ['inserting_others','inserting_self','inserted_ass','inserted_pussy']:
        logger.error("Wrong objective type!")

    th = Thread(target=async_main_wrapper, daemon=True)
    th.start()

def main():
    global dispatcher, handlers,th
    dispatcher = Dispatcher()
    handlers = []

    insert_params = SETTINGS['osr2'][SETTINGS['osr2']['objective']]

    stroke_handler = StrokeHandler(SETTINGS=SETTINGS)
    handlers.append(stroke_handler)

    target_param = insert_params#[SETTINGS['osr2']['objective']]
    logger.success(f"Listening：{target_param}")
    dispatcher.map(target_param, handlers[0].osc_handler)

    if SETTINGS['osr2']['objective'] not in ['inserting_others','inserting_self','inserted_ass','inserted_pussy']:
        logger.error("Wrong objective type!")


    th = Thread(target=async_main_wrapper, daemon=True)
    th.start()

    if (SETTINGS['general']['auto_open_web_page'] == True):
        webbrowser.open_new_tab(f"http://127.0.0.1:{SETTINGS['web_server']['listen_port']}")
        # app.run(SETTINGS['web_server']['listen_host'], SETTINGS['web_server']['listen_port'], debug=False)

if __name__ == "__main__":
    try:
        config_init()
        start_osr()
        app.run(SETTINGS['web_server']['listen_host'], SETTINGS['web_server']['listen_port'], debug=False)
        # start_osr()
    except ConfigFileInited:
        logger.success('The configuration file initialization is complete. Please modify it as needed and restart the program.')
        logger.success('配置文件初始化完成，请按需修改后重启程序。')
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("Unexpected Error.")
    
    logger.info('Exiting in 1 seconds ... Press Ctrl-C to exit immediately')
    logger.info('退出等待1秒 ... 按Ctrl-C立即退出')
    if connector:
        # 使用同步方式关闭串口连接
        if hasattr(connector, 'ser') and connector.ser and connector.ser.is_open:
            connector.ser.close()
            logger.info(f"Disconnected from {connector.port}.")
    time.sleep(1)
