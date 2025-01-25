import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('设置')),
      body: ListView(
        children: const [
          ListTile(
            leading: Icon(Icons.person),
            title: Text('个人信息'),
          ),
          ListTile(
            leading: Icon(Icons.notifications),
            title: Text('通知设置'),
          ),
          ListTile(
            leading: Icon(Icons.security),
            title: Text('隐私设置'),
          ),
          ListTile(
            leading: Icon(Icons.help),
            title: Text('帮助与反馈'),
          ),
          ListTile(
            leading: Icon(Icons.info),
            title: Text('关于'),
          ),
        ],
      ),
    );
  }
} 