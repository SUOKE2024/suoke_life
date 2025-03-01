import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:logger/logger.dart';

import '../../../core/theme/app_colors.dart';
import '../../../ai_agents/rag/rag_provider.dart';
import '../../../ai_agents/models/rag_result.dart';
import '../../../domain/entities/knowledge_node.dart';
import '../../../core/router/app_router.gr.dart';

/// 知识图谱详情页面
/// 展示知识节点的详细信息、相关资源和问答功能
@RoutePage()
class KnowledgeDetailScreen extends ConsumerStatefulWidget {
  /// 知识节点ID
  final String nodeId;
  
  /// 知识节点类型
  final String nodeType;
  
  /// 知识节点描述
  final String nodeDescription;

  const KnowledgeDetailScreen({
    super.key,
    required this.nodeId,
    required this.nodeType,
    required this.nodeDescription,
  });

  @override
  ConsumerState<KnowledgeDetailScreen> createState() => _KnowledgeDetailScreenState();
}

class _KnowledgeDetailScreenState extends ConsumerState<KnowledgeDetailScreen> with TickerProviderStateMixin {
  final Logger _logger = Logger();
  
  // 问答相关状态
  bool _isLoadingAnswer = false;
  RAGResult? _currentResult;
  final TextEditingController _questionController = TextEditingController();
  
  // 常见问题列表
  late List<String> _commonQuestions;
  
  // Tab控制器
  late TabController _tabController;
  
  // 滚动控制器
  final ScrollController _scrollController = ScrollController();
  
  @override
  void initState() {
    super.initState();
    
    // 初始化常见问题
    _commonQuestions = [
      '什么是${widget.nodeId}？',
      '${widget.nodeId}有哪些主要特点？',
      '${widget.nodeId}的应用方法是什么？',
      '${widget.nodeId}与健康的关系？',
    ];
    
    // 初始化TabController
    _tabController = TabController(length: 3, vsync: this);
  }
  
  @override
  void dispose() {
    _questionController.dispose();
    _tabController.dispose();
    _scrollController.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.nodeId),
        actions: [
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: () {
              // 分享功能
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('分享功能即将推出')),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.bookmark_border),
            onPressed: () {
              // 收藏功能
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('已添加到收藏')),
              );
            },
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: '概述'),
            Tab(text: '相关资源'),
            Tab(text: '智能问答'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          // 概述标签页
          _buildOverviewTab(),
          
          // 相关资源标签页
          _buildRelatedResourcesTab(),
          
          // 智能问答标签页
          _buildQATab(),
        ],
      ),
    );
  }
  
  // 构建概述标签页
  Widget _buildOverviewTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 知识节点基本信息
          _buildNodeInfoCard(),
          
          const SizedBox(height: 24),
          
          // 知识内容
          _buildKnowledgeContent(),
          
          const SizedBox(height: 24),
          
          // 相关知识节点
          _buildRelatedNodes(),
        ],
      ),
    );
  }
  
  // 构建节点信息卡片
  Widget _buildNodeInfoCard() {
    final Color typeColor = _getColorForType(widget.nodeType);
    
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 24,
                  backgroundColor: typeColor.withOpacity(0.2),
                  child: Icon(
                    _getIconForType(widget.nodeType),
                    color: typeColor,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.nodeId,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: typeColor.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: typeColor.withOpacity(0.3),
                          ),
                        ),
                        child: Text(
                          widget.nodeType,
                          style: TextStyle(
                            fontSize: 12,
                            color: typeColor,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              widget.nodeDescription,
              style: TextStyle(
                fontSize: 14,
                height: 1.5,
                color: Colors.grey[800],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  // 构建知识内容
  Widget _buildKnowledgeContent() {
    // 这里应该根据节点类型获取不同的内容
    final String content = _getNodeContent();
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '详细内容',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        Card(
          elevation: 1,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: MarkdownBody(
              data: content,
              styleSheet: MarkdownStyleSheet(
                p: const TextStyle(height: 1.5),
                h1: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                h2: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                h3: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ),
          ),
        ),
      ],
    );
  }
  
  // 构建相关节点
  Widget _buildRelatedNodes() {
    // 模拟相关节点数据
    final relatedNodes = _getRelatedNodes();
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '相关知识',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: relatedNodes.length,
          separatorBuilder: (context, index) => const Divider(),
          itemBuilder: (context, index) {
            final node = relatedNodes[index];
            final Color typeColor = _getColorForType(node['type'] as String);
            
            return ListTile(
              leading: CircleAvatar(
                backgroundColor: typeColor.withOpacity(0.2),
                child: Icon(
                  _getIconForType(node['type'] as String),
                  color: typeColor,
                  size: 20,
                ),
              ),
              title: Text(node['id'] as String),
              subtitle: Text(
                node['description'] as String,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              onTap: () {
                // 导航到相关节点详情页面
                context.router.push(
                  KnowledgeDetailRoute(
                    nodeId: node['id'] as String,
                    nodeType: node['type'] as String,
                    nodeDescription: node['description'] as String,
                  ),
                );
              },
            );
          },
        ),
      ],
    );
  }
  
  // 构建相关资源标签页
  Widget _buildRelatedResourcesTab() {
    // 模拟相关资源数据
    final resources = _getRelatedResources();
    
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: resources.length,
      itemBuilder: (context, index) {
        final resource = resources[index];
        
        return Card(
          margin: const EdgeInsets.only(bottom: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 资源图标
                    Container(
                      width: 60,
                      height: 60,
                      decoration: BoxDecoration(
                        color: Colors.grey[200],
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Icon(
                        _getIconForResourceType(resource['type'] as String),
                        color: AppColors.primaryColor,
                        size: 30,
                      ),
                    ),
                    const SizedBox(width: 16),
                    
                    // 资源信息
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            resource['title'] as String,
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            resource['source'] as String,
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey[600],
                            ),
                          ),
                          const SizedBox(height: 8),
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 8,
                                  vertical: 2,
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.blue.withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text(
                                  resource['type'] as String,
                                  style: const TextStyle(
                                    fontSize: 10,
                                    color: Colors.blue,
                                  ),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Icon(
                                Icons.access_time,
                                size: 12,
                                color: Colors.grey[600],
                              ),
                              const SizedBox(width: 4),
                              Text(
                                resource['date'] as String,
                                style: TextStyle(
                                  fontSize: 10,
                                  color: Colors.grey[600],
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  resource['description'] as String,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[800],
                  ),
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    OutlinedButton(
                      onPressed: () {
                        // 查看资源详情
                      },
                      style: OutlinedButton.styleFrom(
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(20),
                        ),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                      ),
                      child: const Text('查看'),
                    ),
                    const SizedBox(width: 8),
                    ElevatedButton(
                      onPressed: () {
                        // 下载或打开资源
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.primaryColor,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(20),
                        ),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                      ),
                      child: const Text('打开'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }
  
  // 构建智能问答标签页
  Widget _buildQATab() {
    return Column(
      children: [
        // 常见问题
        Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '常见问题',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: _commonQuestions.map((question) {
                  return InkWell(
                    onTap: () {
                      _askQuestion(question);
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 8,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.grey[100],
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: Colors.grey[300]!,
                        ),
                      ),
                      child: Text(
                        question,
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[800],
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
            ],
          ),
        ),
        
        // 问答区域
        Expanded(
          child: Container(
            padding: const EdgeInsets.all(16),
            color: Colors.grey[100],
            child: Column(
              children: [
                // 答案显示区域
                Expanded(
                  child: _isLoadingAnswer
                      ? const Center(child: CircularProgressIndicator())
                      : _currentResult == null
                          ? _buildEmptyState()
                          : _buildAnswerCard(),
                ),
                
                // 提问输入框
                Container(
                  margin: const EdgeInsets.only(top: 16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(24),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.05),
                        blurRadius: 10,
                        spreadRadius: 1,
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          child: TextField(
                            controller: _questionController,
                            decoration: const InputDecoration(
                              hintText: '输入您的问题...',
                              border: InputBorder.none,
                            ),
                            maxLines: 1,
                            textInputAction: TextInputAction.send,
                            onSubmitted: (value) {
                              if (value.isNotEmpty) {
                                _askQuestion(value);
                              }
                            },
                          ),
                        ),
                      ),
                      InkWell(
                        onTap: () {
                          final question = _questionController.text.trim();
                          if (question.isNotEmpty) {
                            _askQuestion(question);
                          }
                        },
                        child: Container(
                          margin: const EdgeInsets.all(6),
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: AppColors.primaryColor,
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(
                            Icons.send,
                            color: Colors.white,
                            size: 20,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
  
  // 构建空状态
  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.question_answer_outlined,
            size: 48,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            '提问关于"${widget.nodeId}"的问题',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '例如："${_commonQuestions.first}"',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }
  
  // 构建答案卡片
  Widget _buildAnswerCard() {
    if (_currentResult == null) return const SizedBox();
    
    return Card(
      elevation: 2,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: SingleChildScrollView(
          controller: _scrollController,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 问题
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(
                      Icons.person,
                      size: 16,
                      color: Colors.grey[600],
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _currentResult!.query,
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[800],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 16),
              
              // 答案
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  CircleAvatar(
                    radius: 12,
                    backgroundColor: AppColors.primaryColor.withOpacity(0.2),
                    child: Icon(
                      Icons.assistant,
                      size: 16,
                      color: AppColors.primaryColor,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _currentResult!.answer,
                      style: const TextStyle(
                        fontSize: 14,
                        height: 1.5,
                      ),
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 16),
              
              // 来源信息
              if (_currentResult!.sources.isNotEmpty) ...[
                const Divider(),
                const SizedBox(height: 8),
                const Text(
                  '参考来源',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey,
                  ),
                ),
                const SizedBox(height: 8),
                ...List.generate(
                  _currentResult!.sources.length,
                  (index) {
                    final source = _currentResult!.sources[index];
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Row(
                        children: [
                          Icon(
                            Icons.link,
                            size: 12,
                            color: Colors.blue[400],
                          ),
                          const SizedBox(width: 4),
                          Expanded(
                            child: Text(
                              source['title'] as String,
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.blue[400],
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          const SizedBox(width: 4),
                          Text(
                            '相关度: ${(source['relevance'] as double).toStringAsFixed(2)}',
                            style: TextStyle(
                              fontSize: 10,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
  
  // 提问问题
  Future<void> _askQuestion(String question) async {
    // 清空输入框
    _questionController.clear();
    
    setState(() {
      _isLoadingAnswer = true;
    });
    
    try {
      // 获取RAG答案
      final ragProvider = ref.read(ragProviderProvider);
      final result = await ragProvider.getAnswerWithSources(
        question,
        context: widget.nodeId,
      );
      
      setState(() {
        _currentResult = result;
        _isLoadingAnswer = false;
      });
      
      // 滚动到顶部
      _scrollController.animateTo(
        0.0,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    } catch (e) {
      _logger.e('获取答案失败: $e');
      setState(() {
        _currentResult = RAGResult(
          query: question,
          answer: '抱歉，无法回答这个问题。请稍后再试。',
          sources: [],
          timestamp: DateTime.now(),
        );
        _isLoadingAnswer = false;
      });
    }
  }
  
  // 根据节点类型获取颜色
  Color _getColorForType(String type) {
    switch (type) {
      case '理论':
        return Colors.blue;
      case '方法':
        return Colors.green;
      case '食疗':
        return Colors.orange;
      case '穴位':
        return Colors.purple;
      case '药物':
        return Colors.red;
      case '病症':
        return Colors.brown;
      default:
        return AppColors.primaryColor;
    }
  }
  
  // 根据节点类型获取图标
  IconData _getIconForType(String type) {
    switch (type) {
      case '理论':
        return Icons.book;
      case '方法':
        return Icons.spatial_tracking;
      case '食疗':
        return Icons.restaurant;
      case '穴位':
        return Icons.touch_app;
      case '药物':
        return Icons.medication;
      case '病症':
        return Icons.healing;
      default:
        return Icons.category;
    }
  }
  
  // 根据资源类型获取图标
  IconData _getIconForResourceType(String type) {
    switch (type) {
      case '文章':
        return Icons.article;
      case '视频':
        return Icons.video_library;
      case '图书':
        return Icons.book;
      case '研究':
        return Icons.science;
      default:
        return Icons.description;
    }
  }
  
  // 获取节点内容
  String _getNodeContent() {
    // 根据节点类型和ID返回不同内容
    if (widget.nodeId == '中医养生') {
      return '''
# 中医养生概述

中医养生是中医学的重要组成部分，是研究如何调养生命、增强体质、预防疾病、延年益寿的一门学问。它基于中医理论，包括阴阳五行、脏腑经络等学说，通过饮食调养、起居调摄、情志调节、运动养生等方式，达到平衡阴阳、调和气血、防病保健的目的。

## 基本理论

中医养生理论以中医学的基本理论为指导，主要包括以下几个方面：

1. **阴阳平衡理论**：认为人体是阴阳统一的整体，养生要注重阴阳平衡。
2. **五脏相关理论**：五脏（肝、心、脾、肺、肾）与五行相对应，养生要注重五脏功能的协调。
3. **气血津液理论**：气血津液是维持人体生命活动的基本物质，养生要注重调养气血津液。
4. **天人相应理论**：人与自然环境密切相关，养生要顺应自然规律。

## 养生方法

中医养生方法多种多样，主要包括：

- **饮食养生**：根据四季变化和个人体质调整饮食，如春吃酸、夏吃苦、秋吃辛、冬吃咸。
- **起居养生**：作息规律，早睡早起，顺应自然规律。
- **运动养生**：适当运动，如太极拳、八段锦、五禽戏等。
- **情志养生**：保持心情舒畅，避免七情过极。
- **穴位保健**：通过按摩、刮痧、艾灸等方式刺激穴位，调节气血。
- **四季养生**：根据不同季节特点，采取相应的养生措施。

## 现代意义

在现代社会，中医养生对预防疾病、维护健康具有重要意义：

1. 强调整体观念，注重身心平衡，符合现代医学健康观。
2. 注重预防为主，有利于慢性病的防控。
3. 方法简便易行，易于大众接受和实践。
4. 重视个体差异，强调因人制宜。
5. 符合可持续健康管理理念，有助于提高生活质量。
''';
    } else if (widget.nodeId == '经络学说') {
      return '''
# 经络学说概述

经络学说是中医理论的重要组成部分，是研究人体经络系统的理论。经络是指人体内气血运行的通道，包括十二正经、奇经八脉、十五络脉等。经络系统连接脏腑、沟通表里、贯穿上下，是气血运行的路径，也是病邪传导的途径。

## 经络系统组成

经络系统主要包括以下几个部分：

1. **十二正经**：包括手三阴经、手三阳经、足三阴经、足三阳经，分别联系相应的脏腑。
2. **奇经八脉**：包括任脉、督脉、冲脉、带脉、阴维脉、阳维脉、阴跷脉、阳跷脉，是正经气血的调节器。
3. **十五络脉**：是正经的分支，联系表里经脉。
4. **十二经别**：是正经的分支，加强脏腑之间的联系。
5. **十二经筋**：是正经的分支，主要分布于肌肉筋膜。
6. **皮部**：是经气输注于体表的部位。

## 经络功能

经络系统的主要功能包括：

- **运行气血**：经络是气血运行的通道，维持正常生理功能。
- **联系脏腑**：经络将五脏六腑联系为一个整体。
- **传导邪气**：疾病可通过经络传导扩散。
- **反应疾病**：脏腑疾病可通过经络反映到体表相应部位。
- **调节阴阳**：通过经络调节人体阴阳平衡。

## 临床应用

经络学说在临床中有广泛应用：

1. **针灸治疗**：通过刺激特定穴位调节经络气血，治疗疾病。
2. **推拿按摩**：沿经络走向推拿按摩，疏通气血。
3. **灸法**：通过艾灸温通经络，调节气血。
4. **拔罐**：通过拔罐促进经络气血运行。
5. **刮痧**：通过刮痧疏通经络，排出邪气。
6. **药物治疗**：根据经络归经理论选择药物。

## 现代研究

现代科学对经络的研究取得了一定进展：

1. 发现经络循行路线上存在特殊的生物物理和生物化学特性。
2. 低电阻特性：经络路线上的电阻较周围组织低。
3. 声、光、电、磁等物理特性的特异性。
4. 同位素迁移速度快于血液循环和淋巴循环。

尽管经络的物质基础尚未完全阐明，但其临床效应已得到广泛验证。
''';
    } else if (widget.nodeId == '穴位按摩') {
      return '''
# 穴位按摩概述

穴位按摩是一种传统中医疗法，通过按压、揉捏、推拿人体特定穴位，调节经络气血，达到防病治病、保健养生的目的。穴位是经络循行路线上的特殊点，具有感应和传导作用。通过刺激这些穴位，可以疏通经络、调节脏腑功能、增强机体免疫力。

## 基本原理

穴位按摩的基本原理基于经络学说，主要包括：

1. **经络循行理论**：穴位是经络循行路线上的特殊点，通过刺激穴位可以影响相应经络。
2. **脏腑相关理论**：不同经络联系不同脏腑，通过刺激相应经络上的穴位可以调节脏腑功能。
3. **气血运行理论**：穴位按摩可以促进气血运行，疏通经络。
4. **反射区理论**：特定穴位与特定器官或功能区域存在反射关系。

## 常用手法

穴位按摩的常用手法包括：

- **按法**：用拇指、食指或中指指腹垂直下按穴位，力度适中，有酸、麻、胀、痛感为宜。
- **揉法**：用指腹在穴位上做圆周运动，顺时针或逆时针揉动。
- **推法**：沿经络方向推动，力度均匀。
- **拿法**：用拇指和食指捏拿肌肉。
- **掐法**：用拇指和食指指甲掐按穴位。
- **点法**：用指尖点按穴位。

## 常用穴位

常用保健穴位包括：

1. **足三里**：小腿外侧，膝盖下三寸，胫骨外侧一横指处，强健脾胃。
2. **合谷**：手背第一、二掌骨间，偏向第二掌骨，解表止痛。
3. **关元**：脐下三寸，补肾助阳。
4. **太溪**：内踝后方，足内侧韧带与跟腱之间的凹陷处，滋补肾阴。
5. **百会**：头顶正中线与两耳尖连线的交点，提神醒脑。
6. **内关**：腕横纹上二寸，前臂掌侧正中，缓解心悸、胸闷。

## 适应范围

穴位按摩适用于多种常见疾病和亚健康状态：

- **疲劳恢复**：通过刺激足三里、合谷等穴位，缓解疲劳。
- **失眠改善**：通过按摩神门、安眠、百会等穴位，改善睡眠。
- **消化不良**：通过按摩足三里、中脘等穴位，促进消化。
- **头痛缓解**：通过按摩太阳、风池等穴位，缓解头痛。
- **情绪调节**：通过按摩内关、神门等穴位，调节情绪。
- **免疫增强**：通过按摩足三里、合谷等穴位，增强免疫力。

## 注意事项

穴位按摩需注意以下几点：

1. 力度适中，以产生酸、麻、胀、痛感为宜，但不应过度疼痛。
2. 每个穴位按摩1-3分钟为宜。
3. 空腹、饱食、醉酒状态下不宜按摩。
4. 孕妇、重病患者应谨慎按摩特定穴位。
5. 皮肤破损、感染部位不宜按摩。
6. 严重心脏病、肿瘤患者按摩前应咨询医生。
''';
    } else {
      return '''
# ${widget.nodeId}

${widget.nodeDescription}

更多详细内容正在整理中，您可以通过"智能问答"标签页了解更多相关信息。
''';
    }
  }
  
  // 获取相关节点
  List<Map<String, dynamic>> _getRelatedNodes() {
    // 模拟相关节点数据
    switch (widget.nodeId) {
      case '中医养生':
        return [
          {
            'id': '四季养生',
            'type': '方法',
            'description': '四季养生是根据春、夏、秋、冬四季气候特点和人体生理变化，采取相应养生方法的养生理论。',
          },
          {
            'id': '经络学说',
            'type': '理论',
            'description': '经络学说是中医理论的重要组成部分，认为人体有十二正经、奇经八脉等经络系统，是气血运行的通道。',
          },
          {
            'id': '中医食疗',
            'type': '食疗',
            'description': '中医食疗是运用中医理论指导饮食，通过食物的性味、功效达到养生保健、防治疾病目的的方法。',
          },
        ];
      case '经络学说':
        return [
          {
            'id': '十二经脉',
            'type': '理论',
            'description': '十二经脉是指人体十二条主要经脉，包括手三阴经、手三阳经、足三阴经、足三阳经。',
          },
          {
            'id': '穴位按摩',
            'type': '穴位',
            'description': '穴位按摩是通过按压、揉捏人体特定穴位，调节经络气血，达到防病治病目的的方法。',
          },
          {
            'id': '奇经八脉',
            'type': '理论',
            'description': '奇经八脉是指任脉、督脉、冲脉、带脉、阴维脉、阳维脉、阴跷脉、阳跷脉八条经脉，是十二经脉的补充。',
          },
        ];
      case '穴位按摩':
        return [
          {
            'id': '足三里',
            'type': '穴位',
            'description': '足三里位于小腿外侧，膝盖下3寸（约四横指），是强壮穴，常用于调理脾胃。',
          },
          {
            'id': '经络导引',
            'type': '方法',
            'description': '经络导引是通过特定的体位、动作、呼吸方法，引导经络中的气血运行，达到养生保健目的的方法。',
          },
          {
            'id': '按摩手法',
            'type': '方法',
            'description': '按摩手法是指在穴位按摩中使用的多种手法，如按法、揉法、推法、拿法、掐法、点法等。',
          },
        ];
      default:
        return [
          {
            'id': '中医养生',
            'type': '理论',
            'description': '中医养生是中医学的重要组成部分，是研究如何调养生命、增强体质、预防疾病、延年益寿的一门学问。',
          },
          {
            'id': '经络学说',
            'type': '理论',
            'description': '经络学说是中医理论的重要组成部分，认为人体有十二正经、奇经八脉等经络系统，是气血运行的通道。',
          },
        ];
    }
  }
  
  // 获取相关资源
  List<Map<String, dynamic>> _getRelatedResources() {
    // 模拟相关资源数据
    switch (widget.nodeId) {
      case '中医养生':
        return [
          {
            'title': '《黄帝内经》养生精华',
            'source': '中医经典研究院',
            'type': '文章',
            'date': '2023-05-15',
            'description': '本文整理了《黄帝内经》中关于养生的核心理念和方法，包括四时养生、饮食调养、起居调摄等内容，对现代人的健康生活有重要参考价值。',
          },
          {
            'title': '中医养生方法详解',
            'source': '中国中医科学院',
            'type': '视频',
            'date': '2023-08-22',
            'description': '本视频由中国中医科学院专家讲解中医养生的基本理论和实用方法，包括四季养生、养生功法、食疗方案等，适合各年龄段人群学习和实践。',
          },
          {
            'title': '现代人如何实践中医养生',
            'source': '健康中国研究所',
            'type': '研究',
            'date': '2023-02-10',
            'description': '本研究针对现代生活方式，提出了适合当代人实践的中医养生方案，经过3000人群的实证研究，证明对改善亚健康状态有显著效果。',
          },
        ];
      case '经络学说':
        return [
          {
            'title': '经络与现代医学的整合研究',
            'source': '中西医结合研究院',
            'type': '研究',
            'date': '2023-07-05',
            'description': '本研究通过现代医学技术探测经络系统的物质基础，发现了经络循行路线上的生物电、热成像等特异性表现，为经络学说提供了科学证据。',
          },
          {
            'title': '十二经脉详解',
            'source': '中国针灸学会',
            'type': '文章',
            'date': '2023-04-18',
            'description': '本文详细介绍了十二经脉的循行路线、主治功能、重要穴位等内容，配有高清经络图谱，是中医学习者的重要参考资料。',
          },
          {
            'title': '经络学说在临床中的应用',
            'source': '北京中医药大学',
            'type': '视频',
            'date': '2023-09-12',
            'description': '本视频讲解了经络学说在针灸、推拿、拔罐等临床治疗中的具体应用，包含多个真实病例分析，展示了经络理论的临床价值。',
          },
        ];
      case '穴位按摩':
        return [
          {
            'title': '常用保健穴位按摩图解',
            'source': '中国保健协会',
            'type': '文章',
            'date': '2023-06-08',
            'description': '本文详细介绍了36个常用保健穴位的位置、功效和按摩方法，配有清晰的定位图和操作示范，适合自我保健使用。',
          },
          {
            'title': '穴位按摩手法详解',
            'source': '传统医学出版社',
            'type': '图书',
            'date': '2023-01-25',
            'description': '本书系统介绍了穴位按摩的基本理论、常用手法和适应症，包括按、揉、推、拿等手法的具体操作要领，是穴位按摩学习的权威教材。',
          },
          {
            'title': '居家穴位按摩保健指南',
            'source': '健康生活频道',
            'type': '视频',
            'date': '2023-10-05',
            'description': '本视频系列教授实用的居家穴位按摩方法，针对常见亚健康问题如失眠、颈肩疲劳、消化不良等，提供针对性的穴位按摩方案。',
          },
        ];
      default:
        return [
          {
            'title': '中医养生概论',
            'source': '中医药出版社',
            'type': '图书',
            'date': '2023-03-20',
            'description': '本书全面介绍了中医养生的基本理论和实践方法，是中医养生入门的权威教材，适合医学专业学生和养生爱好者阅读。',
          },
          {
            'title': '四季养生法',
            'source': '健康生活杂志',
            'type': '文章',
            'date': '2023-06-15',
            'description': '本文详细介绍了春、夏、秋、冬四季的养生要点，包括饮食调整、起居变化、运动建议等，帮助读者根据季节变化调整生活方式。',
          },
        ];
    }
  }
}
