import 'package:flutter/material.dart';
import 'package:graphview/GraphView.dart';

class KnowledgeGraph extends StatelessWidget {
  final Map<String, dynamic> data;

  const KnowledgeGraph({
    Key? key,
    required this.data,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final graph = Graph();
    final builder = SugiyamaConfiguration()
      ..nodeSeparation = 60
      ..levelSeparation = 100;

    // 构建节点和边
    final nodes = <Node>[];
    final edges = <Edge>[];

    // 添加节点
    for (final node in data['nodes'] ?? []) {
      nodes.add(Node.Id(node['id'])
        ..data = Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Theme.of(context).primaryColor,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            node['label'] as String,
            style: const TextStyle(color: Colors.white),
          ),
        ));
    }

    // 添加边
    for (final edge in data['edges'] ?? []) {
      edges.add(Edge(
        Node.Id(edge['from']),
        Node.Id(edge['to']),
        paint: Paint()
          ..color = Colors.grey
          ..strokeWidth = 1,
      ));
    }

    // 添加到图中
    graph.addNodes(nodes);
    graph.addEdges(edges);

    return SizedBox(
      height: 300,
      child: InteractiveViewer(
        constrained: false,
        boundaryMargin: const EdgeInsets.all(100),
        minScale: 0.01,
        maxScale: 5.6,
        child: GraphView(
          graph: graph,
          algorithm: SugiyamaAlgorithm(builder),
          paint: Paint()
            ..color = Colors.grey
            ..strokeWidth = 1
            ..style = PaintingStyle.stroke,
        ),
      ),
    );
  }
} 