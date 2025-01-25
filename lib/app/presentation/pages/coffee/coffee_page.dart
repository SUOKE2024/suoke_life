import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class CoffeePage extends StatelessWidget {
  const CoffeePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('咖啡')),
      body: const Center(child: Text('咖啡页面')),
    );
  }
} 