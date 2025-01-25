import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';
import '../../data/models/sync_log.dart';

class SyncLogItem extends StatelessWidget {
  final SyncLog log;
  final VoidCallback onTap;

  const SyncLogItem({
    Key? key,
    required this.log,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              _buildStatusIcon(),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      log.description,
                      style: Get.textTheme.titleMedium,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _formatDateTime(log.timestamp),
                      style: Get.textTheme.bodySmall?.copyWith(
                        color: Colors.grey,
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(
                Icons.chevron_right,
                color: Colors.grey,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusIcon() {
    IconData iconData;
    Color color;

    switch (log.status) {
      case 'success':
        iconData = Icons.check_circle;
        color = Colors.green;
        break;
      case 'error':
        iconData = Icons.error;
        color = Colors.red;
        break;
      case 'warning':
        iconData = Icons.warning_amber;
        color = Colors.orange;
        break;
      default:
        iconData = Icons.help;
        color = Colors.grey;
    }

    return Icon(
      iconData,
      color: color,
      size: 24,
    );
  }

  String _formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inDays > 0) {
      return DateFormat('MM-dd HH:mm').format(dateTime);
    } else if (difference.inHours > 0) {
      return '${difference.inHours}小时前';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}分钟前';
    } else {
      return '刚���';
    }
  }
} 