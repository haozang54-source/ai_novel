"""
时间检查工具
"""
import time
from datetime import datetime


class TimeChecker:
    """时间检查器，用于控制程序运行时间"""
    
    def __init__(self, config: dict):
        """
        初始化时间检查器
        
        Args:
            config: 配置字典
        """
        self.config = config
        runtime_config = config.get('runtime', {})
        self.enabled = bool(runtime_config)
        self.start_hour = runtime_config.get('start', 22)
        self.end_hour = runtime_config.get('end', 8)
        self.check_interval = runtime_config.get('check_interval', 300)
        self.last_check_time = datetime.now()
    
    def is_allowed(self) -> bool:
        """
        检查当前时间是否允许运行
        
        Returns:
            是否允许运行
        """
        if not self.enabled:
            return True
        
        current_hour = datetime.now().hour
        
        # 处理跨天的情况
        if self.start_hour > self.end_hour:
            # 跨天：如 22点到次日8点
            return current_hour >= self.start_hour or current_hour < self.end_hour
        else:
            # 不跨天
            return self.start_hour <= current_hour < self.end_hour
    
    def check_and_wait(self):
        """
        检查时间，如果不在允许时段则等待
        """
        if not self.enabled:
            return
        
        # 如果距离上次检查不到间隔时间，跳过
        now = datetime.now()
        if (now - self.last_check_time).seconds < self.check_interval:
            return
        
        self.last_check_time = now
        
        if not self.is_allowed():
            print(f"\n⏰ [{now.strftime('%H:%M:%S')}] 超出允许运行时间段，暂停...")
            self._wait_for_allowed_time()
            print(f"✓ [{datetime.now().strftime('%H:%M:%S')}] 恢复运行\n")
    
    def _wait_for_allowed_time(self):
        """等待到允许的运行时间段"""
        while not self.is_allowed():
            current_time = datetime.now()
            current_hour = current_time.hour
            
            # 计算距离下次允许时间的小时数
            if self.start_hour > self.end_hour:
                if current_hour < self.start_hour and current_hour >= self.end_hour:
                    hours_to_wait = self.start_hour - current_hour
                else:
                    hours_to_wait = 1
            else:
                hours_to_wait = (self.start_hour - current_hour) if current_hour < self.start_hour else (24 - current_hour + self.start_hour)
            
            print(f"   当前时间：{current_time.strftime('%H:%M')}")
            print(f"   允许时段：{self.start_hour:02d}:00 - {self.end_hour:02d}:00")
            print(f"   预计等待：约 {hours_to_wait} 小时")
            print(f"   下次检查：5分钟后...\n")
            
            time.sleep(300)  # 等待5分钟
    
    def get_time_info(self) -> str:
        """
        获取时间信息字符串
        
        Returns:
            时间信息
        """
        if not self.enabled:
            return "无时间限制"
        
        return f"允许运行时段：{self.start_hour:02d}:00 - {self.end_hour:02d}:00"
