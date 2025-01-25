import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
import 'package:suoke_life/features/profile/lib/widgets/user_info_tile.dart';
import 'package:suoke_life/libs/ui_components/lib/navigation/bottom_navigation_bar.dart';
import 'package:suoke_life/core/services/agent_memory_service.dart';
import 'package:suoke_life/core/models/user_preference.dart';

class SettingsPage extends StatefulWidget {
  const SettingsPage({super.key});

  @override
  _SettingsPageState createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  int _currentIndex = 4;
  String _dataRetentionPeriod = '30d'; // 默认数据保留期限
  bool _dataContributionEnabled = false; // 默认数据贡献状态
  final AgentMemoryService _agentMemoryService = GetIt.instance<AgentMemoryService>();

  @override
  void initState() {
    super.initState();
    _loadPrivacySettings();
  }

  Future<void> _loadPrivacySettings() async {
    final userPreference = await _agentMemoryService.getUserPreference('defaultUserId'); //  使用默认用户 ID
    if (userPreference != null) {
      setState(() {
        _dataRetentionPeriod = userPreference.localDataRetentionPeriod ?? '30d';
        _dataContributionEnabled = userPreference.dataContributionEnabled ?? false;
      });
    }
  }

  Future<void> _savePrivacySettings() async {
    final userPreference = UserPreference(
      userId: 'defaultUserId', //  使用默认用户 ID
      localDataRetentionPeriod: _dataRetentionPeriod,
      dataContributionEnabled: _dataContributionEnabled,
    );
    await _agentMemoryService.saveUserPreference(userPreference);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('隐私设置已保存'),
      ),
    );
  }

  void _onTabTapped(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: ListView(
        children: <Widget>[
          ListTile(
            title: const Text('隐私设置', style: TextStyle(fontWeight: FontWeight.bold)),
            dense: true,
            enabled: false,
          ),
          ListTile(
            title: const Text('数据保留期限'),
            trailing: DropdownButton<String>(
              value: _dataRetentionPeriod,
              items: <String>['7d', '30d', '90d', 'persistent']
                  .map<DropdownMenuItem<String>>((String value) {
                return DropdownMenuItem<String>(
                  value: value,
                  child: Text(value == 'persistent' ? '永久保留' : value),
                );
              }).toList(),
              onChanged: (String? newValue) {
                setState(() {
                  _dataRetentionPeriod = newValue!;
                });
              },
            ),
          ),
          SwitchListTile(
            title: const Text('数据贡献'),
            value: _dataContributionEnabled,
            subtitle: const Text('匿名化后贡献数据以改进服务'),
            onChanged: (bool newValue) {
              setState(() {
                _dataContributionEnabled = newValue;
              });
            },
          ),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: ElevatedButton(
              onPressed: _savePrivacySettings,
              child: const Text('保存隐私设置'),
            ),
          ),
          const Divider(),
          ListTile(
            title: const Text('账户设置', style: TextStyle(fontWeight: FontWeight.bold)),
            dense: true,
            enabled: false,
          ),
          ListTile(
            title: const Text('修改密码'),
            onTap: () {
              // TODO: Implement change password functionality
            },
          ),
          ListTile(
            title: const Text('注销账户'),
            onTap: () {
              // TODO: Implement delete account functionality
            },
          ),
          const Divider(),
          ListTile(
            title: const Text('通用设置', style: TextStyle(fontWeight: FontWeight.bold)),
            dense: true,
            enabled: false,
          ),
          ListTile(
            title: const Text('用户信息'),
            onTap: () {
              // TODO: Implement user info functionality
            },
          ),
          ListTile(
            title: const Text('通知设置'),
            onTap: () {
              // TODO: Implement notification settings functionality
            },
          ),
          ListTile(
            title: const Text('帮助与反馈'),
            onTap: () {
              // TODO: Implement help and feedback functionality
            },
          ),
        ],
      ),
      bottomNavigationBar: AppBottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: _onTabTapped,
      ),
    );
  }
} 