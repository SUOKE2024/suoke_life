import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class TCMTestPage extends StatelessWidget {
  const TCMTestPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('中医体质测试')),
      body: const Center(child: Text('中医体质测试页面')),
    );
  }
} 