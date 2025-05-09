import 'package:flutter/material.dart';

/// 个人资料屏幕
class ProfileScreen extends StatelessWidget {
  /// 构造函数
  const ProfileScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('个人资料'),
      ),
      body: const Center(
        child: Text('个人资料内容'),
      ),
    );
  }
}
