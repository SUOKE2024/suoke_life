import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class RegisterPage extends StatelessWidget {
  const RegisterPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('注册')),
      body: const Center(child: Text('注册页面')),
    );
  }
} 