#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API密钥管理模块
===========
负责API密钥的生成、验证、轮换和废弃
"""

import os
import json
import time
import secrets
import hmac
import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from loguru import logger
import threading
import schedule

class ApiKeyManager:
    """API密钥管理器"""
    
    def __init__(self, 
                 config_path: str = None, 
                 auto_rotate: bool = True,
                 rotation_days: int = 90,
                 overlap_days: int = 7):
        """初始化API密钥管理器
        
        Args:
            config_path: 密钥配置文件路径
            auto_rotate: 是否启用自动轮换
            rotation_days: 密钥轮换周期（天）
            overlap_days: 新旧密钥重叠期（天）
        """
        self.config_path = config_path or os.environ.get(
            "API_KEYS_CONFIG", "/etc/suoke/rag-service/api_keys.json")
        self.rotation_days = rotation_days
        self.overlap_days = overlap_days
        self.auto_rotate = auto_rotate
        
        # 密钥数据结构
        self.keys: Dict[str, Dict] = {}
        
        # 加载密钥配置
        self._load_keys()
        
        # 如果没有密钥，创建一个
        if not self.keys:
            self.generate_key(description="初始密钥")
            
        # 启动自动轮换定时任务
        if self.auto_rotate:
            self._setup_auto_rotation()
    
    def _load_keys(self) -> None:
        """从配置文件加载密钥"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.keys = json.load(f)
                logger.info(f"从 {self.config_path} 加载了 {len(self.keys)} 个API密钥")
            else:
                logger.warning(f"API密钥配置文件不存在: {self.config_path}")
                self.keys = {}
        except Exception as e:
            logger.error(f"加载API密钥配置失败: {e}")
            self.keys = {}
    
    def _save_keys(self) -> None:
        """保存密钥到配置文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # 保存到临时文件，然后原子重命名
            temp_path = f"{self.config_path}.tmp"
            with open(temp_path, 'w') as f:
                json.dump(self.keys, f, indent=2)
            
            os.rename(temp_path, self.config_path)
            os.chmod(self.config_path, 0o600)  # 安全权限
            logger.info(f"API密钥配置已保存到 {self.config_path}")
        except Exception as e:
            logger.error(f"保存API密钥配置失败: {e}")
    
    def generate_key(self, description: str = "", expires_in_days: int = None) -> str:
        """生成新的API密钥
        
        Args:
            description: 密钥描述
            expires_in_days: 过期天数，如果为None则使用默认轮换周期
            
        Returns:
            str: 新生成的API密钥
        """
        # 生成随机密钥
        api_key = secrets.token_hex(32)
        
        # 计算密钥哈希 (用于内部存储)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # 设置过期时间
        if expires_in_days is None:
            expires_in_days = self.rotation_days
        
        expiry = None
        if expires_in_days > 0:
            expiry = (datetime.now() + timedelta(days=expires_in_days)).isoformat()
        
        # 保存密钥信息
        self.keys[key_hash] = {
            "created_at": datetime.now().isoformat(),
            "expires_at": expiry,
            "description": description,
            "status": "active"
        }
        
        # 保存配置
        self._save_keys()
        
        logger.info(f"已生成新的API密钥: {self._mask_key(api_key)}")
        return api_key
    
    def validate_key(self, api_key: str) -> bool:
        """验证API密钥是否有效
        
        Args:
            api_key: 待验证的API密钥
            
        Returns:
            bool: 密钥是否有效
        """
        if not api_key:
            return False
        
        # 计算密钥哈希
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # 检查密钥是否存在
        if key_hash not in self.keys:
            return False
        
        key_info = self.keys[key_hash]
        
        # 检查密钥状态
        if key_info.get("status") != "active":
            return False
        
        # 检查密钥是否过期
        expiry = key_info.get("expires_at")
        if expiry and datetime.fromisoformat(expiry) < datetime.now():
            # 自动将过期密钥标记为废弃
            key_info["status"] = "expired"
            self._save_keys()
            return False
        
        return True
    
    def rotate_keys(self) -> Tuple[str, List[str]]:
        """执行密钥轮换，生成新密钥并废弃过期密钥
        
        Returns:
            Tuple[str, List[str]]: 新密钥和被废弃的密钥列表
        """
        logger.info("执行API密钥轮换")
        
        # 生成新密钥
        new_key = self.generate_key(
            description=f"自动轮换 {datetime.now().strftime('%Y-%m-%d')}",
            expires_in_days=self.rotation_days
        )
        
        # 找出需要废弃的密钥
        revoked_keys = []
        now = datetime.now()
        for key_hash, info in list(self.keys.items()):
            # 已经不是活跃状态的密钥跳过
            if info.get("status") != "active":
                continue
                
            # 检查过期时间
            expiry = info.get("expires_at")
            if expiry and datetime.fromisoformat(expiry) < now:
                # 标记为过期
                info["status"] = "expired"
                logger.info(f"密钥已过期: {key_hash[:8]}...")
                revoked_keys.append(key_hash)
        
        # 保存更改
        self._save_keys()
        
        return new_key, revoked_keys
    
    def revoke_key(self, api_key: str) -> bool:
        """撤销特定的API密钥
        
        Args:
            api_key: 要撤销的API密钥
            
        Returns:
            bool: 是否成功撤销
        """
        # 计算密钥哈希
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # 检查密钥是否存在
        if key_hash not in self.keys:
            logger.warning(f"尝试撤销不存在的API密钥")
            return False
        
        # 标记为已撤销
        self.keys[key_hash]["status"] = "revoked"
        self.keys[key_hash]["revoked_at"] = datetime.now().isoformat()
        
        # 保存更改
        self._save_keys()
        
        logger.info(f"已撤销API密钥: {self._mask_key(api_key)}")
        return True
    
    def list_keys(self) -> List[Dict]:
        """列出所有密钥信息（不包含实际密钥值）
        
        Returns:
            List[Dict]: 密钥信息列表
        """
        return [
            {
                "id": key_hash[:8],
                **{k: v for k, v in info.items() if k != "key"}
            }
            for key_hash, info in self.keys.items()
        ]
    
    def _mask_key(self, api_key: str) -> str:
        """遮蔽API密钥，仅显示部分字符
        
        Args:
            api_key: 完整API密钥
            
        Returns:
            str: 遮蔽后的API密钥
        """
        if len(api_key) <= 8:
            return "****"
        return f"{api_key[:4]}...{api_key[-4:]}"
    
    def _setup_auto_rotation(self) -> None:
        """设置自动轮换定时任务"""
        def rotation_job():
            try:
                self.rotate_keys()
                logger.info("自动API密钥轮换已完成")
            except Exception as e:
                logger.error(f"自动API密钥轮换失败: {e}")
        
        # 每天检查是否需要轮换
        schedule.every().day.at("03:00").do(rotation_job)
        
        # 在后台线程中运行调度器
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(3600)  # 每小时检查一次
        
        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()
        logger.info(f"API密钥自动轮换已启动，周期: {self.rotation_days}天，重叠期: {self.overlap_days}天")

# 单例实例
_key_manager = None

def get_key_manager() -> ApiKeyManager:
    """获取API密钥管理器单例"""
    global _key_manager
    if _key_manager is None:
        _key_manager = ApiKeyManager()
    return _key_manager

if __name__ == "__main__":
    # 命令行工具
    import argparse
    
    parser = argparse.ArgumentParser(description="API密钥管理工具")
    parser.add_argument("action", choices=["generate", "validate", "rotate", "revoke", "list"],
                        help="要执行的操作")
    parser.add_argument("--key", help="用于验证或撤销的API密钥")
    parser.add_argument("--description", default="", help="新密钥的描述")
    parser.add_argument("--expires", type=int, default=None, help="密钥过期天数")
    parser.add_argument("--config", default=None, help="密钥配置文件路径")
    
    args = parser.parse_args()
    
    # 初始化密钥管理器
    manager = ApiKeyManager(config_path=args.config)
    
    if args.action == "generate":
        key = manager.generate_key(description=args.description, expires_in_days=args.expires)
        print(f"已生成新的API密钥: {key}")
    
    elif args.action == "validate":
        if not args.key:
            print("错误: 验证操作需要指定 --key 参数")
            exit(1)
        
        valid = manager.validate_key(args.key)
        print(f"密钥验证结果: {'有效' if valid else '无效'}")
    
    elif args.action == "rotate":
        new_key, revoked = manager.rotate_keys()
        print(f"已生成新的API密钥: {new_key}")
        if revoked:
            print(f"已废弃 {len(revoked)} 个过期密钥")
    
    elif args.action == "revoke":
        if not args.key:
            print("错误: 撤销操作需要指定 --key 参数")
            exit(1)
        
        success = manager.revoke_key(args.key)
        if success:
            print("密钥已成功撤销")
        else:
            print("密钥撤销失败")
    
    elif args.action == "list":
        keys = manager.list_keys()
        print(f"共有 {len(keys)} 个API密钥:")
        for i, key_info in enumerate(keys, 1):
            status = key_info.get("status", "unknown")
            created = key_info.get("created_at", "unknown")
            expires = key_info.get("expires_at", "never")
            desc = key_info.get("description", "")
            
            print(f"{i}. ID: {key_info['id']}, 状态: {status}, 创建: {created}, 过期: {expires}")
            if desc:
                print(f"   描述: {desc}")
            print("") 