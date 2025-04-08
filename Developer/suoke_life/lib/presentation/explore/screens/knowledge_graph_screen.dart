import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/data/models/knowledge_model.dart';
import 'package:suoke_life/domain/usecases/knowledge/get_nodes_usecase.dart';
import 'package:suoke_life/domain/usecases/knowledge/search_nodes_usecase.dart';
import 'package:suoke_life/di/providers.dart';

/// 知识图谱屏幕
class KnowledgeGraphScreen extends ConsumerStatefulWidget {
  /// 构造函数
  const KnowledgeGraphScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<KnowledgeGraphScreen> createState() => _KnowledgeGraphScreenState();
}

class _KnowledgeGraphScreenState extends ConsumerState<KnowledgeGraphScreen> {
  final TextEditingController _searchController = TextEditingController();
  List<KnowledgeNodeModel>? _nodes;
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadNodes();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadNodes() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final getNodesUseCase = ref.read(getNodesUseCaseProvider);
    final result = await getNodesUseCase(const NodesParams());

    result.fold(
      (failure) {
        setState(() {
          _errorMessage = failure.message;
          _isLoading = false;
        });
      },
      (nodes) {
        setState(() {
          _nodes = nodes;
          _isLoading = false;
        });
      },
    );
  }

  Future<void> _searchNodes(String query) async {
    if (query.isEmpty) {
      _loadNodes();
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final searchNodesUseCase = ref.read(searchNodesUseCaseProvider);
    final result = await searchNodesUseCase(SearchParams(query: query));

    result.fold(
      (failure) {
        setState(() {
          _errorMessage = failure.message;
          _isLoading = false;
        });
      },
      (nodes) {
        setState(() {
          _nodes = nodes;
          _isLoading = false;
        });
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('知识图谱'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadNodes,
          ),
        ],
      ),
      body: Column(
        children: [
          // 搜索框
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: '搜索知识节点...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: IconButton(
                  icon: const Icon(Icons.clear),
                  onPressed: () {
                    _searchController.clear();
                    _loadNodes();
                  },
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                ),
              ),
              onSubmitted: _searchNodes,
            ),
          ),
          // 节点列表
          Expanded(
            child: _errorMessage != null
                ? _buildErrorWidget()
                : _isLoading
                    ? _buildLoadingWidget()
                    : _buildNodesList(),
          ),
        ],
      ),
    );
  }

  Widget _buildNodesList() {
    final nodes = _nodes;
    
    if (nodes == null || nodes.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.info_outline, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text(
              '没有知识节点',
              style: TextStyle(fontSize: 18, color: Colors.grey),
            ),
          ],
        ),
      );
    }
    
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: nodes.length,
      itemBuilder: (context, index) {
        final node = nodes[index];
        return _buildNodeItem(node);
      },
    );
  }

  Widget _buildNodeItem(KnowledgeNodeModel node) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    node.title,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: AppColors.primaryColor.withAlpha(50),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    node.nodeType,
                    style: TextStyle(
                      fontSize: 12,
                      color: AppColors.primaryColor,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              node.content,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: node.tags.map((tag) {
                return Chip(
                  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  label: Text(tag),
                  backgroundColor: Colors.grey.shade200,
                  labelStyle: const TextStyle(fontSize: 12),
                  padding: EdgeInsets.zero,
                );
              }).toList(),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: () {
                    _showNodeDetailsDialog(node);
                  },
                  child: const Text('查看详情'),
                ),
                if (node.relations != null && node.relations!.isNotEmpty)
                  TextButton(
                    onPressed: () {
                      _showRelationsDialog(node);
                    },
                    child: const Text('查看关系'),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _showNodeDetailsDialog(KnowledgeNodeModel node) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(node.title),
          content: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: AppColors.primaryColor.withAlpha(50),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    node.nodeType,
                    style: TextStyle(
                      fontSize: 12,
                      color: AppColors.primaryColor,
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                const Text(
                  '内容:',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(node.content),
                const SizedBox(height: 16),
                const Text(
                  '标签:',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: node.tags.map((tag) {
                    return Chip(
                      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      label: Text(tag),
                      backgroundColor: Colors.grey.shade200,
                      labelStyle: const TextStyle(fontSize: 12),
                      padding: EdgeInsets.zero,
                    );
                  }).toList(),
                ),
                if (node.metadata != null) ...[
                  const SizedBox(height: 16),
                  const Text(
                    '元数据:',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(node.metadata.toString()),
                ],
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context);
              },
              child: const Text('关闭'),
            ),
          ],
        );
      },
    );
  }

  void _showRelationsDialog(KnowledgeNodeModel node) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('节点关系'),
          content: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('${node.title} 的关系:'),
                const SizedBox(height: 16),
                if (node.relations != null && node.relations!.isNotEmpty)
                  ...node.relations!.map((relation) {
                    return Card(
                      margin: const EdgeInsets.only(bottom: 8),
                      child: Padding(
                        padding: const EdgeInsets.all(8),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '关系类型: ${relation.relationType}',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Text('目标节点: ${relation.targetId}'),
                          ],
                        ),
                      ),
                    );
                  }).toList()
                else
                  const Text('没有关系数据'),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context);
              },
              child: const Text('关闭'),
            ),
          ],
        );
      },
    );
  }

  Widget _buildLoadingWidget() {
    return const Center(
      child: CircularProgressIndicator(),
    );
  }

  Widget _buildErrorWidget() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.error_outline,
            color: Colors.red,
            size: 48,
          ),
          const SizedBox(height: 16),
          Text(
            _errorMessage ?? '未知错误',
            style: const TextStyle(
              color: Colors.red,
              fontSize: 16,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: _loadNodes,
            child: const Text('重试'),
          ),
        ],
      ),
    );
  }
} 