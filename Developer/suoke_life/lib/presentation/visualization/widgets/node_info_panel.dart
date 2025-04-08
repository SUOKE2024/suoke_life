import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/domain/entities/knowledge_graph.dart';
import 'package:suoke_life/presentation/visualization/providers/visualization_providers.dart';

class NodeInfoPanel extends ConsumerWidget {
  final String nodeId;
  final VoidCallback onClose;

  const NodeInfoPanel({
    super.key,
    required this.nodeId,
    required this.onClose,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final visualizationState = ref.watch(visualizationControllerProvider);
    final node = visualizationState.nodes.firstWhere(
      (n) => n.id == nodeId,
      orElse: () => throw Exception('Node not found'),
    );

    return Card(
      elevation: 4,
      child: Container(
        width: 300,
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '节点信息',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: onClose,
                ),
              ],
            ),
            const Divider(),
            _buildNodeInfo(context, node),
            const SizedBox(height: 16),
            _buildNodeActions(context, node),
          ],
        ),
      ),
    );
  }

  Widget _buildNodeInfo(BuildContext context, KnowledgeNode node) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '名称：${node.name}',
          style: Theme.of(context).textTheme.bodyLarge,
        ),
        const SizedBox(height: 8),
        Text(
          '类型：${node.type}',
          style: Theme.of(context).textTheme.bodyMedium,
        ),
        if (node.description != null) ...[
          const SizedBox(height: 8),
          Text(
            '描述：${node.description}',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ],
        const SizedBox(height: 8),
        Text(
          '属性：',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        ...node.properties.entries.map((entry) => Padding(
          padding: const EdgeInsets.only(left: 16, top: 4),
          child: Text(
            '${entry.key}: ${entry.value}',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        )),
      ],
    );
  }

  Widget _buildNodeActions(BuildContext context, KnowledgeNode node) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        ElevatedButton.icon(
          icon: const Icon(Icons.edit),
          label: const Text('编辑'),
          onPressed: () {
            // 实现编辑功能
          },
        ),
        ElevatedButton.icon(
          icon: const Icon(Icons.delete),
          label: const Text('删除'),
          onPressed: () {
            // 实现删除功能
          },
        ),
        ElevatedButton.icon(
          icon: const Icon(Icons.share),
          label: const Text('分享'),
          onPressed: () {
            // 实现分享功能
          },
        ),
      ],
    );
  }
}