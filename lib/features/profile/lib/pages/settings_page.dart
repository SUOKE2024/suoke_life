import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:suoke_life/ui_components/navigation/bottom_navigation_bar.dart';
import 'package:suoke_life/lib/core/utils/app_localizations.dart';
import 'package:suoke_life/features/profile/lib/pages/health_data_input_page.dart';
import 'package:suoke_life/lib/core/widgets/common_bottom_navigation_bar.dart';
import 'package:suoke_life/lib/core/widgets/common_scaffold.dart';
import 'package:suoke_life/lib/core/services/agent_memory_service.dart';
import 'package:suoke_life/lib/core/models/user_preference.dart';
import 'package:get_it/get_it.dart';

class SettingsPage extends StatefulWidget {
  const SettingsPage({Key? key}) : super(key: key);

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  int _currentIndex = 3;
  String _dataRetentionPeriod = '30d';
  bool _dataContributionEnabled = false;
  final AgentMemoryService _agentMemoryService = GetIt.instance<AgentMemoryService>();

  @override
  void initState() {
    super.initState();
    _loadPrivacySettings();
  }

  Future<void> _loadPrivacySettings() async {
    final userPreference = await _agentMemoryService.getUserPreference('defaultUserId');
    if (userPreference != null) {
      setState(() {
        _dataRetentionPeriod = userPreference.localDataRetentionPeriod ?? '30d';
        _dataContributionEnabled = userPreference.dataContributionEnabled ?? false;
      });
    }
  }

  Future<void> _savePrivacySettings() async {
    final userPreference = UserPreference(
      userId: 'defaultUserId',
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
    final localizations = AppLocalizations.of(context)!;
    return CommonScaffold(
      title: localizations.translate('settings_title'),
      body: ListView(
        children: [
          ListTile(
            title: Text(localizations.translate('notifications')),
            onTap: () {
              // TODO: Implement notifications settings
            },
          ),
          ListTile(
            title: Text(localizations.translate('privacy')),
            onTap: () {
              // TODO: Implement privacy settings
            },
          ),
          ListTile(
            title: Text(localizations.translate('about')),
            onTap: () {
              // TODO: Implement about page
            },
          ),
          ListTile(
            title: const Text('Edit Profile'),
            onTap: () => context.go('/edit_profile'),
          ),
          ListTile(
            leading: const Icon(Icons.fitness_center),
            title: const Text('健康数据录入'),
            onTap: () {
              Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) => const HealthDataInputPage()));
            },
          ),
          ListTile(
            title: const Text('Admin Dashboard'),
            onTap: () => context.go('/admin_dashboard'),
          ),
          const ListTile(
            title: Text('隐私设置', style: TextStyle(fontWeight: FontWeight.bold)),
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
          const ListTile(
            title: Text('账户设置', style: TextStyle(fontWeight: FontWeight.bold)),
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
          const ListTile(
            title: Text('通用设置', style: TextStyle(fontWeight: FontWeight.bold)),
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
      bottomNavigationBar: CommonBottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: _onTabTapped,
      ),
    );
  }
}
