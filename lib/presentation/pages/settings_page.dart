import 'package:flutter/material.dart';

import '../../services/services/auth_service.dart';

class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('设置'),
      ),
      body: ListView(
        children: [
          _buildSection(
            context,
            '账号设置',
            [
              _SettingItem(
                icon: Icons.person_outline,
                title: '个人资料',
                onTap: () {
                  // TODO: 打开个人资料页面
                },
              ),
              _SettingItem(
                icon: Icons.security,
                title: '账号安全',
                onTap: () {
                  // TODO: 打开账号安全页面
                },
              ),
              _SettingItem(
                icon: Icons.notifications_none,
                title: '消息通知',
                onTap: () {
                  // TODO: 打开消息通知设置页面
                },
              ),
              _SettingItem(
                icon: Icons.privacy_tip_outlined,
                title: '隐私设置',
                onTap: () {
                  // TODO: 打开隐私设置页面
                },
              ),
            ],
          ),
          _buildSection(
            context,
            '通用设置',
            [
              _SettingItem(
                icon: Icons.language,
                title: '语言',
                trailing: const Text('简体中文'),
                onTap: () {
                  // TODO: 打开语言设置页面
                },
              ),
              _SettingItem(
                icon: Icons.dark_mode_outlined,
                title: '深色模式',
                trailing: Switch(
                  value: Theme.of(context).brightness == Brightness.dark,
                  onChanged: (value) {
                    // TODO: 切换深色模式
                  },
                ),
              ),
              _SettingItem(
                icon: Icons.font_download_outlined,
                title: '字体大小',
                trailing: const Text('标准'),
                onTap: () {
                  // TODO: 打开字体设置页面
                },
              ),
              _SettingItem(
                icon: Icons.storage_outlined,
                title: '清除缓存',
                trailing: const Text('1.2MB'),
                onTap: () {
                  // TODO: 清除缓存
                },
              ),
            ],
          ),
          _buildSection(
            context,
            '其他设置',
            [
              _SettingItem(
                icon: Icons.info_outline,
                title: '关于我们',
                onTap: () {
                  // TODO: 打开关于页面
                },
              ),
              _SettingItem(
                icon: Icons.help_outline,
                title: '帮助与反馈',
                onTap: () {
                  // TODO: 打开帮助页面
                },
              ),
              _SettingItem(
                icon: Icons.update,
                title: '检查更新',
                trailing: const Text('v1.0.0'),
                onTap: () {
                  // TODO: 检查更新
                },
              ),
            ],
          ),
          const SizedBox(height: 24),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Consumer<AuthService>(
              builder: (context, authService, child) {
                if (!authService.isAuthenticated) {
                  return const SizedBox.shrink();
                }
                return ElevatedButton(
                  onPressed: () async {
                    final confirmed = await showDialog<bool>(
                      context: context,
                      builder: (context) => AlertDialog(
                        title: const Text('退出登录'),
                        content: const Text('确定要退出登录吗？'),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.pop(context, false),
                            child: const Text('取消'),
                          ),
                          TextButton(
                            onPressed: () => Navigator.pop(context, true),
                            child: const Text('确定'),
                          ),
                        ],
                      ),
                    );

                    if (confirmed == true && context.mounted) {
                      await authService.logout();
                      Navigator.pop(context);
                    }
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                  ),
                  child: const Text('退出登录'),
                );
              },
            ),
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildSection(
    BuildContext context,
    String title,
    List<_SettingItem> items,
  ) {
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
            children: items.map((item) {
              return _buildSettingItem(context, item);
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildSettingItem(BuildContext context, _SettingItem item) {
    return InkWell(
      onTap: item.onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 12,
        ),
        decoration: BoxDecoration(
          border: Border(
            bottom: BorderSide(
              color: Colors.grey[200]!,
            ),
          ),
        ),
        child: Row(
          children: [
            Icon(
              item.icon,
              size: 24,
              color: Colors.grey[600],
            ),
            const SizedBox(width: 12),
            Text(
              item.title,
              style: const TextStyle(fontSize: 16),
            ),
            const Spacer(),
            if (item.trailing != null) item.trailing!,
            if (item.trailing == null)
              Icon(
                Icons.arrow_forward_ios,
                size: 16,
                color: Colors.grey[400],
              ),
          ],
        ),
      ),
    );
  }
}

class _SettingItem {
  final IconData icon;
  final String title;
  final Widget? trailing;
  final VoidCallback onTap;

  const _SettingItem({
    required this.icon,
    required this.title,
    this.trailing,
    required this.onTap,
  });
} 