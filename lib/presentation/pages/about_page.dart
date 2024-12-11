import 'package:flutter/material.dart';
import 'package:package_info_plus/package_info_plus.dart';

class AboutPage extends StatefulWidget {
  const AboutPage({super.key});

  @override
  State<AboutPage> createState() => _AboutPageState();
}

class _AboutPageState extends State<AboutPage> {
  String _version = '';

  @override
  void initState() {
    super.initState();
    _loadVersion();
  }

  Future<void> _loadVersion() async {
    final packageInfo = await PackageInfo.fromPlatform();
    setState(() {
      _version = packageInfo.version;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('关于我们'),
      ),
      body: ListView(
        children: [
          const SizedBox(height: 32),
          Center(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(20),
              child: Image.asset(
                'assets/images/app_icon.png',
                width: 100,
                height: 100,
              ),
            ),
          ),
          const SizedBox(height: 16),
          Center(
            child: Text(
              '索客生活',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
          ),
          Center(
            child: Text(
              '版本 $_version',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
          const SizedBox(height: 32),
          ListTile(
            leading: const Icon(Icons.update),
            title: const Text('检查更新'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              // TODO: 实现检查更新功能
            },
          ),
          ListTile(
            leading: const Icon(Icons.description),
            title: const Text('用户协议'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              Navigator.pushNamed(context, '/terms');
            },
          ),
          ListTile(
            leading: const Icon(Icons.privacy_tip),
            title: const Text('隐私政策'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              Navigator.pushNamed(context, '/privacy');
            },
          ),
          const SizedBox(height: 32),
          const Center(
            child: Text(
              '© 2024 索客生活. All rights reserved.',
              style: TextStyle(
                color: Colors.grey,
                fontSize: 12,
              ),
            ),
          ),
        ],
      ),
    );
  }
} 