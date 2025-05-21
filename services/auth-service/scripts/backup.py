#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库备份脚本

提供PostgreSQL数据库的定期自动备份和恢复功能
支持增量备份和完整备份
"""
import argparse
import datetime
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("backup.log")]
)
logger = logging.getLogger("db-backup")

# 默认配置
DEFAULT_BACKUP_DIR = os.environ.get("BACKUP_DIR", "/var/backups/auth-service")
DEFAULT_RETENTION_DAYS = int(os.environ.get("BACKUP_RETENTION_DAYS", "30"))
DEFAULT_DB_HOST = os.environ.get("DB_HOST", "localhost")
DEFAULT_DB_PORT = os.environ.get("DB_PORT", "5432")
DEFAULT_DB_NAME = os.environ.get("DB_NAME", "auth_db")
DEFAULT_DB_USER = os.environ.get("DB_USER", "postgres")


def create_backup_directory(backup_dir: str) -> None:
    """
    创建备份目录（如果不存在）
    
    Args:
        backup_dir: 备份目录路径
    """
    Path(backup_dir).mkdir(parents=True, exist_ok=True)
    logger.info(f"备份目录已确认: {backup_dir}")


def perform_full_backup(
    backup_dir: str,
    db_host: str,
    db_port: str,
    db_name: str,
    db_user: str
) -> Optional[str]:
    """
    执行完整备份
    
    Args:
        backup_dir: 备份目录
        db_host: 数据库主机
        db_port: 数据库端口
        db_name: 数据库名称
        db_user: 数据库用户
        
    Returns:
        备份文件路径或None（失败时）
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"full_backup_{db_name}_{timestamp}.sql")
    
    try:
        # 使用pg_dump执行完整备份
        cmd = [
            "pg_dump",
            f"--host={db_host}",
            f"--port={db_port}",
            f"--username={db_user}",
            "--format=custom",
            f"--file={backup_file}",
            db_name
        ]
        
        logger.info(f"开始完整备份: {' '.join(cmd)}")
        process = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        logger.info(f"完整备份成功: {backup_file}")
        return backup_file
    
    except subprocess.CalledProcessError as e:
        logger.error(f"备份失败: {e.stderr}")
        return None


def perform_incremental_backup(
    backup_dir: str,
    db_host: str,
    db_port: str,
    db_name: str,
    db_user: str
) -> Optional[str]:
    """
    执行增量备份（WAL文件）
    
    Args:
        backup_dir: 备份目录
        db_host: 数据库主机
        db_port: 数据库端口
        db_name: 数据库名称
        db_user: 数据库用户
        
    Returns:
        备份文件路径或None（失败时）
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    wal_dir = os.path.join(backup_dir, "wal_archives")
    Path(wal_dir).mkdir(exist_ok=True)
    
    try:
        # 使用pg_basebackup执行WAL归档
        cmd = [
            "pg_basebackup",
            f"--host={db_host}",
            f"--port={db_port}",
            f"--username={db_user}",
            "--wal-method=fetch",
            f"--pgdata={wal_dir}",
            "--format=tar",
            "--gzip",
            "--label", f"auth_incremental_{timestamp}"
        ]
        
        logger.info(f"开始增量备份: {' '.join(cmd)}")
        process = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        logger.info(f"增量备份成功: {wal_dir}")
        return wal_dir
    
    except subprocess.CalledProcessError as e:
        logger.error(f"增量备份失败: {e.stderr}")
        return None


def restore_backup(
    backup_file: str,
    db_host: str,
    db_port: str,
    db_name: str,
    db_user: str
) -> bool:
    """
    从备份文件恢复数据库
    
    Args:
        backup_file: 备份文件路径
        db_host: 数据库主机
        db_port: 数据库端口
        db_name: 数据库名称
        db_user: 数据库用户
        
    Returns:
        恢复是否成功
    """
    try:
        # 使用pg_restore恢复备份
        cmd = [
            "pg_restore",
            f"--host={db_host}",
            f"--port={db_port}",
            f"--username={db_user}",
            "--clean",
            "--if-exists",
            f"--dbname={db_name}",
            backup_file
        ]
        
        logger.info(f"开始恢复备份: {' '.join(cmd)}")
        process = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        logger.info(f"备份恢复成功: {backup_file}")
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"恢复失败: {e.stderr}")
        return False


def cleanup_old_backups(backup_dir: str, retention_days: int) -> None:
    """
    清理超过保留期的旧备份
    
    Args:
        backup_dir: 备份目录
        retention_days: 保留天数
    """
    logger.info(f"开始清理超过 {retention_days} 天的旧备份...")
    retention_seconds = retention_days * 86400  # 转换为秒
    current_time = datetime.datetime.now().timestamp()
    
    for root, _, files in os.walk(backup_dir):
        for file in files:
            if file.endswith('.sql') or file.endswith('.tar.gz'):
                file_path = os.path.join(root, file)
                file_mtime = os.path.getmtime(file_path)
                
                # 如果文件超过保留期，则删除
                if current_time - file_mtime > retention_seconds:
                    logger.info(f"删除旧备份: {file_path}")
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        logger.error(f"删除文件失败: {e}")


def main():
    """主函数，处理命令行参数并执行操作"""
    parser = argparse.ArgumentParser(description="PostgreSQL数据库备份与恢复工具")
    
    # 操作类型
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--full", action="store_true", help="执行完整备份")
    group.add_argument("--incremental", action="store_true", help="执行增量备份")
    group.add_argument("--restore", type=str, help="从指定文件恢复备份", metavar="BACKUP_FILE")
    group.add_argument("--cleanup", action="store_true", help="清理旧备份")
    
    # 配置参数
    parser.add_argument("--backup-dir", default=DEFAULT_BACKUP_DIR, help="备份目录")
    parser.add_argument("--retention-days", type=int, default=DEFAULT_RETENTION_DAYS, help="备份保留天数")
    parser.add_argument("--db-host", default=DEFAULT_DB_HOST, help="数据库主机")
    parser.add_argument("--db-port", default=DEFAULT_DB_PORT, help="数据库端口")
    parser.add_argument("--db-name", default=DEFAULT_DB_NAME, help="数据库名称")
    parser.add_argument("--db-user", default=DEFAULT_DB_USER, help="数据库用户")
    
    args = parser.parse_args()
    
    # 确保备份目录存在
    create_backup_directory(args.backup_dir)
    
    # 根据命令行参数执行相应操作
    if args.full:
        logger.info("开始执行完整备份...")
        backup_file = perform_full_backup(
            args.backup_dir,
            args.db_host,
            args.db_port,
            args.db_name,
            args.db_user
        )
        if not backup_file:
            sys.exit(1)
    
    elif args.incremental:
        logger.info("开始执行增量备份...")
        backup_dir = perform_incremental_backup(
            args.backup_dir,
            args.db_host,
            args.db_port,
            args.db_name,
            args.db_user
        )
        if not backup_dir:
            sys.exit(1)
    
    elif args.restore:
        logger.info(f"开始从 {args.restore} 恢复备份...")
        success = restore_backup(
            args.restore,
            args.db_host,
            args.db_port,
            args.db_name,
            args.db_user
        )
        if not success:
            sys.exit(1)
    
    elif args.cleanup:
        logger.info("开始清理旧备份...")
        cleanup_old_backups(args.backup_dir, args.retention_days)
    
    logger.info("操作完成")


if __name__ == "__main__":
    main() 