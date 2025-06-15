"""
容灾备份机制服务 - 提供数据备份、恢复和容灾能力
"""

import datetime
import json
import logging
import os
import shutil
import threading
import time
from typing import Any

logger = logging.getLogger(__name__)


class BackupScheduler:
    """备份调度器 - 负责管理定时备份任务"""

    def __init__(self, config):
        """初始化备份调度器

        Args:
            config: 配置对象
        """
        self.config = config

        # 安全获取备份配置
        try:
            self.backup_enabled = config.resilience.backup.enabled
        except AttributeError:
            self.backup_enabled = False
            logger.warning("未找到备份启用配置，备份功能将被禁用")

        # 如果备份功能禁用，使用默认值
        if not self.backup_enabled:
            logger.info("备份功能已禁用，使用默认配置值")
            self.backup_schedule = {}
            self.backup_path = "/tmp/backups"
            self.max_backups = 5
        else:
            # 安全获取其他备份配置
            try:
                self.backup_schedule = config.resilience.backup.schedule
            except AttributeError:
                self.backup_schedule = {}
                logger.warning("未找到备份计划配置，使用空计划")

            try:
                self.backup_path = config.resilience.backup.path
            except AttributeError:
                self.backup_path = "/tmp/backups"
                logger.warning(f"未找到备份路径配置，使用默认路径: {self.backup_path}")

            try:
                self.max_backups = config.resilience.backup.max_backups
            except AttributeError:
                self.max_backups = 5
                logger.warning(f"未找到最大备份数配置，使用默认值: {self.max_backups}")

        self.jobs = {}
        self.running = False
        self.scheduler_thread = None
        logger.info("初始化备份调度器")

    def start(self) -> None:
        """启动备份调度器"""
        if not self.backup_enabled:
            logger.info("备份功能已禁用，不启动备份调度器")
            return

        logger.info("启动备份调度器")
        self.running = True

        # 创建备份目录
        self._ensure_backup_dir()

        # 启动调度器线程
        self.scheduler_thread = threading.Thread(
            target=self._run_scheduler, daemon=True
        )
        self.scheduler_thread.start()

    def stop(self) -> None:
        """停止备份调度器"""
        if not self.running:
            return

        logger.info("停止备份调度器")
        self.running = False

        # 等待调度器线程结束
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)

    def _ensure_backup_dir(self) -> None:
        """确保备份目录存在"""
        if not os.path.exists(self.backup_path):
            logger.info(f"创建备份目录: {self.backup_path}")
            os.makedirs(self.backup_path, exist_ok=True)

    def _run_scheduler(self) -> None:
        """运行调度器线程"""
        logger.info("备份调度器线程启动")

        while self.running:
            # 检查需要运行的备份任务
            self._check_scheduled_backups()

            # 清理过期备份
            self._cleanup_old_backups()

            # 休眠60秒
            time.sleep(60)

    def _check_scheduled_backups(self) -> None:
        """检查和执行计划中的备份任务"""
        now = datetime.datetime.now()

        for job_name, job_config in self.backup_schedule.items():
            # 解析备份时间
            backup_time = self._parse_backup_time(job_config.get("time", "00:00"))

            # 获取上次运行时间
            last_run = job_config.get("last_run", None)

            # 检查是否应该运行
            if self._should_run_backup(job_name, job_config, now):
                logger.info(f"启动计划备份任务: {job_name}")

                # 执行备份
                try:
                    backup_type = job_config.get("type", "full")
                    self._run_backup(job_name, backup_type)

                    # 更新上次运行时间
                    self.backup_schedule[job_name]["last_run"] = now.isoformat()
                except Exception as e:
                    logger.error(f"执行备份任务 {job_name} 失败: {e!s}")

    def _parse_backup_time(self, time_str: str) -> tuple[int, int]:
        """解析备份时间

        Args:
            time_str: 时间字符串 (HH:MM)

        Returns:
            Tuple[int, int]: (小时, 分钟)
        """
        try:
            hour, minute = time_str.split(":")
            return int(hour), int(minute)
        except:
            logger.warning(f"无效的备份时间格式: {time_str}，使用默认值 00:00")
            return 0, 0

    def _should_run_backup(
        self, job_name: str, job_config: dict[str, Any], current_time: datetime.datetime
    ) -> bool:
        """检查是否应该运行备份任务

        Args:
            job_name: 任务名称
            job_config: 任务配置
            current_time: 当前时间

        Returns:
            bool: 是否应该运行
        """
        # 检查频率
        frequency = job_config.get("frequency", "daily")

        # 获取上次运行时间
        last_run_str = job_config.get("last_run")
        if not last_run_str:
            logger.info(f"备份任务 {job_name} 从未运行过，应该运行")
            return True

        try:
            last_run = datetime.datetime.fromisoformat(last_run_str)
        except:
            logger.warning(f"解析上次运行时间失败: {last_run_str}，将重新运行")
            return True

        # 获取计划时间
        hour, minute = self._parse_backup_time(job_config.get("time", "00:00"))

        # 根据频率检查是否应该运行
        if frequency == "hourly":
            # 检查是否过了一个小时
            delta = current_time - last_run
            return delta.total_seconds() >= 3600
        elif frequency == "daily":
            # 检查是否是新的一天，且时间已过
            is_new_day = current_time.date() > last_run.date()
            time_passed = current_time.hour > hour or (
                current_time.hour == hour and current_time.minute >= minute
            )
            return is_new_day and time_passed
        elif frequency == "weekly":
            # 检查是否是新的一周，且时间已过
            is_new_week = (current_time.date() - last_run.date()).days >= 7
            time_passed = current_time.hour > hour or (
                current_time.hour == hour and current_time.minute >= minute
            )
            return is_new_week and time_passed
        elif frequency == "monthly":
            # 检查是否是新的一月，且时间已过
            is_new_month = current_time.month > last_run.month or (
                current_time.month == last_run.month
                and current_time.year > last_run.year
            )
            time_passed = current_time.hour > hour or (
                current_time.hour == hour and current_time.minute >= minute
            )
            return is_new_month and time_passed

        return False

    def _run_backup(self, job_name: str, backup_type: str) -> str:
        """执行备份任务

        Args:
            job_name: 任务名称
            backup_type: 备份类型 (full/incremental/differential)

        Returns:
            str: 备份ID
        """
        logger.info(f"执行备份任务 {job_name}，类型: {backup_type}")

        # 创建备份ID
        backup_id = (
            f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{job_name}"
        )

        # 确定备份目标路径
        backup_dir = os.path.join(self.backup_path, backup_id)
        os.makedirs(backup_dir, exist_ok=True)

        # 创建备份元数据
        metadata = {
            "id": backup_id,
            "type": backup_type,
            "job_name": job_name,
            "created_at": datetime.datetime.now().isoformat(),
            "status": "running",
            "files": [],
        }

        # 保存元数据
        self._save_metadata(backup_id, metadata)

        try:
            # 执行实际备份
            if backup_type == "full":
                file_count = self._perform_full_backup(backup_dir, metadata)
            elif backup_type == "incremental":
                file_count = self._perform_incremental_backup(backup_dir, metadata)
            elif backup_type == "differential":
                file_count = self._perform_differential_backup(backup_dir, metadata)
            else:
                logger.warning(f"未知的备份类型: {backup_type}，执行完整备份")
                file_count = self._perform_full_backup(backup_dir, metadata)

            # 更新元数据
            metadata["status"] = "completed"
            metadata["completed_at"] = datetime.datetime.now().isoformat()
            metadata["file_count"] = file_count
            self._save_metadata(backup_id, metadata)

            logger.info(f"备份任务 {job_name} 完成，共备份 {file_count} 个文件")
            return backup_id
        except Exception as e:
            logger.error(f"备份任务 {job_name} 失败: {e!s}")

            # 更新元数据
            metadata["status"] = "failed"
            metadata["error"] = str(e)
            self._save_metadata(backup_id, metadata)

            return backup_id

    def _perform_full_backup(self, backup_dir: str, metadata: dict[str, Any]) -> int:
        """执行完整备份

        Args:
            backup_dir: 备份目录
            metadata: 备份元数据

        Returns:
            int: 备份的文件数
        """
        # 获取要备份的目录
        data_dirs = self.config.resilience.backup.backup_items
        file_count = 0

        for src_dir in data_dirs:
            if not os.path.exists(src_dir):
                logger.warning(f"备份源目录不存在: {src_dir}")
                continue

            # 创建目标目录
            rel_path = os.path.relpath(src_dir, self.config.service.data_root)
            dst_dir = os.path.join(backup_dir, rel_path)
            os.makedirs(os.path.dirname(dst_dir), exist_ok=True)

            # 复制目录内容
            logger.info(f"备份目录: {src_dir} -> {dst_dir}")
            if os.path.isdir(src_dir):
                file_count += self._copy_directory(src_dir, dst_dir, metadata)
            else:
                self._copy_file(src_dir, dst_dir, metadata)
                file_count += 1

        return file_count

    def _perform_incremental_backup(
        self, backup_dir: str, metadata: dict[str, Any]
    ) -> int:
        """执行增量备份（只备份上次备份后修改的文件）

        Args:
            backup_dir: 备份目录
            metadata: 备份元数据

        Returns:
            int: 备份的文件数
        """
        # 查找上次成功的备份
        last_backup = self._find_last_backup(metadata["job_name"])
        if not last_backup:
            logger.warning("找不到上次备份，执行完整备份")
            return self._perform_full_backup(backup_dir, metadata)

        # 记录上次备份ID
        metadata["parent_backup"] = last_backup["id"]

        # 获取上次备份时间
        last_backup_time = datetime.datetime.fromisoformat(last_backup["completed_at"])
        last_backup_timestamp = last_backup_time.timestamp()

        # 获取要备份的目录
        data_dirs = self.config.resilience.backup.backup_items
        file_count = 0

        for src_dir in data_dirs:
            if not os.path.exists(src_dir):
                logger.warning(f"备份源目录不存在: {src_dir}")
                continue

            # 创建目标目录
            rel_path = os.path.relpath(src_dir, self.config.service.data_root)
            dst_dir = os.path.join(backup_dir, rel_path)
            os.makedirs(os.path.dirname(dst_dir), exist_ok=True)

            # 复制目录内容
            logger.info(f"增量备份目录: {src_dir} -> {dst_dir}")
            if os.path.isdir(src_dir):
                file_count += self._copy_directory(
                    src_dir,
                    dst_dir,
                    metadata,
                    last_modified_after=last_backup_timestamp,
                )
            else:
                # 检查文件修改时间
                file_mtime = os.path.getmtime(src_dir)
                if file_mtime > last_backup_timestamp:
                    self._copy_file(src_dir, dst_dir, metadata)
                    file_count += 1

        return file_count

    def _perform_differential_backup(
        self, backup_dir: str, metadata: dict[str, Any]
    ) -> int:
        """执行差异备份（相对于最后一次完整备份的所有修改）

        Args:
            backup_dir: 备份目录
            metadata: 备份元数据

        Returns:
            int: 备份的文件数
        """
        # 查找上次成功的完整备份
        last_full_backup = self._find_last_backup(
            metadata["job_name"], backup_type="full"
        )
        if not last_full_backup:
            logger.warning("找不到上次完整备份，执行完整备份")
            return self._perform_full_backup(backup_dir, metadata)

        # 记录上次备份ID
        metadata["parent_backup"] = last_full_backup["id"]

        # 获取上次备份时间
        last_backup_time = datetime.datetime.fromisoformat(
            last_full_backup["completed_at"]
        )
        last_backup_timestamp = last_backup_time.timestamp()

        # 执行与增量备份相同的逻辑，但是相对于上次完整备份
        # 获取要备份的目录
        data_dirs = self.config.resilience.backup.backup_items
        file_count = 0

        for src_dir in data_dirs:
            if not os.path.exists(src_dir):
                logger.warning(f"备份源目录不存在: {src_dir}")
                continue

            # 创建目标目录
            rel_path = os.path.relpath(src_dir, self.config.service.data_root)
            dst_dir = os.path.join(backup_dir, rel_path)
            os.makedirs(os.path.dirname(dst_dir), exist_ok=True)

            # 复制目录内容
            logger.info(f"差异备份目录: {src_dir} -> {dst_dir}")
            if os.path.isdir(src_dir):
                file_count += self._copy_directory(
                    src_dir,
                    dst_dir,
                    metadata,
                    last_modified_after=last_backup_timestamp,
                )
            else:
                # 检查文件修改时间
                file_mtime = os.path.getmtime(src_dir)
                if file_mtime > last_backup_timestamp:
                    self._copy_file(src_dir, dst_dir, metadata)
                    file_count += 1

        return file_count

    def _copy_directory(
        self,
        src_dir: str,
        dst_dir: str,
        metadata: dict[str, Any],
        last_modified_after: float = 0,
    ) -> int:
        """递归复制目录内容

        Args:
            src_dir: 源目录
            dst_dir: 目标目录
            metadata: 备份元数据
            last_modified_after: 只复制在此时间戳之后修改的文件

        Returns:
            int: 复制的文件数
        """
        file_count = 0

        try:
            # 创建目标目录
            os.makedirs(dst_dir, exist_ok=True)

            # 遍历源目录
            for item in os.listdir(src_dir):
                src_path = os.path.join(src_dir, item)
                dst_path = os.path.join(dst_dir, item)

                # 处理目录
                if os.path.isdir(src_path):
                    file_count += self._copy_directory(
                        src_path, dst_path, metadata, last_modified_after
                    )
                # 处理文件
                else:
                    # 检查文件修改时间
                    file_mtime = os.path.getmtime(src_path)
                    if file_mtime > last_modified_after:
                        self._copy_file(src_path, dst_path, metadata)
                        file_count += 1

            return file_count
        except Exception as e:
            logger.error(f"复制目录失败 {src_dir} -> {dst_dir}: {e!s}")
            return file_count

    def _copy_file(self, src_file: str, dst_file: str, metadata: dict[str, Any]):
        """复制单个文件

        Args:
            src_file: 源文件
            dst_file: 目标文件
            metadata: 备份元数据
        """
        try:
            # 复制文件
            shutil.copy2(src_file, dst_file)

            # 添加到备份元数据
            rel_path = os.path.relpath(src_file, self.config.service.data_root)
            file_info = {
                "path": rel_path,
                "size": os.path.getsize(src_file),
                "mtime": os.path.getmtime(src_file),
            }
            metadata["files"].append(file_info)
        except Exception as e:
            logger.error(f"复制文件失败 {src_file} -> {dst_file}: {e!s}")
            raise

    def _save_metadata(self, backup_id: str, metadata: dict[str, Any]):
        """保存备份元数据

        Args:
            backup_id: 备份ID
            metadata: 备份元数据
        """
        metadata_path = os.path.join(self.backup_path, f"{backup_id}_metadata.json")

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

    def _find_last_backup(
        self, job_name: str, backup_type: str = None
    ) -> dict[str, Any]:
        """查找上次成功的备份

        Args:
            job_name: 任务名称
            backup_type: 备份类型（可选）

        Returns:
            Dict[str, Any]: 备份元数据，如果没有找到则返回None
        """
        # 列出所有备份
        backups = self.list_backups()

        # 过滤匹配条件的备份
        matching_backups = []
        for backup in backups:
            if backup["job_name"] == job_name and backup["status"] == "completed":
                if backup_type is None or backup["type"] == backup_type:
                    matching_backups.append(backup)

        if not matching_backups:
            return None

        # 按完成时间排序
        matching_backups.sort(key=lambda x: x["completed_at"], reverse=True)

        # 返回最新的备份
        return matching_backups[0]

    def _cleanup_old_backups(self) -> None:
        """清理过期备份"""
        if not self.max_backups or self.max_backups <= 0:
            return

        # 列出所有备份
        backups = self.list_backups()

        # 按完成时间排序
        backups.sort(key=lambda x: x.get("completed_at", ""), reverse=True)

        # 保留指定数量的备份
        backups_to_keep = backups[: self.max_backups]
        backups_to_delete = backups[self.max_backups :]

        # 删除多余备份
        for backup in backups_to_delete:
            backup_id = backup["id"]
            logger.info(f"清理过期备份: {backup_id}")
            self._delete_backup(backup_id)

    def _delete_backup(self, backup_id: str):
        """删除备份

        Args:
            backup_id: 备份ID
        """
        backup_dir = os.path.join(self.backup_path, backup_id)
        metadata_path = os.path.join(self.backup_path, f"{backup_id}_metadata.json")

        # 删除备份目录
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)

        # 删除元数据文件
        if os.path.exists(metadata_path):
            os.remove(metadata_path)

    def list_backups(self) -> list[dict[str, Any]]:
        """列出所有备份

        Returns:
            List[Dict[str, Any]]: 备份列表
        """
        backups = []

        try:
            # 查找所有元数据文件
            for filename in os.listdir(self.backup_path):
                if filename.endswith("_metadata.json"):
                    metadata_path = os.path.join(self.backup_path, filename)

                    try:
                        with open(metadata_path) as f:
                            metadata = json.load(f)
                            backups.append(metadata)
                    except Exception as e:
                        logger.error(f"读取备份元数据失败 {metadata_path}: {e!s}")
        except Exception as e:
            logger.error(f"列出备份失败: {e!s}")

        return backups

    def run_manual_backup(self, job_name: str, backup_type: str = "full") -> str:
        """手动运行备份任务

        Args:
            job_name: 任务名称
            backup_type: 备份类型 (full/incremental/differential)

        Returns:
            str: 备份ID
        """
        logger.info(f"手动运行备份任务: {job_name}")
        return self._run_backup(job_name, backup_type)

    def restore_backup(self, backup_id: str, target_dir: str = None) -> bool:
        """从备份恢复数据

        Args:
            backup_id: 备份ID
            target_dir: 恢复目标目录（默认为原始位置）

        Returns:
            bool: 是否成功
        """
        logger.info(f"从备份 {backup_id} 恢复数据")

        # 检查备份是否存在
        backup_dir = os.path.join(self.backup_path, backup_id)
        metadata_path = os.path.join(self.backup_path, f"{backup_id}_metadata.json")

        if not os.path.exists(backup_dir) or not os.path.exists(metadata_path):
            logger.error(f"备份不存在: {backup_id}")
            return False

        # 读取备份元数据
        try:
            with open(metadata_path) as f:
                metadata = json.load(f)
        except Exception as e:
            logger.error(f"读取备份元数据失败: {e!s}")
            return False

        # 检查备份状态
        if metadata.get("status") != "completed":
            logger.error(f"备份状态不是已完成: {metadata.get('status')}")
            return False

        # 对于增量和差异备份，需要先恢复父备份
        if (
            metadata["type"] in ["incremental", "differential"]
            and "parent_backup" in metadata
        ):
            parent_id = metadata["parent_backup"]
            logger.info(f"先恢复父备份: {parent_id}")
            self.restore_backup(parent_id, target_dir)

        # 确定恢复目标目录
        restore_dir = target_dir or self.config.service.data_root

        # 恢复文件
        success = True
        for file_info in metadata.get("files", []):
            try:
                # 获取文件路径
                rel_path = file_info["path"]
                src_path = os.path.join(backup_dir, rel_path)
                dst_path = os.path.join(restore_dir, rel_path)

                # 确保目标目录存在
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)

                # 复制文件
                if os.path.exists(src_path):
                    shutil.copy2(src_path, dst_path)
                    logger.debug(f"已恢复文件: {rel_path}")
                else:
                    logger.warning(f"备份中找不到文件: {rel_path}")
                    success = False
            except Exception as e:
                logger.error(f"恢复文件 {rel_path} 失败: {e!s}")
                success = False

        logger.info(f"从备份 {backup_id} 恢复数据{'成功' if success else '部分失败'}")
        return success

    def get_backup_info(self, backup_id: str) -> dict[str, Any]:
        """获取备份详细信息

        Args:
            backup_id: 备份ID

        Returns:
            Dict[str, Any]: 备份信息
        """
        metadata_path = os.path.join(self.backup_path, f"{backup_id}_metadata.json")

        if not os.path.exists(metadata_path):
            return {"error": "backup_not_found"}

        try:
            with open(metadata_path) as f:
                metadata = json.load(f)

            # 添加额外信息
            backup_dir = os.path.join(self.backup_path, backup_id)
            if os.path.exists(backup_dir):
                metadata["size"] = self._get_directory_size(backup_dir)

            return metadata
        except Exception as e:
            logger.error(f"获取备份信息失败: {e!s}")
            return {"error": str(e)}

    def _get_directory_size(self, path: str) -> int:
        """获取目录大小

        Args:
            path: 目录路径

        Returns:
            int: 大小（字节）
        """
        total_size = 0

        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)

        return total_size
