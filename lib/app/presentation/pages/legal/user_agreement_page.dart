import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class UserAgreementPage extends StatelessWidget {
  const UserAgreementPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('用户协议')),
      body: const Center(child: Text('用户协议页面')),
    );
  }
} 