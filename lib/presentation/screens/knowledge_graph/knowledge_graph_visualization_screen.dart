import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:graphview/graphview.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/utils/logger.dart';
import '../../../domain/entities/knowledge_node.dart';
import '../../../domain/entities/node_relation.dart';
import '../../../di/providers/knowledge_providers.dart';
import '../../widgets/error_view.dart';
import '../../widgets/loading_view.dart';

/// 知识图谱可视化界面
class KnowledgeGraphVisualizationScreen extends ConsumerStatefulWidget {
  /// 标题
  final String title;
  
  /// 初始节点类型
  final String? initialNodeType;
  
  /// 构造函数
  const KnowledgeGraphVisualizationScreen({
    super.key,
    this.title = '知识图谱',
    this.initialNodeType,
  });

  @override
  ConsumerState<KnowledgeGraphVisualizationScreen> createState() => _KnowledgeGraphVisualizationScreenState();
}

class _KnowledgeGraphVisualizationScreenState extends ConsumerState<KnowledgeGraphVisualizationScreen> {
  /// 图谱布局算法
  final Algorithm _algorithm = FruchtermanReingoldAlgorithm();
  
  /// 缩放控制器
  final TransformationController _transformationController = TransformationController();
  
  /// 图谱
  final Graph _graph = Graph()..isTree = false;
  
  /// 当前选中的节点
  KnowledgeNode? _selectedNode;
  
  /// 节点类型过滤
  String? _selectedNodeType;
  
  /// 搜索关键词
  String _searchKeyword = '';
  
  /// 可用的节点类型
  List<String> _availableNodeTypes = [];
  
  @override
  void initState() {
    super.initState();
    _selectedNodeType = widget.initialNodeType;
  }
  
  @override
  void dispose() {
    _transformationController.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => _refreshGraph(),
            tooltip: '刷新图谱',
          ),
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () => _showSearchDialog(),
            tooltip: '搜索节点',
          ),
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: () => _showFilterDialog(),
            tooltip: '过滤节点',
          ),
        ],
      ),
      body: Column(
        children: [
          // 过滤器栏
          if (_selectedNodeType != null)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: Colors.grey.shade200,
              child: Row(
                children: [
                  const Text('过滤: ', style: TextStyle(fontWeight: FontWeight.bold)),
                  Chip(
                    label: Text(_selectedNodeType!),
                    deleteIcon: const Icon(Icons.close, size: 16),
                    onDeleted: () => setState(() => _selectedNodeType = null),
                  ),
                  const Spacer(),
                  Text('${_graph.nodeCount()}个节点', style: const TextStyle(fontSize: 12)),
                ],
              ),
            ),
          
          // 图谱内容
          Expanded(
            child: _buildGraphContent(),
          ),
        ],
      ),
      // 选中节点详情
      bottomSheet: _selectedNode != null
          ? _buildNodeDetailSheet()
          : null,
    );
  }
  
  /// 构建图谱内容
  Widget _buildGraphContent() {
    return Consumer(
      builder: (context, ref, child) {
        // 如果有选择节点类型，则获取特定类型的节点
        final nodesProvider = _selectedNodeType != null
            ? nodesByTypeProvider(_selectedNodeType!)
            : allNodesProvider;
            
        final nodesAsync = ref.watch(nodesProvider);
        
        return nodesAsync.when(
          data: (nodes) {
            // 更新可用的节点类型
            _updateAvailableNodeTypes(nodes);
            
            // 如果有搜索关键词，过滤节点
            final filteredNodes = _searchKeyword.isEmpty
                ? nodes
                : nodes.where((node) => 
                    node.title.toLowerCase().contains(_searchKeyword.toLowerCase()) ||
                    (node.description?.toLowerCase().contains(_searchKeyword.toLowerCase()) ?? false)
                  ).toList();
                  
            if (filteredNodes.isEmpty) {
              return const Center(
                child: Text('没有找到匹配的节点'),
              );
            }
            
            // 构建图谱
            _buildGraph(filteredNodes);
            
            // 显示图谱
            return InteractiveViewer(
              transformationController: _transformationController,
              constrained: false,
              boundaryMargin: const EdgeInsets.all(64),
              minScale: 0.1,
              maxScale: 5.0,
              child: GraphView(
                graph: _graph,
                algorithm: _algorithm,
                paint: Paint()
                  ..color = Colors.black
                  ..strokeWidth = 1
                  ..style = PaintingStyle.stroke,
                builder: (Node node) {
                  // 获取知识节点
                  final knowledgeNode = node.data as KnowledgeNode;
                  final isSelected = _selectedNode?.id == knowledgeNode.id;
                  
                  // 根据节点类型选择颜色
                  final color = _getNodeColor(knowledgeNode.type);
                  
                  return GestureDetector(
                    onTap: () => _onNodeTap(knowledgeNode),
                    child: Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: color,
                        shape: BoxShape.circle,
                        border: isSelected 
                            ? Border.all(color: Colors.orange, width: 3)
                            : null,
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black26,
                            blurRadius: 5,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Center(
                        child: Text(
                          knowledgeNode.title,
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                          ),
                        ),
                      ),
                    ),
                  );
                },
              ),
            );
          },
          loading: () => const LoadingView(),
          error: (error, stack) {
            logger.e('加载知识图谱节点失败', error: error, stackTrace: stack);
            return ErrorView(
              message: '加载知识图谱失败',
              onRetry: _refreshGraph,
            );
          },
        );
      },
    );
  }
  
  /// 构建节点详情底部栏
  Widget _buildNodeDetailSheet() {
    if (_selectedNode == null) return const SizedBox.shrink();
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
        borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                _selectedNode!.title,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              IconButton(
                icon: const Icon(Icons.close),
                onPressed: () => setState(() => _selectedNode = null),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: _getNodeColor(_selectedNode!.type).withOpacity(0.2),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Text(
              _selectedNode!.type,
              style: TextStyle(
                color: _getNodeColor(_selectedNode!.type),
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
            ),
          ),
          const SizedBox(height: 16),
          if (_selectedNode!.description != null)
            Text(
              _selectedNode!.description!,
              style: const TextStyle(fontSize: 14),
            ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              OutlinedButton.icon(
                icon: const Icon(Icons.open_in_new),
                label: const Text('查看详情'),
                onPressed: () => _openNodeDetail(_selectedNode!),
              ),
            ],
          ),
        ],
      ),
    );
  }
  
  /// 构建图谱
  void _buildGraph(List<KnowledgeNode> nodes) {
    // 清空图谱
    _graph.clear();
    
    // 添加节点
    final nodeMap = <String, Node>{};
    for (final knowledgeNode in nodes) {
      final node = Node.Id(knowledgeNode.id)
        ..data = knowledgeNode;
      nodeMap[knowledgeNode.id] = node;
      _graph.addNode(node);
    }
    
    // TODO: 添加关系边 (需要获取节点关系)
    // 示例关系
    for (int i = 0; i < nodes.length; i++) {
      for (int j = i + 1; j < nodes.length; j++) {
        // 随机添加关系，实际应用中应该从数据源获取关系
        if (i % 3 == 0 && j % 2 == 0) {
          _graph.addEdge(
            nodeMap[nodes[i].id]!,
            nodeMap[nodes[j].id]!,
            paint: Paint()
              ..color = Colors.grey
              ..strokeWidth = 1.5,
          );
        }
      }
    }
    
    // 应用布局
    _algorithm.setOptions({
      'iterations': 1000,
      'cooling factor': 0.9,
      'optimal distance': 200.0,
    });
  }
  
  /// 获取节点颜色
  Color _getNodeColor(String nodeType) {
    // 根据节点类型返回不同颜色
    switch (nodeType) {
      case '中医理论':
        return Colors.red;
      case '西医概念':
        return Colors.blue;
      case '疾病':
        return Colors.purple;
      case '症状':
        return Colors.orange;
      case '治疗方法':
        return Colors.green;
      case '药材':
        return Colors.teal;
      case '食材':
        return Colors.amber;
      case '穴位':
        return Colors.indigo;
      default:
        // 使用哈希生成颜色
        final hash = nodeType.hashCode;
        return Color.fromARGB(
          255,
          (hash & 0xFF0000) >> 16,
          (hash & 0x00FF00) >> 8,
          hash & 0x0000FF,
        );
    }
  }
  
  /// 节点点击事件
  void _onNodeTap(KnowledgeNode node) {
    setState(() {
      _selectedNode = node;
    });
  }
  
  /// 打开节点详情
  void _openNodeDetail(KnowledgeNode node) {
    // TODO: 导航到节点详情页面
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('查看节点详情: ${node.title}')),
    );
  }
  
  /// 显示搜索对话框
  void _showSearchDialog() {
    showDialog(
      context: context,
      builder: (context) {
        String keyword = _searchKeyword;
        
        return AlertDialog(
          title: const Text('搜索节点'),
          content: TextField(
            decoration: const InputDecoration(
              hintText: '输入关键词',
              prefixIcon: Icon(Icons.search),
            ),
            onChanged: (value) => keyword = value,
            controller: TextEditingController(text: _searchKeyword),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('取消'),
            ),
            ElevatedButton(
              onPressed: () {
                setState(() => _searchKeyword = keyword);
                Navigator.pop(context);
              },
              child: const Text('搜索'),
            ),
          ],
        );
      },
    );
  }
  
  /// 显示过滤对话框
  void _showFilterDialog() {
    showDialog(
      context: context,
      builder: (context) {
        String? selectedType = _selectedNodeType;
        
        return AlertDialog(
          title: const Text('按类型过滤'),
          content: DropdownButtonFormField<String?>(
            value: selectedType,
            decoration: const InputDecoration(
              labelText: '节点类型',
              border: OutlineInputBorder(),
            ),
            items: [
              const DropdownMenuItem<String?>(
                value: null,
                child: Text('全部'),
              ),
              ..._availableNodeTypes.map((type) => DropdownMenuItem<String?>(
                value: type,
                child: Text(type),
              )),
            ],
            onChanged: (value) => selectedType = value,
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('取消'),
            ),
            ElevatedButton(
              onPressed: () {
                setState(() => _selectedNodeType = selectedType);
                Navigator.pop(context);
              },
              child: const Text('应用'),
            ),
          ],
        );
      },
    );
  }
  
  /// 刷新图谱
  void _refreshGraph() {
    setState(() {
      _selectedNode = null;
      ref.refresh(_selectedNodeType != null
          ? nodesByTypeProvider(_selectedNodeType!)
          : allNodesProvider);
    });
  }
  
  /// 更新可用的节点类型
  void _updateAvailableNodeTypes(List<KnowledgeNode> nodes) {
    final types = nodes.map((node) => node.type).toSet().toList();
    types.sort();
    
    if (!listEquals(_availableNodeTypes, types)) {
      setState(() {
        _availableNodeTypes = types;
      });
    }
  }
} 