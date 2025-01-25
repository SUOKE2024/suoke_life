import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class AboutPage extends StatelessWidget {
  const AboutPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('关于')),
      body: ListView(
        children: const [
          ListTile(
            title: Text('版本'),
            trailing: Text('1.0.0'),
          ),
          ListTile(
            title: Text('开发者'),
            trailing: Text('SUOKE Team'),
          ),
          ListTile(
            title: Text('版权所有'),
            trailing: Text('© 2024'),
          ),
        ],
      ),
    );
  }
} 