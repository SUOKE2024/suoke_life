import 'package:flutter/material.dart';
import '../../services/connection_manager_service.dart';

class ConnectionStatusWidget extends StatelessWidget {
  final ConnectionState state;

  const ConnectionStatusWidget({
    Key? key,
    required this.state,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            _getIcon(),
            color: _getColor(),
            size: 16,
          ),
          const SizedBox(width: 4),
          Text(
            _getStatusText(),
            style: TextStyle(
              color: _getColor(),
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  IconData _getIcon() {
    switch (state) {
      case ConnectionState.connected:
        return Icons.check_circle;
      case ConnectionState.connecting:
      case ConnectionState.reconnecting:
        return Icons.sync;
      case ConnectionState.disconnected:
        return Icons.cloud_off;
      case ConnectionState.failed:
        return Icons.error;
      default:
        return Icons.help;
    }
  }

  Color _getColor() {
    switch (state) {
      case ConnectionState.connected:
        return Colors.green;
      case ConnectionState.connecting:
      case ConnectionState.reconnecting:
        return Colors.orange;
      case ConnectionState.disconnected:
        return Colors.grey;
      case ConnectionState.failed:
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  String _getStatusText() {
    switch (state) {
      case ConnectionState.connected:
        return '已连接';
      case ConnectionState.connecting:
        return '连接中';
      case ConnectionState.reconnecting:
        return '重连中';
      case ConnectionState.disconnected:
        return '已断开';
      case ConnectionState.failed:
        return '连接失败';
      default:
        return '未知状态';
    }
  }
} 