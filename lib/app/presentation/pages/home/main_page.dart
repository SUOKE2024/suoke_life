import 'package:flutter/material.dart';
import 'package:get/get.dart';

class MainPage extends StatelessWidget {
  const MainPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('首页'),
        actions: [
          // 加号图标1
          IconButton(
            icon: const Icon(Icons.add_circle_outline),
            onPressed: () {
              // 显示添加朋友、发起群聊等菜单
            },
          ),
          // 加号图标2
          IconButton(
            icon: const Icon(Icons.person_add),
            onPressed: () {
              // 显示会员注册、专家注册菜单
            },
          ),
        ],
      ),
      body: ListView(
        children: [
          // 聊天列表
          ListTile(
            leading: const CircleAvatar(child: Text('小艾')),
            title: const Text('小艾'),
            subtitle: const Text('最新消息...'),
            onTap: () => Navigator.pushNamed('/chat/detail'),
          ),
          ListTile(
            leading: const CircleAvatar(child: Text('老克')),
            title: const Text('老克'),
            subtitle: const Text('最新消息...'),
            onTap: () => Navigator.pushNamed('/chat/detail'),
          ),
          ListTile(
            leading: const CircleAvatar(child: Text('小克')),
            title: const Text('小克'),
            subtitle: const Text('最新消息...'),
            onTap: () => Navigator.pushNamed('/chat/detail'),
          ),
        ],
      ),
    );
  }
} 