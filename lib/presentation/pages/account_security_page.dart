import 'package:flutter/material.dart';

import '../../services/services/auth_service.dart';

class AccountSecurityPage extends StatelessWidget {
  const AccountSecurityPage({super.key});

  @override
  Widget build(BuildContext context) {
    final userInfo = context.read<AuthService>().userInfo!;

    return Scaffold(
      appBar: AppBar(
        title: const Text('账号安全'),
      ),
      body: ListView(
        children: [
          _buildSection(
            context,
            '登录密码',
            [
              _SecurityItem(
                title: '修改密码',
                subtitle: '建议定期修改密码，确保账号安全',
                onTap: () {
                  // TODO: 打开修改密码页面
                },
              ),
            ],
          ),
          _buildSection(
            context,
            '账号绑定',
            [
              _SecurityItem(
                title: '手机号',
                subtitle: userInfo['phone'] ?? '未绑定',
                onTap: () {
                  // TODO: 打开手机号绑定页面
                },
              ),
              _SecurityItem(
                title: '微信',
                subtitle: userInfo['wechat'] ?? '未绑定',
                onTap: () {
                  // TODO: 打开微信绑定页面
                },
              ),
              _SecurityItem(
                title: '支付宝',
                subtitle: userInfo['alipay'] ?? '未绑定',
                onTap: () {
                  // TODO: 打开支付宝绑定页面
                },
              ),
              _SecurityItem(
                title: 'Apple ID',
                subtitle: userInfo['apple_id'] ?? '未绑定',
                onTap: () {
                  // TODO: 打开Apple ID绑定页面
                },
              ),
            ],
          ),
          _buildSection(
            context,
            '安全设置',
            [
              _SecurityItem(
                title: '登录验证',
                subtitle: '未开启',
                trailing: Switch(
                  value: userInfo['two_factor_auth'] ?? false,
                  onChanged: (value) {
                    // TODO: 切换两步验证
                  },
                ),
              ),
              _SecurityItem(
                title: '设备管理',
                subtitle: '查看已登录设备',
                onTap: () {
                  // TODO: 打开设备管理页面
                },
              ),
              _SecurityItem(
                title: '登录记录',
                subtitle: '查看登录历史',
                onTap: () {
                  // TODO: 打开登录记录页面
                },
              ),
            ],
          ),
          const SizedBox(height: 24),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: OutlinedButton(
              onPressed: () {
                showDialog(
                  context: context,
                  builder: (context) => AlertDialog(
                    title: const Text('注销账号'),
                    content: const Text(
                      '注销账号后，您的所有数据将被永久删除，且无法恢复。'
                      '如果您确定要注销账号，请联系客服。',
                    ),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.pop(context),
                        child: const Text('取消'),
                      ),
                      TextButton(
                        onPressed: () {
                          // TODO: 跳转到客服页面
                          Navigator.pop(context);
                        },
                        child: const Text('联系客服'),
                      ),
                    ],
                  ),
                );
              },
              style: OutlinedButton.styleFrom(
                foregroundColor: Colors.red,
                side: const BorderSide(color: Colors.red),
              ),
              child: const Text('注销账号'),
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
    List<_SecurityItem> items,
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
              return _buildSecurityItem(context, item);
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildSecurityItem(BuildContext context, _SecurityItem item) {
    return InkWell(
      onTap: item.trailing == null ? item.onTap : null,
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
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.title,
                    style: const TextStyle(fontSize: 16),
                  ),
                  if (item.subtitle != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      item.subtitle!,
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ],
              ),
            ),
            if (item.trailing != null)
              item.trailing!
            else
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

class _SecurityItem {
  final String title;
  final String? subtitle;
  final Widget? trailing;
  final VoidCallback? onTap;

  const _SecurityItem({
    required this.title,
    this.subtitle,
    this.trailing,
    this.onTap,
  });
} 