import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class HistoryPage extends StatelessWidget {
  const HistoryPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('历史记录')),
      body: ListView.builder(
        itemCount: 10, // TODO: Replace with actual data
        itemBuilder: (context, index) {
          return ListTile(
            title: Text('记录 ${index + 1}'),
            subtitle: Text('2024-${index + 1}-01'),
            trailing: const Icon(Icons.chevron_right),
          );
        },
      ),
    );
  }
} 