import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class HelpPage extends StatelessWidget {
  const HelpPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('帮助')),
      body: ListView(
        children: const [
          ListTile(
            leading: Icon(Icons.help_outline),
            title: Text('常见问题'),
          ),
          ListTile(
            leading: Icon(Icons.book),
            title: Text('使用指南'),
          ),
          ListTile(
            leading: Icon(Icons.support_agent),
            title: Text('联系客服'),
          ),
        ],
      ),
    );
  }
} 