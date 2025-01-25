import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class LicensesPage extends StatelessWidget {
  const LicensesPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('开源许可')),
      body: const LicensePage(
        applicationName: 'SUOKE',
        applicationVersion: '1.0.0',
        applicationLegalese: '© 2024 SUOKE Team',
      ),
    );
  }
} 