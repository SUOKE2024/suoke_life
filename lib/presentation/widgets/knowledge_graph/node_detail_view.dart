import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../domain/entities/knowledge_node.dart';
import '../../../domain/entities/knowledge_relation.dart';
import '../../../presentation/providers/knowledge_graph_providers.dart';

class NodeDetailView extends ConsumerWidget {
  const NodeDetailView({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedNode = ref.watch(selectedNodeProvider);
    
    if (selectedNode == null) {
      return const SizedBox.shrink();
    }
    
    return Card(
      margin: const EdgeInsets.all(16.0),
      elevation: 8.0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16.0)),
      child: Container(
        width: 320,
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeader(context, selectedNode),
            const Divider(height: 24.0),
            _buildDetailInfo(context, selectedNode),
            const SizedBox(height: 16.0),
            _buildRelatedNodes(context, ref, selectedNode),
            const SizedBox(height: 16.0),
            _buildActionButtons(context, ref, selectedNode),
          ],
        ),
      ),
    );
  }
  
  Widget _buildHeader(BuildContext context, KnowledgeNode node) {
    return Row(
      children: [
        Container(
          width: 48.0,
          height: 48.0,
          decoration: BoxDecoration(
            color: _getNodeColor(node.type),
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(
              node.name.substring(0, 1),
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 20.0,
              ),
            ),
          ),
        ),
        const SizedBox(width: 16.0),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                node.name,
                style: Theme.of(context).textTheme.titleLarge,
                overflow: TextOverflow.ellipsis,
              ),
              Text(
                '类型: ${node.type}',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ),
        IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => _closeDetail(context),
        ),
      ],
    );
  }
  
  Widget _buildDetailInfo(BuildContext context, KnowledgeNode node) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildInfoRow(context, '主题', node.topic),
        _buildInfoRow(context, '权重', node.weight.toString()),
        _buildInfoRow(context, '描述', node.description ?? '暂无描述'),
      ],
    );
  }
  
  Widget _buildInfoRow(BuildContext context, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              '$label:',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildRelatedNodes(BuildContext context, WidgetRef ref, KnowledgeNode node) {
    final relationsAsync = ref.watch(knowledgeRelationsProvider);
    
    return relationsAsync.when(
      data: (relations) {
        // 过滤出与当前节点相关的关系
        final relatedRelations = relations.where((relation) => 
          relation.sourceId == node.id || relation.targetId == node.id
        ).toList();
        
        if (relatedRelations.isEmpty) {
          return const Text('没有相关节点');
        }
        
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '相关节点',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8.0),
            SizedBox(
              height: 120.0,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                itemCount: relatedRelations.length,
                itemBuilder: (context, index) {
                  return _buildRelatedNodeItem(
                    context, 
                    ref, 
                    node, 
                    relatedRelations[index],
                  );
                },
              ),
            ),
          ],
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stack) => Text('加载关系数据出错: $error'),
    );
  }
  
  Widget _buildRelatedNodeItem(
    BuildContext context,
    WidgetRef ref,
    KnowledgeNode currentNode,
    KnowledgeRelation relation,
  ) {
    final nodesAsync = ref.watch(knowledgeNodesProvider);
    
    return nodesAsync.when(
      data: (nodes) {
        // 确定关联节点
        final String relatedNodeId = relation.sourceId == currentNode.id 
            ? relation.targetId 
            : relation.sourceId;
        
        final relatedNode = nodes.firstWhere(
          (node) => node.id == relatedNodeId,
          orElse: () => KnowledgeNode(
            id: 'unknown',
            name: '未知节点',
            type: '未知',
            topic: '未知',
          ),
        );
        
        final isSourceNode = relation.sourceId == currentNode.id;
        
        return Card(
          margin: const EdgeInsets.only(right: 8.0),
          child: InkWell(
            onTap: () {
              // 切换到关联节点
              ref.read(selectedNodeProvider.notifier).state = relatedNode;
            },
            child: Container(
              width: 120.0,
              padding: const EdgeInsets.all(8.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    width: 32.0,
                    height: 32.0,
                    decoration: BoxDecoration(
                      color: _getNodeColor(relatedNode.type),
                      shape: BoxShape.circle,
                    ),
                    child: Center(
                      child: Text(
                        relatedNode.name.substring(0, 1),
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 4.0),
                  Text(
                    relatedNode.name,
                    textAlign: TextAlign.center,
                    overflow: TextOverflow.ellipsis,
                    maxLines: 2,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 4.0),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      if (!isSourceNode) const Icon(Icons.arrow_back_ios, size: 14.0),
                      Text(
                        relation.type,
                        style: Theme.of(context).textTheme.bodySmall,
                        overflow: TextOverflow.ellipsis,
                      ),
                      if (isSourceNode) const Icon(Icons.arrow_forward_ios, size: 14.0),
                    ],
                  ),
                ],
              ),
            ),
          ),
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stack) => Text('加载节点数据出错: $error'),
    );
  }
  
  Widget _buildActionButtons(BuildContext context, WidgetRef ref, KnowledgeNode node) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.end,
      children: [
        TextButton.icon(
          icon: const Icon(Icons.edit),
          label: const Text('编辑'),
          onPressed: () => _showEditDialog(context, ref, node),
        ),
        const SizedBox(width: 8.0),
        TextButton.icon(
          icon: const Icon(Icons.add_link),
          label: const Text('添加关系'),
          onPressed: () => _showAddRelationDialog(context, ref, node),
        ),
      ],
    );
  }
  
  void _closeDetail(BuildContext context) {
    // 清除选中状态
    Navigator.of(context).maybePop();
  }
  
  void _showEditDialog(BuildContext context, WidgetRef ref, KnowledgeNode node) {
    // 显示编辑节点对话框
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('编辑节点'),
        content: const Text('节点编辑功能将在后续版本实现'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('关闭'),
          ),
        ],
      ),
    );
  }
  
  void _showAddRelationDialog(BuildContext context, WidgetRef ref, KnowledgeNode node) {
    // 显示添加关系对话框
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('添加新关系'),
        content: const Text('添加关系功能将在后续版本实现'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('关闭'),
          ),
        ],
      ),
    );
  }
  
  Color _getNodeColor(String nodeType) {
    const Map<String, Color> typeColors = {
      '主题': Colors.red,
      '概念': Colors.blue,
      '方法': Colors.green,
      '实例': Colors.purple,
      '疾病': Colors.orange,
      '症状': Colors.teal,
      '治疗方法': Colors.indigo,
    };
    
    return typeColors[nodeType] ?? Colors.grey;
  }
} 