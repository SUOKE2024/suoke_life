import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../domain/entities/knowledge_node.dart';
import '../../../domain/entities/knowledge_relation.dart';
import '../../widgets/knowledge_graph/knowledge_graph_view.dart';
import '../../widgets/knowledge_graph/knowledge_graph_controls.dart';
import '../../widgets/knowledge_graph/node_detail_view.dart';
import '../../providers/knowledge_graph_providers.dart';

@RoutePage()
class KnowledgeGraphScreen extends ConsumerStatefulWidget {
  final String? initialTopic;
  final String? nodeId;

  const KnowledgeGraphScreen({
    Key? key,
    this.initialTopic,
    this.nodeId,
  }) : super(key: key);

  @override
  ConsumerState<KnowledgeGraphScreen> createState() => _KnowledgeGraphScreenState();
}

class _KnowledgeGraphScreenState extends ConsumerState<KnowledgeGraphScreen> {
  late final TextEditingController _searchController;
  late final ScrollController _scrollController;
  bool _showControls = true;
  bool _showDetail = false;

  @override
  void initState() {
    super.initState();
    _searchController = TextEditingController();
    _scrollController = ScrollController();

    // 如果提供了初始主题，则设置主题
    if (widget.initialTopic != null) {
      Future.microtask(() {
        ref.read(selectedTopicProvider.notifier).state = widget.initialTopic!;
      });
    }

    // 如果提供了节点ID，则加载并选中该节点
    if (widget.nodeId != null) {
      Future.microtask(() {
        _selectNodeById(widget.nodeId!);
      });
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  // 根据ID选择节点
  Future<void> _selectNodeById(String nodeId) async {
    final nodesAsync = await ref.read(knowledgeNodesProvider.future);
    final node = nodesAsync.firstWhere(
      (node) => node.id == nodeId,
      orElse: () => KnowledgeNode(
        id: '',
        name: '未找到节点',
        type: 'unknown',
        topic: '未知',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      ),
    );

    if (node.id.isNotEmpty) {
      ref.read(selectedNodeProvider.notifier).state = node;
      setState(() {
        _showDetail = true;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final graphController = ref.watch(knowledgeGraphControllerProvider);
    final selectedNode = ref.watch(selectedNodeProvider);
    final isMobile = MediaQuery.of(context).size.width < 600;

    return Scaffold(
      appBar: AppBar(
        title: const Text('知识图谱'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: Icon(_showControls ? Icons.settings : Icons.settings_outlined),
            onPressed: () {
              setState(() {
                _showControls = !_showControls;
              });
            },
            tooltip: '显示/隐藏控制面板',
          ),
          if (selectedNode != null)
            IconButton(
              icon: Icon(_showDetail ? Icons.info : Icons.info_outline),
              onPressed: () {
                setState(() {
                  _showDetail = !_showDetail;
                });
              },
              tooltip: '显示/隐藏节点详情',
            ),
        ],
      ),
      body: Column(
        children: [
          _buildSearchBar(),
          Expanded(
            child: Stack(
              children: [
                // 知识图谱视图
                const Positioned.fill(
                  child: KnowledgeGraphView(),
                ),
                
                // 加载指示器
                if (graphController.isRefreshing)
                  const Positioned.fill(
                    child: Center(
                      child: CircularProgressIndicator(),
                    ),
                  ),
                
                // 控制面板
                if (_showControls)
                  Positioned(
                    top: 16,
                    right: 16,
                    child: Card(
                      elevation: 4,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Container(
                        width: isMobile ? MediaQuery.of(context).size.width * 0.8 : 300,
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 12,
                        ),
                        child: const KnowledgeGraphControls(),
                      ),
                    ),
                  ),
                
                // 节点详情
                if (_showDetail && selectedNode != null)
                  Positioned(
                    bottom: 16,
                    left: 16,
                    right: 16,
                    child: SizedBox(
                      height: MediaQuery.of(context).size.height * 0.4,
                      child: Card(
                        elevation: 4,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        clipBehavior: Clip.antiAlias,
                        child: NodeDetailView(
                          node: selectedNode,
                          onClose: () {
                            setState(() {
                              _showDetail = false;
                            });
                          },
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        child: const Icon(Icons.refresh),
        onPressed: () {
          ref.read(knowledgeGraphControllerProvider.notifier).refreshGraph();
        },
        tooltip: '刷新图谱',
      ),
    );
  }

  // 搜索栏
  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: TextField(
        controller: _searchController,
        decoration: InputDecoration(
          hintText: '搜索节点...',
          prefixIcon: const Icon(Icons.search),
          suffixIcon: IconButton(
            icon: const Icon(Icons.clear),
            onPressed: () {
              _searchController.clear();
              // 清除搜索结果
            },
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide.none,
          ),
          filled: true,
          fillColor: Colors.grey.shade200,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 14,
          ),
        ),
        onSubmitted: (query) {
          if (query.isEmpty) return;
          
          // 实现搜索逻辑
          // TODO: 实现节点搜索功能
        },
      ),
    );
  }
} 