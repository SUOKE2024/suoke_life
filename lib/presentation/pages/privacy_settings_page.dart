import 'package:flutter/material.dart';

class PrivacySettingsPage extends StatefulWidget {
  const PrivacySettingsPage({super.key});

  @override
  State<PrivacySettingsPage> createState() => _PrivacySettingsPageState();
}

class _PrivacySettingsPageState extends State<PrivacySettingsPage> {
  bool _isLoading = false;
  final Map<String, bool> _settings = {
    'location_service': true,
    'usage_data': true,
    'personalized_ads': false,
    'third_party_sharing': false,
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

  Future<void> _exportData() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('导出个人数据'),
        content: const Text(
          '我们将为您生成一份包含您的个人数据的文件，'
          '这可能需要一些时间。文件生成后，我们会通过邮件通知您。',
        ),
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

    if (confirmed == true && mounted) {
      setState(() => _isLoading = true);
      try {
        // TODO: 调用服务器导出数据
        await Future.delayed(const Duration(seconds: 1));
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('数据导出请求已提交，请注意查收邮件'),
            ),
          );
        }
      } finally {
        if (mounted) {
          setState(() => _isLoading = false);
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('隐私设置'),
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
            '位置服务',
            [
              _buildSwitchTile(
                '位置服务',
                '允许访问您的位置信息以提供更好的服务',
                'location_service',
              ),
            ],
          ),
          _buildSection(
            '数据收集',
            [
              _buildSwitchTile(
                '使用数据',
                '收集应用使用数据以改善用户体验',
                'usage_data',
              ),
              _buildSwitchTile(
                '个性化广告',
                '根据您的兴趣偏好显示广告',
                'personalized_ads',
              ),
              _buildSwitchTile(
                '第三方数据共享',
                '与合作伙伴共享数据以提供更好的服务',
                'third_party_sharing',
              ),
            ],
          ),
          _buildSection(
            '数据管理',
            [
              ListTile(
                title: const Text('导出个人数据'),
                subtitle: const Text('下载您的个人数据副本'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: _isLoading ? null : _exportData,
              ),
              ListTile(
                title: const Text('清除搜索历史'),
                subtitle: const Text('清除您的搜索记录'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: _isLoading
                    ? null
                    : () {
                        // TODO: 实现清除搜索历史功能
                      },
              ),
              ListTile(
                title: const Text('清除浏览历史'),
                subtitle: const Text('清除您的浏览记录'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: _isLoading
                    ? null
                    : () {
                        // TODO: 实现清除浏览历史功能
                      },
              ),
            ],
          ),
          _buildSection(
            '隐私政策',
            [
              ListTile(
                title: const Text('隐私政策'),
                subtitle: const Text('了解我们如何保护您的隐私'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () {
                  // TODO: 打开隐私政策页面
                },
              ),
              ListTile(
                title: const Text('Cookie政策'),
                subtitle: const Text('了解我们如何使用Cookie'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () {
                  // TODO: 打开Cookie政策页面
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
    String settingKey,
  ) {
    return SwitchListTile(
      title: Text(title),
      subtitle: Text(
        subtitle,
        style: TextStyle(
          color: Colors.grey[600],
        ),
      ),
      value: _settings[settingKey]!,
      onChanged: _isLoading
          ? null
          : (value) {
              setState(() {
                _settings[settingKey] = value;
              });
            },
    );
  }
} 