import 'package:flutter/material.dart';

class KnowledgeGraph extends StatelessWidget {
  final Map<String, dynamic> data;

  const KnowledgeGraph({
    Key? key,
    required this.data,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListView(
        shrinkWrap: true,
        children: [
          for (final node in data['nodes'] as List)
            ListTile(
              title: Text(node['label'] as String),
              subtitle: Text(node['description'] as String? ?? ''),
              onTap: () {
                // TODO: 处理节点点击
              },
            ),
        ],
      ),
    );
  }
} 