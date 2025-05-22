"""
SQLite数据库管理器

提供优化的SQLite数据库连接和操作，适用于索克生活APP移动端本地存储。
主要功能：
1. WAL模式支持
2. 连接池管理
3. 异步操作支持
4. 自动备份和恢复
5. 数据同步接口
"""

import asyncio
import json
import logging
import os
import shutil
import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import aiosqlite
from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

class SQLiteManager:
    """SQLite数据库管理器"""
    
    def __init__(self, db_path: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化SQLite管理器
        
        Args:
            db_path: 数据库文件路径
            config: 数据库配置
        """
        self.db_path = db_path
        self.db_dir = os.path.dirname(db_path)
        self.config = config or {}
        
        # 确保数据库目录存在
        os.makedirs(self.db_dir, exist_ok=True)
        
        # 连接配置
        self.journal_mode = self.config.get("journal_mode", "WAL")
        self.synchronous = self.config.get("synchronous", "NORMAL")
        self.busy_timeout = self.config.get("busy_timeout", 5000)  # 毫秒
        self.cache_size = self.config.get("cache_size", 2000)  # 页数
        self.temp_store = self.config.get("temp_store", "MEMORY")  # MEMORY或FILE
        
        # 备份配置
        self.backup_enabled = self.config.get("backup", {}).get("enabled", True)
        self.backup_interval = self.config.get("backup", {}).get("interval", 24 * 60 * 60)  # 默认1天
        self.max_backups = self.config.get("backup", {}).get("max_count", 5)
        
        # 初始化数据库
        self._initialize_db()
        
        # 启动定时备份
        if self.backup_enabled:
            self._schedule_backup()
    
    def _initialize_db(self):
        """初始化数据库连接和优化设置"""
        try:
            with self._get_connection() as conn:
                # 设置日志模式
                conn.execute(f"PRAGMA journal_mode = {self.journal_mode}")
                
                # 设置同步模式
                conn.execute(f"PRAGMA synchronous = {self.synchronous}")
                
                # 设置缓存大小
                conn.execute(f"PRAGMA cache_size = {self.cache_size}")
                
                # 设置临时存储位置
                conn.execute(f"PRAGMA temp_store = {self.temp_store}")
                
                # 启用外键约束
                conn.execute("PRAGMA foreign_keys = ON")
                
                logger.info(f"SQLite数据库初始化成功: {self.db_path}")
                
                # 获取数据库状态
                journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
                page_size = conn.execute("PRAGMA page_size").fetchone()[0]
                
                logger.info(f"SQLite设置: 日志模式={journal_mode}, 页大小={page_size}字节")
        except Exception as e:
            logger.error(f"初始化SQLite数据库失败: {str(e)}")
            raise
    
    @contextmanager
    def _get_connection(self) -> sqlite3.Connection:
        """
        获取SQLite连接
        
        Returns:
            sqlite3.Connection对象
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=self.busy_timeout/1000)
            conn.row_factory = sqlite3.Row
            yield conn
        finally:
            if conn:
                conn.close()
    
    async def _get_async_connection(self) -> aiosqlite.Connection:
        """
        获取异步SQLite连接
        
        Returns:
            aiosqlite.Connection对象
        """
        conn = await aiosqlite.connect(self.db_path, timeout=self.busy_timeout/1000)
        conn.row_factory = aiosqlite.Row
        
        # 设置PRAGMA
        await conn.execute(f"PRAGMA journal_mode = {self.journal_mode}")
        await conn.execute(f"PRAGMA synchronous = {self.synchronous}")
        await conn.execute(f"PRAGMA cache_size = {self.cache_size}")
        await conn.execute("PRAGMA foreign_keys = ON")
        
        return conn
    
    def execute(self, query: str, params: Optional[Union[Tuple, Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        执行SQL查询
        
        Args:
            query: SQL查询
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        with tracer.start_as_current_span("sqlite_execute") as span:
            span.set_attribute("db.system", "sqlite")
            span.set_attribute("db.statement", query)
            
            if params:
                span.set_attribute("db.params", str(params))
            
            start_time = time.time()
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                
                # 检查是否为SELECT查询
                if query.strip().upper().startswith("SELECT"):
                    rows = cursor.fetchall()
                    result = [dict(row) for row in rows]
                else:
                    conn.commit()
                    result = [{"affected_rows": cursor.rowcount}]
                
                # 记录查询性能
                query_time = (time.time() - start_time) * 1000  # 毫秒
                span.set_attribute("db.query.time_ms", query_time)
                
                return result
    
    async def execute_async(self, query: str, params: Optional[Union[Tuple, Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        异步执行SQL查询
        
        Args:
            query: SQL查询
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        with tracer.start_as_current_span("sqlite_execute_async") as span:
            span.set_attribute("db.system", "sqlite")
            span.set_attribute("db.statement", query)
            
            if params:
                span.set_attribute("db.params", str(params))
            
            start_time = time.time()
            
            conn = await self._get_async_connection()
            try:
                cursor = await conn.execute(query, params or ())
                
                # 检查是否为SELECT查询
                if query.strip().upper().startswith("SELECT"):
                    rows = await cursor.fetchall()
                    result = [dict(row) for row in rows]
                else:
                    await conn.commit()
                    result = [{"affected_rows": cursor.rowcount}]
                
                # 记录查询性能
                query_time = (time.time() - start_time) * 1000  # 毫秒
                span.set_attribute("db.query.time_ms", query_time)
                
                return result
            finally:
                await conn.close()
    
    def execute_batch(self, queries: List[Tuple[str, Optional[Union[Tuple, Dict[str, Any]]]]]) -> List[Dict[str, Any]]:
        """
        批量执行SQL查询
        
        Args:
            queries: 查询列表，每个元素为(query, params)元组
            
        Returns:
            每个查询的结果列表
        """
        with tracer.start_as_current_span("sqlite_execute_batch") as span:
            span.set_attribute("db.system", "sqlite")
            span.set_attribute("db.statements_count", len(queries))
            
            start_time = time.time()
            results = []
            
            with self._get_connection() as conn:
                for i, (query, params) in enumerate(queries):
                    cursor = conn.cursor()
                    cursor.execute(query, params or ())
                    
                    # 检查是否为SELECT查询
                    if query.strip().upper().startswith("SELECT"):
                        rows = cursor.fetchall()
                        query_result = [dict(row) for row in rows]
                    else:
                        query_result = [{"affected_rows": cursor.rowcount}]
                    
                    results.append(query_result)
                
                # 提交所有更改
                conn.commit()
            
            # 记录总执行时间
            total_time = (time.time() - start_time) * 1000  # 毫秒
            span.set_attribute("db.batch.total_time_ms", total_time)
            
            return results
    
    async def execute_batch_async(self, queries: List[Tuple[str, Optional[Union[Tuple, Dict[str, Any]]]]]) -> List[Dict[str, Any]]:
        """
        异步批量执行SQL查询
        
        Args:
            queries: 查询列表，每个元素为(query, params)元组
            
        Returns:
            每个查询的结果列表
        """
        with tracer.start_as_current_span("sqlite_execute_batch_async") as span:
            span.set_attribute("db.system", "sqlite")
            span.set_attribute("db.statements_count", len(queries))
            
            start_time = time.time()
            results = []
            
            conn = await self._get_async_connection()
            try:
                for i, (query, params) in enumerate(queries):
                    cursor = await conn.execute(query, params or ())
                    
                    # 检查是否为SELECT查询
                    if query.strip().upper().startswith("SELECT"):
                        rows = await cursor.fetchall()
                        query_result = [dict(row) for row in rows]
                    else:
                        query_result = [{"affected_rows": cursor.rowcount}]
                    
                    results.append(query_result)
                
                # 提交所有更改
                await conn.commit()
            finally:
                await conn.close()
            
            # 记录总执行时间
            total_time = (time.time() - start_time) * 1000  # 毫秒
            span.set_attribute("db.batch.total_time_ms", total_time)
            
            return results
    
    def backup_db(self, backup_path: Optional[str] = None) -> str:
        """
        备份数据库
        
        Args:
            backup_path: 备份文件路径，如果为None则自动生成
            
        Returns:
            备份文件路径
        """
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(self.db_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, f"{os.path.basename(self.db_path)}.{timestamp}.bak")
        
        # 检查目标目录是否存在
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        with tracer.start_as_current_span("sqlite_backup") as span:
            span.set_attribute("db.backup.source", self.db_path)
            span.set_attribute("db.backup.destination", backup_path)
            
            start_time = time.time()
            
            try:
                # 执行备份
                with self._get_connection() as source_conn:
                    backup_conn = sqlite3.connect(backup_path)
                    source_conn.backup(backup_conn)
                    backup_conn.close()
                
                # 记录备份时间
                backup_time = time.time() - start_time
                span.set_attribute("db.backup.time_seconds", backup_time)
                logger.info(f"数据库备份成功: {backup_path}，耗时: {backup_time:.2f}秒")
                
                # 管理备份数量
                self._manage_backups()
                
                return backup_path
            except Exception as e:
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                logger.error(f"数据库备份失败: {str(e)}")
                raise
    
    def _manage_backups(self):
        """管理备份文件数量"""
        backup_dir = os.path.join(self.db_dir, "backups")
        if not os.path.exists(backup_dir):
            return
            
        # 获取所有备份文件
        backups = []
        for filename in os.listdir(backup_dir):
            if filename.startswith(os.path.basename(self.db_path)) and filename.endswith(".bak"):
                file_path = os.path.join(backup_dir, filename)
                backups.append((file_path, os.path.getmtime(file_path)))
        
        # 按修改时间排序
        backups.sort(key=lambda x: x[1], reverse=True)
        
        # 删除多余的备份
        if len(backups) > self.max_backups:
            for file_path, _ in backups[self.max_backups:]:
                try:
                    os.remove(file_path)
                    logger.info(f"删除旧备份文件: {file_path}")
                except Exception as e:
                    logger.error(f"删除备份文件失败: {file_path}, 错误: {str(e)}")
    
    def _schedule_backup(self):
        """调度定时备份"""
        def backup_task():
            while True:
                try:
                    time.sleep(self.backup_interval)
                    self.backup_db()
                except Exception as e:
                    logger.error(f"定时备份失败: {str(e)}")
        
        # 启动备份线程
        thread = threading.Thread(target=backup_task, daemon=True)
        thread.start()
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """
        从备份恢复数据库
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            恢复是否成功
        """
        with tracer.start_as_current_span("sqlite_restore") as span:
            span.set_attribute("db.restore.source", backup_path)
            span.set_attribute("db.restore.destination", self.db_path)
            
            start_time = time.time()
            
            # 先进行当前状态备份
            try:
                current_backup = self.backup_db()
                
                # 关闭所有连接
                self.close()
                
                # 复制备份文件到主数据库
                shutil.copy2(backup_path, self.db_path)
                
                # 如果使用WAL模式，需要删除相关文件
                wal_file = f"{self.db_path}-wal"
                shm_file = f"{self.db_path}-shm"
                
                if os.path.exists(wal_file):
                    os.remove(wal_file)
                    
                if os.path.exists(shm_file):
                    os.remove(shm_file)
                
                # 重新初始化数据库
                self._initialize_db()
                
                # 记录恢复时间
                restore_time = time.time() - start_time
                span.set_attribute("db.restore.time_seconds", restore_time)
                logger.info(f"数据库恢复成功，耗时: {restore_time:.2f}秒")
                
                return True
            except Exception as e:
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                logger.error(f"数据库恢复失败: {str(e)}")
                
                # 尝试回滚到刚才的备份
                try:
                    if 'current_backup' in locals():
                        logger.info(f"尝试回滚到当前状态备份: {current_backup}")
                        shutil.copy2(current_backup, self.db_path)
                        self._initialize_db()
                except Exception as rollback_error:
                    logger.error(f"回滚数据库失败: {str(rollback_error)}")
                
                return False
    
    def optimize(self):
        """优化数据库"""
        with tracer.start_as_current_span("sqlite_optimize") as span:
            start_time = time.time()
            
            try:
                with self._get_connection() as conn:
                    # 收集未使用的空间
                    conn.execute("VACUUM")
                    
                    # 分析查询优化
                    conn.execute("ANALYZE")
                    
                    # 优化索引
                    conn.execute("PRAGMA optimize")
                    
                    # 记录优化时间
                    optimize_time = time.time() - start_time
                    span.set_attribute("db.optimize.time_seconds", optimize_time)
                    logger.info(f"数据库优化完成，耗时: {optimize_time:.2f}秒")
                
                return True
            except Exception as e:
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                logger.error(f"数据库优化失败: {str(e)}")
                return False
    
    def get_db_stats(self) -> Dict[str, Any]:
        """
        获取数据库统计信息
        
        Returns:
            数据库统计信息
        """
        try:
            stats = {}
            
            with self._get_connection() as conn:
                # 基本信息
                stats["file_size"] = os.path.getsize(self.db_path)
                stats["journal_mode"] = conn.execute("PRAGMA journal_mode").fetchone()[0]
                stats["page_size"] = conn.execute("PRAGMA page_size").fetchone()[0]
                stats["page_count"] = conn.execute("PRAGMA page_count").fetchone()[0]
                stats["total_size"] = stats["page_size"] * stats["page_count"]
                stats["freelist_count"] = conn.execute("PRAGMA freelist_count").fetchone()[0]
                
                # 计算碎片率
                fragmentation = 0
                if stats["page_count"] > 0:
                    fragmentation = (stats["freelist_count"] / stats["page_count"]) * 100
                stats["fragmentation_percent"] = fragmentation
                
                # 获取所有表信息
                tables = []
                for table_info in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
                    table_name = table_info[0]
                    
                    # 获取表行数
                    row_count = conn.execute(f"SELECT COUNT(*) FROM '{table_name}'").fetchone()[0]
                    
                    # 获取表结构
                    columns = []
                    for column_info in conn.execute(f"PRAGMA table_info('{table_name}')"):
                        columns.append({
                            "name": column_info[1],
                            "type": column_info[2],
                            "notnull": bool(column_info[3]),
                            "pk": bool(column_info[5])
                        })
                    
                    # 获取索引信息
                    indices = []
                    for index_info in conn.execute(f"PRAGMA index_list('{table_name}')"):
                        index_name = index_info[1]
                        is_unique = bool(index_info[2])
                        
                        # 获取索引列
                        index_columns = []
                        for idx_col in conn.execute(f"PRAGMA index_info('{index_name}')"):
                            index_columns.append(idx_col[2])
                        
                        indices.append({
                            "name": index_name,
                            "unique": is_unique,
                            "columns": index_columns
                        })
                    
                    tables.append({
                        "name": table_name,
                        "row_count": row_count,
                        "columns": columns,
                        "indices": indices
                    })
                
                stats["tables"] = tables
                
                # WAL文件大小
                wal_file = f"{self.db_path}-wal"
                if os.path.exists(wal_file):
                    stats["wal_size"] = os.path.getsize(wal_file)
                else:
                    stats["wal_size"] = 0
                
                return stats
            
        except Exception as e:
            logger.error(f"获取数据库统计信息失败: {str(e)}")
            return {"error": str(e)}
    
    def export_json(self, tables: Optional[List[str]] = None, file_path: Optional[str] = None) -> str:
        """
        将数据库导出为JSON
        
        Args:
            tables: 要导出的表列表，如果为None则导出所有表
            file_path: 导出文件路径，如果为None则自动生成
            
        Returns:
            导出文件路径
        """
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_dir = os.path.join(self.db_dir, "exports")
            os.makedirs(export_dir, exist_ok=True)
            file_path = os.path.join(export_dir, f"{os.path.basename(self.db_path)}.{timestamp}.json")
        
        # 确保目标目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with tracer.start_as_current_span("sqlite_export_json") as span:
            span.set_attribute("db.export.source", self.db_path)
            span.set_attribute("db.export.destination", file_path)
            
            start_time = time.time()
            
            try:
                export_data = {}
                
                with self._get_connection() as conn:
                    # 获取所有表名
                    if tables is None:
                        tables = []
                        for table_info in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
                            tables.append(table_info[0])
                    
                    # 导出每个表的数据
                    for table in tables:
                        rows = []
                        for row in conn.execute(f"SELECT * FROM '{table}'"):
                            rows.append(dict(row))
                        export_data[table] = rows
                
                # 写入JSON文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                # 记录导出时间
                export_time = time.time() - start_time
                span.set_attribute("db.export.time_seconds", export_time)
                logger.info(f"数据库导出成功: {file_path}，耗时: {export_time:.2f}秒")
                
                return file_path
            except Exception as e:
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                logger.error(f"数据库导出失败: {str(e)}")
                raise
    
    def import_json(self, file_path: str) -> bool:
        """
        从JSON导入数据到数据库
        
        Args:
            file_path: 导入文件路径
            
        Returns:
            导入是否成功
        """
        with tracer.start_as_current_span("sqlite_import_json") as span:
            span.set_attribute("db.import.source", file_path)
            span.set_attribute("db.import.destination", self.db_path)
            
            start_time = time.time()
            
            try:
                # 先备份当前数据库
                self.backup_db()
                
                # 读取JSON文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    import_data = json.load(f)
                
                with self._get_connection() as conn:
                    # 导入每个表的数据
                    for table, rows in import_data.items():
                        # 检查表是否存在
                        table_exists = conn.execute(
                            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
                            (table,)
                        ).fetchone()
                        
                        if not table_exists:
                            logger.warning(f"表 {table} 不存在，跳过导入")
                            continue
                        
                        # 获取表的列名
                        columns = []
                        for column_info in conn.execute(f"PRAGMA table_info('{table}')"):
                            columns.append(column_info[1])
                        
                        # 清空表
                        conn.execute(f"DELETE FROM '{table}'")
                        
                        # 批量插入数据
                        for row in rows:
                            # 过滤掉不在表中的列
                            row_data = {k: v for k, v in row.items() if k in columns}
                            
                            if not row_data:
                                continue
                                
                            # 构建INSERT语句
                            columns_str = ', '.join([f"'{col}'" for col in row_data.keys()])
                            placeholders = ', '.join(['?' for _ in row_data])
                            query = f"INSERT INTO '{table}' ({columns_str}) VALUES ({placeholders})"
                            
                            # 执行插入
                            conn.execute(query, list(row_data.values()))
                    
                    # 提交事务
                    conn.commit()
                
                # 记录导入时间
                import_time = time.time() - start_time
                span.set_attribute("db.import.time_seconds", import_time)
                logger.info(f"数据库导入成功，耗时: {import_time:.2f}秒")
                
                return True
            except Exception as e:
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                logger.error(f"数据库导入失败: {str(e)}")
                return False
    
    def close(self):
        """关闭数据库连接"""
        # 由于使用的是上下文管理器，不需要显式关闭连接
        pass 