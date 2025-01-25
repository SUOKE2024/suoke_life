import 'package:flutter/material.dart';
import '../../data/models/login_record.dart';
import 'package:timeago/timeago.dart' as timeago;

class LoginRecordItem extends StatelessWidget {
  final LoginRecord record;
  final VoidCallback onTap;

  const LoginRecordItem({
    Key? key,
    required this.record,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(
        _getLoginTypeIcon(),
        color: record.success ? Colors.green : Colors.red,
      ),
      title: Row(
        children: [
          Expanded(
            child: Text(_getLoginTypeText()),
          ),
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: 8,
              vertical: 2,
            ),
            decoration: BoxDecoration(
              color: record.success ? Colors.green[100] : Colors.red[100],
              borderRadius: BorderRadius.circular(10),
            ),
            child: Text(
              record.success ? '成功' : '失败',
              style: TextStyle(
                fontSize: 12,
                color: record.success ? Colors.green[700] : Colors.red[700],
              ),
            ),
          ),
        ],
      ),
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(record.deviceInfo),
          Text(
            timeago.format(record.timestamp, locale: 'zh'),
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
      onTap: onTap,
    );
  }

  String _getLoginTypeText() {
    switch (record.loginType) {
      case 'password':
        return '密码登录';
      case 'biometric':
        return '生物识别';
      case 'wechat':
        return '微信登录';
      case 'google':
        return 'Google登录';
      case 'apple':
        return 'Apple登录';
      default:
        return record.loginType;
    }
  }

  IconData _getLoginTypeIcon() {
    switch (record.loginType) {
      case 'password':
        return Icons.lock;
      case 'biometric':
        return Icons.fingerprint;
      case 'wechat':
        return Icons.wechat;
      case 'google':
        return Icons.g_mobiledata;
      case 'apple':
        return Icons.apple;
      default:
        return Icons.login;
    }
  }
} 