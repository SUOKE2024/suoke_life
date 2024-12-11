import 'package:flutter/material.dart';

import '../../services/services/notification_service.dart';

class NotificationSettingsPage extends StatefulWidget {
  const NotificationSettingsPage({super.key});

  @override
  State<NotificationSettingsPage> createState() => _NotificationSettingsPageState();
}

class _NotificationSettingsPageState extends State<NotificationSettingsPage> {
  bool _isLoading = false;
  final Map<String, bool> _settings = {
    'enable_all': true,
    'system_notification': true,
    'chat_notification': true,
    'order_notification': true,
    'promotion_notification': false,
    'sound': true,
    'vibration': true,
    'show_preview': true,
  };

  Future<void> _saveSettings() async {
    setState(() => _isLoading = true);
    try {
      // TODO: 保存设置到服务器
      await Future.delayed(const Duration(seconds: 1));
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('设置已保存')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('通知设置'),
        actions: [
          TextButton(
            onPressed: _isLoading ? null : _saveSettings,
            child: _isLoading
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('保存'),
          ),
        ],
      ),
      body: ListView(
        children: [
          _buildSection(
            '通知开关',
            [
              _buildSwitchTile(
                '接收全部通知',
                '开启后可以接收所有类型的通知',
                'enable_all',
                onChanged: (value) {
                  setState(() {
                    _settings['enable_all'] = value;
                    if (!value) {
                      _settings['system_notification'] = false;
                      _settings['chat_notification'] = false;
                      _settings['order_notification'] = false;
                      _settings['promotion_notification'] = false;
                    }
                  });
                },
              ),
              _buildSwitchTile(
                '系统通知',
                '系统更新、账号安全等重要通知',
                'system_notification',
                enabled: _settings['enable_all']!,
              ),
              _buildSwitchTile(
                '对话通知',
                'AI助理的消息提醒',
                'chat_notification',
                enabled: _settings['enable_all']!,
              ),
              _buildSwitchTile(
                '订单通知',
                '订单状态变更、物流信息等',
                'order_notification',
                enabled: _settings['enable_all']!,
              ),
              _buildSwitchTile(
                '活动通知',
                '优惠促销、新功能等',
                'promotion_notification',
                enabled: _settings['enable_all']!,
              ),
            ],
          ),
          _buildSection(
            '提醒方式',
            [
              _buildSwitchTile(
                '声音',
                '收到通知时播放提示音',
                'sound',
              ),
              _buildSwitchTile(
                '震动',
                '收到通知时震动提醒',
                'vibration',
              ),
              _buildSwitchTile(
                '通知预览',
                '在锁屏界面显示通知内容',
                'show_preview',
              ),
            ],
          ),
          _buildSection(
            '免打扰时段',
            [
              ListTile(
                title: const Text('时间段设置'),
                subtitle: const Text('22:00 - 08:00'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () {
                  // TODO: 打开免打扰时段设置页面
                },
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSection(String title, List<Widget> children) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Text(
            title,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        Container(
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surface,
            border: Border(
              top: BorderSide(color: Colors.grey[200]!),
              bottom: BorderSide(color: Colors.grey[200]!),
            ),
          ),
          child: Column(
            children: children,
          ),
        ),
      ],
    );
  }

  Widget _buildSwitchTile(
    String title,
    String subtitle,
    String settingKey, {
    bool enabled = true,
    void Function(bool)? onChanged,
  }) {
    return SwitchListTile(
      title: Text(title),
      subtitle: Text(
        subtitle,
        style: TextStyle(
          color: enabled ? Colors.grey[600] : Colors.grey[400],
        ),
      ),
      value: _settings[settingKey]!,
      onChanged: enabled
          ? (value) {
              setState(() {
                _settings[settingKey] = value;
                onChanged?.call(value);
              });
            }
          : null,
    );
  }
} 