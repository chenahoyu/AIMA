"""
grandMA3 OSC 通信客户端模块

提供与 grandMA3 控制台的 OSC 通信功能。
根据实践经验，发送给 grandMA3 的指令字符串严禁包含 /cmd 前缀，
且必须剥离字符串外层的所有多余引号。

作者：AI-MA 项目组
版本：1.0.0
日期：2026-04-12
"""

import logging
import sys
from pathlib import Path
from typing import Optional, List, Any
from pythonosc import udp_client

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from config import settings


class GMA3Client:
    """
    grandMA3 OSC 通信客户端
    
    提供与 grandMA3 控制台的 OSC 通信功能，包括：
    - 连接管理
    - 命令发送
    - 属性控制
    - 状态监控
    """
    
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        """
        初始化 OSC 客户端
        
        Args:
            host: grandMA3 主机地址，默认为配置中的 ma3_osc_host
            port: grandMA3 OSC 端口，默认为配置中的 ma3_osc_port
        """
        # 使用配置或传入参数
        self.host = host or settings.ma3_osc_host
        self.port = port or settings.ma3_osc_port
        
        # 客户端状态
        self.client: Optional[udp_client.SimpleUDPClient] = None
        self.connected = False
        self.connection_time: Optional[float] = None
        
        # 统计信息
        self.stats = {
            "commands_sent": 0,
            "commands_failed": 0,
            "connections": 0,
            "errors": 0
        }
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"GMA3Client 初始化：{self.host}:{self.port}")
    
    def connect(self) -> bool:
        """
        连接到 grandMA3 OSC 服务器
        
        Returns:
            bool: 连接是否成功
        """
        if self.connected:
            self.logger.warning("已经连接到 grandMA3")
            return True
        
        try:
            # 创建 UDP 客户端
            self.client = udp_client.SimpleUDPClient(self.host, self.port)
            self.connected = True
            self.connection_time = __import__('time').time()
            self.stats["connections"] += 1
            
            self.logger.info(f"成功连接到 grandMA3: {self.host}:{self.port}")
            return True
            
        except Exception as e:
            self.connected = False
            self.stats["errors"] += 1
            self.logger.error(f"连接 grandMA3 失败：{e}")
            return False
    
    def disconnect(self) -> None:
        """断开与 grandMA3 的连接"""
        if not self.connected:
            return
        
        try:
            self.client = None
            self.connected = False
            self.connection_time = None
            self.logger.info("已断开 grandMA3 连接")
        except Exception as e:
            self.logger.error(f"断开连接时出错：{e}")
    
    def send_command(self, cmd_string) -> tuple:
        """
        发送 grandMA3 命令
        
        支持发送单个命令字符串或命令列表
        硬性约束：
        - 严禁包含 /cmd 前缀
        - 必须剥离字符串外层的所有多余引号
        - 发送多条指令时必须加入微小延迟
        
        Args:
            cmd_string: grandMA3 命令字符串或命令列表，例如 "Fixture 1 At 100" 或 ["ClearAll", "Fixture 1 At 100"]
            
        Returns:
            tuple: (success: bool, message: str)
        """
        import time
        
        # 检查连接状态
        if not self.connected:
            self.logger.warning("未连接到 grandMA3，尝试重新连接...")
            if not self.connect():
                self.logger.error("无法连接到 grandMA3，命令发送失败")
                return (False, "未连接到 grandMA3")
        
        # 支持列表输入
        if isinstance(cmd_string, list):
            commands = cmd_string
        else:
            commands = [cmd_string]
        
        success_count = 0
        failed_commands = []
        
        # 遍历发送每条指令
        for i, cmd_string in enumerate(commands):
            # 清理命令字符串
            cleaned_cmd = self._clean_command(cmd_string)
            
            try:
                # 发送 OSC 消息
                # 注意：根据实践经验，发送给 grandMA3 的指令字符串严禁包含 /cmd 前缀
                # send_message 的 value 参数可以是字符串或列表
                # 我们直接发送纯净的命令字符串
                print(f"DEBUG OSC: 准备发送 - address=/cmd, value={repr(cleaned_cmd)}, type={type(cleaned_cmd)}")
                self.client.send_message("/cmd", cleaned_cmd)
                print(f"DEBUG OSC: 发送成功")
                
                self.stats["commands_sent"] += 1
                self.logger.info(f"命令 {i+1}/{len(commands)} 发送成功：{cleaned_cmd}")
                self.logger.info(f"发送的数据类型：{type(cleaned_cmd)}, 值：{repr(cleaned_cmd)}")
                success_count += 1
                
            except Exception as e:
                self.stats["commands_failed"] += 1
                self.stats["errors"] += 1
                self.logger.error(f"命令 {i+1}/{len(commands)} 发送失败：{cleaned_cmd}")
                self.logger.error(f"错误：{e}")
                failed_commands.append((cleaned_cmd, str(e)))
            
            # 每条指令之间加入微小延迟（防止解析故障）
            if i < len(commands) - 1:  # 最后一条不需要延迟
                time.sleep(0.05)
        
        # 返回整体结果
        if success_count == len(commands):
            return (True, f"所有 {success_count} 条命令已发送成功")
        else:
            failed_str = "; ".join([f"{cmd}: {err}" for cmd, err in failed_commands])
            return (False, f"{success_count}/{len(commands)} 条命令发送成功，失败：{failed_str}")
    
    def set_fixture_attribute(
        self,
        fixture_id: int,
        attribute: str,
        value: Any,
        at: bool = True
    ) -> bool:
        """
        封装高级函数，设置灯具属性
        
        自动组装成符合 MA3 逻辑的命令行字符串
        
        Args:
            fixture_id: 灯具 ID
            attribute: 属性名称，例如 "Dimmer", "ColorRGB_R"
            value: 属性值
            at: 是否使用 "At" 关键字（默认 True）
            
        Returns:
            bool: 是否发送成功
            
        Examples:
            >>> client.set_fixture_attribute(101, "Dimmer", 100)
            # 发送：Fixture 101 Attribute "Dimmer" At 100
            
            >>> client.set_fixture_attribute(5, "ColorRGB_R", 255, at=False)
            # 发送：Fixture 5 Attribute "ColorRGB_R" 255
        """
        # 构建命令字符串
        # 格式：Fixture {id} Attribute "{attribute}" [At] {value}
        if at:
            cmd = f'Fixture {fixture_id} Attribute "{attribute}" At {value}'
        else:
            cmd = f'Fixture {fixture_id} Attribute "{attribute}" {value}'
        
        return self.send_command(cmd)
    
    def set_fixture_dimmer(self, fixture_id: int, dimmer_value: int) -> bool:
        """
        快捷函数：设置灯具亮度
        
        Args:
            fixture_id: 灯具 ID
            dimmer_value: 亮度值 (0-100)
            
        Returns:
            bool: 是否发送成功
        """
        return self.set_fixture_attribute(fixture_id, "Dimmer", dimmer_value)
    
    def set_fixture_color(
        self,
        fixture_id: int,
        r: int,
        g: int,
        b: int
    ) -> bool:
        """
        快捷函数：设置灯具颜色
        
        Args:
            fixture_id: 灯具 ID
            r: 红色值 (0-255)
            g: 绿色值 (0-255)
            b: 蓝色值 (0-255)
            
        Returns:
            bool: 是否发送成功
        """
        # 分别设置 RGB 通道
        success = True
        success &= self.set_fixture_attribute(fixture_id, "ColorRGB_R", r)
        success &= self.set_fixture_attribute(fixture_id, "ColorRGB_G", g)
        success &= self.set_fixture_attribute(fixture_id, "ColorRGB_B", b)
        return success
    
    def go_plus(self, sequence_id: int) -> bool:
        """
        执行序列 Go+
        
        Args:
            sequence_id: 序列 ID
            
        Returns:
            bool: 是否发送成功
        """
        return self.send_command(f"Sequence {sequence_id} Go+")
    
    def preset_go(self, preset_id: str) -> bool:
        """
        执行预设
        
        Args:
            preset_id: 预设 ID，例如 "1.1"
            
        Returns:
            bool: 是否发送成功
        """
        return self.send_command(f"Preset {preset_id}")
    
    def group_at(self, group_id: int, value: int) -> bool:
        """
        设置组亮度
        
        Args:
            group_id: 组 ID
            value: 亮度值 (0-100)
            
        Returns:
            bool: 是否发送成功
        """
        return self.send_command(f"Group {group_id} At {value}")
    
    def clear_all(self) -> bool:
        """
        清除所有
        
        Returns:
            bool: 是否发送成功
        """
        return self.send_command("ClearAll")
    
    def get_status(self) -> dict:
        """
        获取客户端状态信息
        
        Returns:
            dict: 状态信息字典
        """
        return {
            "connected": self.connected,
            "host": self.host,
            "port": self.port,
            "connection_time": self.connection_time,
            "stats": self.stats.copy()
        }
    
    def clear_stats(self) -> None:
        """清空统计信息"""
        self.stats = {
            "commands_sent": 0,
            "commands_failed": 0,
            "connections": 0,
            "errors": 0
        }
    
    # 私有方法
    def _clean_command(self, cmd_string: str) -> str:
        """
        清理命令字符串
        
        硬性约束：
        - 剥离字符串外层的所有多余引号
        - 确保不包含 /cmd 前缀
        
        Args:
            cmd_string: 原始命令字符串
            
        Returns:
            str: 清理后的命令字符串
        """
        # 移除 /cmd 前缀
        if cmd_string.startswith("/cmd"):
            cmd_string = cmd_string[4:].strip()
        
        # 移除外层引号（单引号或双引号）
        if (cmd_string.startswith('"') and cmd_string.endswith('"')) or \
           (cmd_string.startswith("'") and cmd_string.endswith("'")):
            cmd_string = cmd_string[1:-1]
        
        # 去除首尾空白
        cmd_string = cmd_string.strip()
        
        return cmd_string
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()
    
    def __repr__(self) -> str:
        """对象表示"""
        status = "connected" if self.connected else "disconnected"
        return f"GMA3Client(host={self.host}, port={self.port}, status={status})"


# 快捷函数
def create_gma3_client(host: Optional[str] = None, port: Optional[int] = None) -> GMA3Client:
    """
    创建并返回配置好的 grandMA3 客户端
    
    Args:
        host: 主机地址
        port: 端口
        
    Returns:
        GMA3Client: 配置好的客户端实例
    """
    return GMA3Client(host=host, port=port)


if __name__ == "__main__":
    # 模块测试代码
    import sys
    import time
    
    # 设置基础日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=== GMA3Client 模块测试 ===")
    print()
    
    # 创建客户端
    print("1. 创建客户端...")
    client = create_gma3_client()
    print(f"   客户端：{client}")
    print()
    
    # 测试连接
    print("2. 测试连接...")
    success = client.connect()
    if success:
        print("   ✅ 连接成功")
    else:
        print("   ❌ 连接失败")
        print("   请确保 grandMA3 正在运行并监听 OSC 端口")
        sys.exit(1)
    
    print()
    
    if success:
        # 发送测试命令
        print("3. 发送测试命令...")
        
        test_commands = [
            ("设置灯具 1 亮度 100%", lambda: client.set_fixture_dimmer(1, 100)),
            ("设置灯具 2 亮度 50%", lambda: client.set_fixture_dimmer(2, 50)),
            ("设置灯具 3 红色", lambda: client.set_fixture_color(3, 255, 0, 0)),
            ("设置组 1 亮度 75%", lambda: client.group_at(1, 75)),
        ]
        
        for description, command_func in test_commands:
            print(f"   测试：{description}")
            result = command_func()
            print(f"   结果：{'✅ 成功' if result else '❌ 失败'}")
            time.sleep(0.5)  # 短暂延迟
        
        print()
        
        # 显示状态
        print("4. 客户端状态:")
        status = client.get_status()
        print(f"   连接状态：{status['connected']}")
        print(f"   主机：{status['host']}:{status['port']}")
        print(f"   发送命令数：{status['stats']['commands_sent']}")
        print(f"   失败命令数：{status['stats']['commands_failed']}")
        print(f"   错误数：{status['stats']['errors']}")
        
        print()
        print("=== 测试完成 ===")
        
        # 断开连接
        client.disconnect()
        print("已断开连接")
    else:
        print("=== 测试失败 ===")
        print("请检查 grandMA3 是否正在运行")
