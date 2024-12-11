import 'package:flutter/material.dart';
import '../services/auth_service.dart';

class PrivacySettingsScreen extends StatefulWidget {
  const PrivacySettingsScreen({Key? key}) : super(key: key);

  @override
  State<PrivacySettingsScreen> createState() => _PrivacySettingsScreenState();
}

class _PrivacySettingsScreenState extends State<PrivacySettingsScreen> {
  final _authService = AuthService();
  bool _isLoading = true;
  
  // 隐私设置
  bool _showOnlineStatus = true;
  bool _showLocation = true;
  bool _allowFriendRequests = true;
  bool _showActivityStatus = true;
  bool _showCollections = true;

  @override
  void initState() {
    super.initState();
    _loadPrivacySettings();
  }

  Future<void> _loadPrivacySettings() async {
    setState(() => _isLoading = true);
    final settings = await _authService.getPrivacySettings();
    if (settings != null) {
      setState(() {
        _showOnlineStatus = settings['show_online_status'] ?? true;
        _showLocation = settings['show_location'] ?? true;
        _allowFriendRequests = settings['allow_friend_requests'] ?? true;
        _showActivityStatus = settings['show_activity_status'] ?? true;
        _showCollections = settings['show_collections'] ?? true;
      });
    }
    setState(() => _isLoading = false);
  }

  Future<void> _saveSettings() async {
    setState(() => _isLoading = true);
    final success = await _authService.updatePrivacySettings(
      showOnlineStatus: _showOnlineStatus,
      showLocation: _showLocation,
      allowFriendRequests: _allowFriendRequests,
      showActivityStatus: _showActivityStatus,
      showCollections: _showCollections,
    );
    setState(() => _isLoading = false);

    if (!mounted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(success ? '设置已保存' : '保存失败，请重试'),
        backgroundColor: success ? Colors.green : Colors.red,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('隐私设置'),
        actions: [
          TextButton(
            onPressed: _saveSettings,
            child: const Text('保存'),
          ),
        ],
      ),
      body: ListView(
        children: [
          _buildSection(
            '在线状态',
            [
              SwitchListTile(
                title: const Text('显示在线状态'),
                subtitle: const Text('让其他玩家看到你是否在线'),
                value: _showOnlineStatus,
                onChanged: (value) {
                  setState(() => _showOnlineStatus = value);
                },
              ),
            ],
          ),
          _buildSection(
            '位置信息',
            [
              SwitchListTile(
                title: const Text('显示位置信息'),
                subtitle: const Text('在游戏中显示你的大致位置'),
                value: _showLocation,
                onChanged: (value) {
                  setState(() => _showLocation = value);
                },
              ),
            ],
          ),
          _buildSection(
            '社交设置',
            [
              SwitchListTile(
                title: const Text('允许好友请求'),
                subtitle: const Text('是否接收新的好友请求'),
                value: _allowFriendRequests,
                onChanged: (value) {
                  setState(() => _allowFriendRequests = value);
                },
              ),
              SwitchListTile(
                title: const Text('显示活动状态'),
                subtitle: const Text('让好友看到你的游戏活动'),
                value: _showActivityStatus,
                onChanged: (value) {
                  setState(() => _showActivityStatus = value);
                },
              ),
            ],
          ),
          _buildSection(
            '收藏展示',
            [
              SwitchListTile(
                title: const Text('公开收藏'),
                subtitle: const Text('让其他玩家查看你的收藏'),
                value: _showCollections,
                onChanged: (value) {
                  setState(() => _showCollections = value);
                },
              ),
            ],
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              '注意：这些设置可能会影响你在游戏中的社交体验。\n'
              '你可以随时更改这些设置。',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[600],
              ),
            ),
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
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.grey[800],
            ),
          ),
        ),
        ...children,
        const Divider(),
      ],
    );
  }
} 