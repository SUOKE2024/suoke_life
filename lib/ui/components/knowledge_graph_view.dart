import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:graphview/graphview.dart';
import 'package:suoke_life_app_app/core/network/clients/health_service_client.dart';
import 'package:suoke_life_app_app/features/health/models/health_data_model.dart';

class KnowledgeGraphView extends ConsumerStatefulWidget {
  final String userId;
  final HealthProfile healthProfile;

  const KnowledgeGraphView({
    super.key,
    required this.userId,
    required this.healthProfile,
  });

  @override
  ConsumerState<KnowledgeGraphView> createState() => _KnowledgeGraphViewState();
}

class _KnowledgeGraphViewState extends ConsumerState<KnowledgeGraphView> {
  late final Graph _graph;
  late final BuchheimWalkerConfiguration _algorithm;
  final Map<String, Node> _nodeMap = {};

  @override
  void initState() {
    super.initState();
    _initializeGraph();
    _algorithm = BuchheimWalkerConfiguration()
      ..orientation = BuchheimWalkerConfiguration.ORIENTATION_TOP_BOTTOM;
  }

  void _initializeGraph() {
    _graph = Graph();
    _buildKnowledgeNodes();
    _buildKnowledgeConnections();
  }

  void _buildKnowledgeNodes() {
    for (final node in widget.healthProfile.knowledgeNodes) {
      final graphNode = Node.Id(_anonymizeId(node.id));
      _nodeMap[_anonymizeId(node.id)] = graphNode;
      _graph.addNode(graphNode);
    }
  }

  void _buildKnowledgeConnections() {
    for (final connection in widget.healthProfile.knowledgeConnections) {
      final from = _nodeMap[_anonymizeId(connection.fromId)];
      final to = _nodeMap[_anonymizeId(connection.toId)];
      if (from != null && to != null) {
        _graph.addEdge(from, to);
      }
    }
  }

  String _anonymizeId(String originalId) {
    // 实现SHA256哈希处理（需集成加密服务）
    return '${originalId}_hashed';
  }

  Color _getCategoryColor(KnowledgeCategory category) {
    return switch (category) {
      KnowledgeCategory.diet => Colors.green,
      KnowledgeCategory.exercise => Colors.blue,
      KnowledgeCategory.sleep => Colors.purple,
      KnowledgeCategory.mental => Colors.orange,
      _ => Colors.grey,
    };
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<HealthProfile>(
      future: HealthServiceClient().getKnowledgeGraph(
        userId: widget.userId,
        cacheStrategy: CacheStrategy.multiLevel,
      ),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError) {
          return Center(child: Text('加载失败: ${snapshot.error}'));
        }

        final data = snapshot.data!;
        
        return InteractiveViewer(
          constrained: false,
          boundaryMargin: const EdgeInsets.all(100),
          minScale: 0.01,
          maxScale: 5.6,
          child: GraphView(
            graph: _graph,
            algorithm: _algorithm,
            builder: (node) {
              final nodeData = data.knowledgeNodes.firstWhere(
                (n) => _anonymizeId(n.id) == node.key?.value,
              );
              
              return Semantics(
                label: '知识节点：${nodeData.label}',
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: _getCategoryColor(nodeData.category).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: _getCategoryColor(nodeData.category),
                      width: 2,
                    ),
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        nodeData.label,
                        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: _getCategoryColor(nodeData.category),
                        ),
                      ),
                      if (nodeData.description != null)
                        Padding(
                          padding: const EdgeInsets.only(top: 8),
                          child: Text(
                            nodeData.description!,
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ),
                    ],
                  ),
                ),
              );
            },
          ),
        );
      },
    );
  }
}
