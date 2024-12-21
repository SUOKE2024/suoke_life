import 'package:flutter/material.dart';

class SyncStatus {
  final String title;
  final String description;
  final IconData icon;
  final Color color;

  const SyncStatus({
    required this.title,
    required this.description,
    required this.icon,
    required this.color,
  });

  factory SyncStatus.normal() => const SyncStatus(
    title: '同步正常',
    description: '所有数据已同步',
    icon: Icons.check_circle,
    color: Colors.green,
  );

  factory SyncStatus.syncing() => const SyncStatus(
    title: '正在同步',
    description: '正在同步数据，请稍候...',
    icon: Icons.sync,
    color: Colors.blue,
  );

  factory SyncStatus.error() => const SyncStatus(
    title: '同步异常',
    description: '请检查网络连接后重试',
    icon: Icons.error_outline,
    color: Colors.red,
  );

  factory SyncStatus.warning() => const SyncStatus(
    title: '部分同步',
    description: '部分数据未能同步',
    icon: Icons.warning_amber,
    color: Colors.orange,
  );
} 