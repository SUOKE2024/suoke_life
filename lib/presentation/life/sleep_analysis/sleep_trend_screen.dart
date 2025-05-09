import 'package:flutter/material.dart';

/// 睡眠趋势屏幕
class SleepTrendScreen extends StatelessWidget {
  /// 构造函数
  const SleepTrendScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('睡眠趋势'),
      ),
      body: const Center(
        child: Text('睡眠趋势分析功能开发中'),
      ),
    );
  }
}
