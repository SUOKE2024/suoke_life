import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';

import '../../../domain/entities/knowledge_node.dart';
import '../../../domain/entities/knowledge_relation.dart';
import '../../../presentation/providers/knowledge_graph_providers.dart';

class KnowledgeGraphView extends ConsumerWidget {
  const KnowledgeGraphView({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final zoomLevel = ref.watch(knowledgeGraphZoomLevelProvider);
    final layoutType = ref.watch(layoutTypeProvider);
    final nodesAsync = ref.watch(knowledgeNodesProvider);
    final relationsAsync = ref.watch(knowledgeRelationsProvider);
    
    return nodesAsync.when(
      data: (nodes) {
        return relationsAsync.when(
          data: (relations) {
            if (nodes.isEmpty) {
              return const Center(
                child: Text('没有找到节点数据，请尝试其他主题或添加新节点'),
              );
            }
            
            return InteractiveViewer(
              boundaryMargin: const EdgeInsets.all(double.infinity),
              minScale: 0.5,
              maxScale: 2.5,
              scaleEnabled: true,
              child: Center(
                child: SizedBox(
                  width: 1000 * zoomLevel,
                  height: 800 * zoomLevel,
                  child: _buildGraphLayout(
                    context,
                    ref,
                    nodes,
                    relations,
                    layoutType,
                  ),
                ),
              ),
            );
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stack) => Center(
            child: Text('加载关系数据出错: $error'),
          ),
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stack) => Center(
        child: Text('加载节点数据出错: $error'),
      ),
    );
  }
  
  Widget _buildGraphLayout(
    BuildContext context,
    WidgetRef ref,
    List<KnowledgeNode> nodes,
    List<KnowledgeRelation> relations,
    KnowledgeGraphLayoutType layoutType,
  ) {
    // 根据布局类型选择不同的布局算法
    switch (layoutType) {
      case KnowledgeGraphLayoutType.force:
        return _buildForceDirectedLayout(context, ref, nodes, relations);
      case KnowledgeGraphLayoutType.radial:
        return _buildRadialLayout(context, ref, nodes, relations);
      case KnowledgeGraphLayoutType.hierarchy:
        return _buildHierarchicalLayout(context, ref, nodes, relations);
      case KnowledgeGraphLayoutType.circular:
        return _buildCircularLayout(context, ref, nodes, relations);
      default:
        return _buildForceDirectedLayout(context, ref, nodes, relations);
    }
  }
  
  // 力导向布局
  Widget _buildForceDirectedLayout(
    BuildContext context,
    WidgetRef ref,
    List<KnowledgeNode> nodes,
    List<KnowledgeRelation> relations,
  ) {
    // 为简单起见，这里使用静态布局
    // 实际实现中，应该使用物理引擎实现力导向布局
    
    // 设置节点位置
    final random = Random(42); // 固定种子以保持一致性
    final width = 900.0;
    final height = 700.0;
    final centerX = width / 2;
    final centerY = height / 2;
    
    // 为尚未有位置的节点分配位置
    for (var node in nodes) {
      if (node.x == null || node.y == null) {
        // 为主题节点特殊处理，放在中心位置
        if (node.type == '主题') {
          node.x = centerX;
          node.y = centerY;
        } else {
          // 随机分配位置，但保持在一定范围内
          node.x = centerX + (random.nextDouble() - 0.5) * width * 0.7;
          node.y = centerY + (random.nextDouble() - 0.5) * height * 0.7;
        }
      }
    }
    
    // 创建节点ID到节点的映射表，方便查找
    final nodeMap = {for (var node in nodes) node.id: node};
    
    return CustomPaint(
      size: Size(width, height),
      painter: KnowledgeGraphPainter(
        nodes: nodes,
        relations: relations,
        nodeMap: nodeMap,
        selectedNodeId: ref.watch(selectedNodeProvider)?.id,
        onNodeTap: (node) {
          ref.read(selectedNodeProvider.notifier).state = node;
        },
      ),
    );
  }
  
  // 放射状布局
  Widget _buildRadialLayout(
    BuildContext context,
    WidgetRef ref,
    List<KnowledgeNode> nodes,
    List<KnowledgeRelation> relations,
  ) {
    // 简化实现：找到主题节点作为中心，其他节点围绕中心节点放置
    final width = 900.0;
    final height = 700.0;
    final centerX = width / 2;
    final centerY = height / 2;
    
    // 找出主要节点（通常是主题节点或具有最多关系的节点）
    var centerNode = nodes.firstWhere(
      (node) => node.type == '主题',
      orElse: () => nodes.first,
    );
    
    // 设置中心节点位置
    centerNode.x = centerX;
    centerNode.y = centerY;
    
    // 计算每个节点与中心节点的连接关系
    final nodeRelations = <String, List<KnowledgeRelation>>{};
    for (var relation in relations) {
      if (relation.sourceId == centerNode.id) {
        nodeRelations.putIfAbsent(relation.targetId, () => []).add(relation);
      } else if (relation.targetId == centerNode.id) {
        nodeRelations.putIfAbsent(relation.sourceId, () => []).add(relation);
      }
    }
    
    // 计算角度增量
    final angleIncrement = 2 * pi / (nodes.length - 1);
    var currentAngle = 0.0;
    
    // 设置其他节点位置
    for (var node in nodes) {
      if (node != centerNode) {
        // 围绕中心节点放置
        final radius = 250.0; // 可以根据节点类型调整不同层级的半径
        node.x = centerX + radius * cos(currentAngle);
        node.y = centerY + radius * sin(currentAngle);
        currentAngle += angleIncrement;
      }
    }
    
    // 创建节点ID到节点的映射表
    final nodeMap = {for (var node in nodes) node.id: node};
    
    return CustomPaint(
      size: Size(width, height),
      painter: KnowledgeGraphPainter(
        nodes: nodes,
        relations: relations,
        nodeMap: nodeMap,
        selectedNodeId: ref.watch(selectedNodeProvider)?.id,
        onNodeTap: (node) {
          ref.read(selectedNodeProvider.notifier).state = node;
        },
      ),
    );
  }
  
  // 层次结构布局
  Widget _buildHierarchicalLayout(
    BuildContext context,
    WidgetRef ref,
    List<KnowledgeNode> nodes,
    List<KnowledgeRelation> relations,
  ) {
    // 简化版层次结构布局
    final width = 900.0;
    final height = 700.0;
    
    // 按类型分组节点
    final nodesByType = <String, List<KnowledgeNode>>{};
    for (var node in nodes) {
      nodesByType.putIfAbsent(node.type, () => []).add(node);
    }
    
    // 按层级排列
    final typeOrder = ['主题', '概念', '方法', '实例', '疾病', '症状', '治疗方法'];
    
    // 计算每层节点位置
    var currentY = 100.0;
    final levelSpacing = height / (typeOrder.length + 1);
    
    for (var type in typeOrder) {
      final typeNodes = nodesByType[type] ?? [];
      if (typeNodes.isNotEmpty) {
        final nodesPerRow = typeNodes.length;
        final nodeSpacing = width / (nodesPerRow + 1);
        
        for (var i = 0; i < typeNodes.length; i++) {
          final node = typeNodes[i];
          node.x = (i + 1) * nodeSpacing;
          node.y = currentY;
        }
        
        currentY += levelSpacing;
      }
    }
    
    // 处理未分类的节点
    final unclassifiedNodes = nodes.where(
      (node) => !typeOrder.contains(node.type)
    ).toList();
    
    if (unclassifiedNodes.isNotEmpty) {
      final nodesPerRow = unclassifiedNodes.length;
      final nodeSpacing = width / (nodesPerRow + 1);
      
      for (var i = 0; i < unclassifiedNodes.length; i++) {
        final node = unclassifiedNodes[i];
        if (node.x == null || node.y == null) {
          node.x = (i + 1) * nodeSpacing;
          node.y = currentY;
        }
      }
    }
    
    // 创建节点ID到节点的映射表
    final nodeMap = {for (var node in nodes) node.id: node};
    
    return CustomPaint(
      size: Size(width, height),
      painter: KnowledgeGraphPainter(
        nodes: nodes,
        relations: relations,
        nodeMap: nodeMap,
        selectedNodeId: ref.watch(selectedNodeProvider)?.id,
        onNodeTap: (node) {
          ref.read(selectedNodeProvider.notifier).state = node;
        },
      ),
    );
  }
  
  // 环形布局
  Widget _buildCircularLayout(
    BuildContext context,
    WidgetRef ref,
    List<KnowledgeNode> nodes,
    List<KnowledgeRelation> relations,
  ) {
    final width = 900.0;
    final height = 700.0;
    final centerX = width / 2;
    final centerY = height / 2;
    
    // 简单环形布局：所有节点均匀分布在圆上
    final radius = min(width, height) * 0.4;
    final angleIncrement = 2 * pi / nodes.length;
    
    for (var i = 0; i < nodes.length; i++) {
      final node = nodes[i];
      final angle = i * angleIncrement;
      node.x = centerX + radius * cos(angle);
      node.y = centerY + radius * sin(angle);
    }
    
    // 创建节点ID到节点的映射表
    final nodeMap = {for (var node in nodes) node.id: node};
    
    return CustomPaint(
      size: Size(width, height),
      painter: KnowledgeGraphPainter(
        nodes: nodes,
        relations: relations,
        nodeMap: nodeMap,
        selectedNodeId: ref.watch(selectedNodeProvider)?.id,
        onNodeTap: (node) {
          ref.read(selectedNodeProvider.notifier).state = node;
        },
      ),
    );
  }
}

class KnowledgeGraphPainter extends CustomPainter {
  final List<KnowledgeNode> nodes;
  final List<KnowledgeRelation> relations;
  final Map<String, KnowledgeNode> nodeMap;
  final String? selectedNodeId;
  final Function(KnowledgeNode)? onNodeTap;
  
  KnowledgeGraphPainter({
    required this.nodes,
    required this.relations,
    required this.nodeMap,
    this.selectedNodeId,
    this.onNodeTap,
  });
  
  static const Map<String, Color> typeColors = {
    '主题': Colors.red,
    '概念': Colors.blue,
    '方法': Colors.green,
    '实例': Colors.purple,
    '疾病': Colors.orange,
    '症状': Colors.teal,
    '治疗方法': Colors.indigo,
  };
  
  @override
  void paint(Canvas canvas, Size size) {
    // 绘制关系线
    for (var relation in relations) {
      final sourceNode = nodeMap[relation.sourceId];
      final targetNode = nodeMap[relation.targetId];
      
      if (sourceNode != null && targetNode != null &&
          sourceNode.x != null && sourceNode.y != null &&
          targetNode.x != null && targetNode.y != null) {
        
        // 是否为选中节点的关系
        final isSelectedRelation = selectedNodeId != null &&
            (relation.sourceId == selectedNodeId || relation.targetId == selectedNodeId);
        
        // 关系线宽度
        final strokeWidth = isSelectedRelation ? 2.5 : 1.0;
        
        // 关系线颜色
        final color = isSelectedRelation
            ? Colors.orangeAccent
            : Colors.grey.withOpacity(0.8);
        
        final paint = Paint()
          ..color = color
          ..strokeWidth = strokeWidth
          ..style = PaintingStyle.stroke;
        
        // 绘制关系线
        canvas.drawLine(
          Offset(sourceNode.x!, sourceNode.y!),
          Offset(targetNode.x!, targetNode.y!),
          paint,
        );
        
        // 绘制关系类型标签
        if (isSelectedRelation) {
          final midX = (sourceNode.x! + targetNode.x!) / 2;
          final midY = (sourceNode.y! + targetNode.y!) / 2;
          
          final textSpan = TextSpan(
            text: relation.type,
            style: const TextStyle(
              color: Colors.black87,
              fontSize: 12,
              fontWeight: FontWeight.bold,
              backgroundColor: Colors.white70,
            ),
          );
          
          final textPainter = TextPainter(
            text: textSpan,
            textDirection: TextDirection.ltr,
            textAlign: TextAlign.center,
          );
          
          textPainter.layout();
          textPainter.paint(
            canvas, 
            Offset(midX - textPainter.width / 2, midY - textPainter.height / 2),
          );
        }
        
        // 如果是双向关系，绘制箭头
        if (relation.isBidirectional) {
          // 双箭头标记（简化版，实际应用中可使用更复杂的箭头标记）
        } else {
          // 单向箭头标记
          _drawArrow(canvas, sourceNode.x!, sourceNode.y!, targetNode.x!, targetNode.y!, paint);
        }
      }
    }
    
    // 绘制节点
    for (var node in nodes) {
      if (node.x != null && node.y != null) {
        final isSelected = node.id == selectedNodeId;
        
        // 节点大小
        final nodeRadius = isSelected ? 24.0 : 18.0 + (node.weight - 1) * 5;
        
        // 节点颜色
        final color = typeColors[node.type] ?? Colors.grey;
        
        // 节点背景
        final paint = Paint()
          ..color = isSelected ? color : color.withOpacity(0.8)
          ..style = PaintingStyle.fill;
        
        // 节点边框
        final borderPaint = Paint()
          ..color = isSelected ? Colors.yellow : Colors.white
          ..strokeWidth = isSelected ? 3.0 : 1.5
          ..style = PaintingStyle.stroke;
        
        // 绘制节点
        canvas.drawCircle(Offset(node.x!, node.y!), nodeRadius, paint);
        canvas.drawCircle(Offset(node.x!, node.y!), nodeRadius, borderPaint);
        
        // 绘制节点标签
        final textSpan = TextSpan(
          text: node.name,
          style: TextStyle(
            color: Colors.white,
            fontSize: isSelected ? 14 : 12,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
          ),
        );
        
        final textPainter = TextPainter(
          text: textSpan,
          textDirection: TextDirection.ltr,
          textAlign: TextAlign.center,
        );
        
        textPainter.layout();
        textPainter.paint(
          canvas, 
          Offset(node.x! - textPainter.width / 2, node.y! - textPainter.height / 2),
        );
      }
    }
  }
  
  // 绘制箭头
  void _drawArrow(Canvas canvas, double x1, double y1, double x2, double y2, Paint paint) {
    // 箭头参数
    const arrowLength = 12.0;
    const arrowAngle = 25.0 * pi / 180; // 箭头角度（25度）
    
    // 计算线条角度
    final angle = atan2(y2 - y1, x2 - x1);
    
    // 箭头位置（离目标节点稍微远一点）
    final arrowX = x2 - 20 * cos(angle);
    final arrowY = y2 - 20 * sin(angle);
    
    // 计算箭头两个点
    final pt1x = arrowX - arrowLength * cos(angle - arrowAngle);
    final pt1y = arrowY - arrowLength * sin(angle - arrowAngle);
    
    final pt2x = arrowX - arrowLength * cos(angle + arrowAngle);
    final pt2y = arrowY - arrowLength * sin(angle + arrowAngle);
    
    // 绘制箭头
    final path = Path();
    path.moveTo(arrowX, arrowY);
    path.lineTo(pt1x, pt1y);
    path.lineTo(pt2x, pt2y);
    path.close();
    
    canvas.drawPath(path, paint..style = PaintingStyle.fill);
  }
  
  @override
  bool shouldRepaint(KnowledgeGraphPainter oldDelegate) {
    return oldDelegate.nodes != nodes ||
           oldDelegate.relations != relations ||
           oldDelegate.selectedNodeId != selectedNodeId;
  }
  
  // 检测点击节点
  bool hitTest(Offset position) {
    for (var node in nodes) {
      if (node.x != null && node.y != null) {
        final distance = (position - Offset(node.x!, node.y!)).distance;
        final nodeRadius = 20.0 + (node.weight - 1) * 5;
        
        if (distance <= nodeRadius) {
          if (onNodeTap != null) {
            onNodeTap!(node);
          }
          return true;
        }
      }
    }
    return false;
  }
} 