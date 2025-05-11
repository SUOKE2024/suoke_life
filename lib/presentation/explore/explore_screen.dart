import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

/// 探索屏幕
@RoutePage()
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
