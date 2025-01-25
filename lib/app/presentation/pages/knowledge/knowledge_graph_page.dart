import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class KnowledgeGraphPage extends StatelessWidget {
  const KnowledgeGraphPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('知识图谱')),
      body: const Center(child: Text('知识图谱页面')),
    );
  }
} 