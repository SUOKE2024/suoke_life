import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../data/models/network_connection_record.dart';

class NetworkHistoryItem extends StatelessWidget {
  final NetworkConnectionRecord record;
  final VoidCallback onTap;

  const NetworkHistoryItem({
    Key? key,
    required this.record,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(
        record.isConnected ? Icons.wifi : Icons.wifi_off,
        color: record.isConnected ? Colors.green : Colors.red,
      ),
      title: Text(record.type),
      subtitle: Text(
        record.errorMessage ?? (record.isConnected ? '连接成功' : '连接断开'),
      ),
      trailing: Text(
        _formatDateTime(record.timestamp),
        style: TextStyle(
          color: Colors.grey[600],
          fontSize: 12,
        ),
      ),
      onTap: onTap,
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
      return '刚刚';
    }
  }
} 