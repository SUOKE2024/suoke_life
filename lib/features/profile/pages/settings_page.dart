import 'package:flutter/material.dart';

class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('我的'),
      ),
      body: ListView(
        children: [
          ListTile(
            leading: const CircleAvatar(
              backgroundImage: AssetImage('assets/images/default_avatar.png'),
            ),
            title: const Text('用户名'),
            subtitle: const Text('积分: 1200'),
            onTap: () {
              // 实现用户信息逻辑
              Navigator.pushNamed(context, '/userProfile');
            },
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.settings),
            title: const Text('系统设置'),
            onTap: () {
              // 实现系统设置逻辑
              Navigator.pushNamed(context, '/systemSettings');
            },
          ),
          ListTile(
            leading: const Icon(Icons.security),
            title: const Text('安全设置'),
            onTap: () {
              // 实现安全设置逻辑
              Navigator.pushNamed(context, '/securitySettings');
            },
          ),
          ListTile(
            leading: const Icon(Icons.info),
            title: const Text('关于我们'),
            onTap: () {
              // 实现关于我们逻辑
              showAboutDialog(
                context: context,
                applicationName: '索克生活',
                applicationVersion: '1.0.0',
                children: [
                  const Text('索克生活是一款帮助用户管理健康生活的应用。'),
                ],
              );
            },
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // 实现 AI 代理交互逻辑
          Navigator.pushNamed(context, '/aiAgentChat');
        },
        child: const Icon(Icons.chat),
      ),
    );
  }
} 