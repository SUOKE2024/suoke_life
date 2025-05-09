import 'package:flutter/material.dart';

/// 探索屏幕
class ExploreScreen extends StatelessWidget {
  /// 构造函数
  const ExploreScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('探索'),
      ),
      body: const Center(
        child: Text('探索内容'),
      ),
    );
  }
}
