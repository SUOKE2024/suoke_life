import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/app_colors.dart';
import '../../routes/app_router.dart';
import '../../../ai_agents/models/ai_agent.dart';

@RoutePage()
class ExploreScreen extends ConsumerStatefulWidget {
  const ExploreScreen({super.key});

  @override
  ConsumerState<ExploreScreen> createState() => _ExploreScreenState();
}

class _ExploreScreenState extends ConsumerState<ExploreScreen> {
  // 搜索控制器
  final TextEditingController _searchController = TextEditingController();
  
  // 当前选中的类别
  String _selectedCategory = '全部';
  
  // 是否正在搜索
  bool _isSearching = false;
  
  // 探索内容类别列表
  final List<String> _categories = [
    '全部',
    '健康知识',
    '养生技巧',
    '游戏挑战',
    '打卡地点',
    '美食探店',
  ];
  
  // 探索内容列表
  final List<Map<String, dynamic>> _exploreItems = [
    {
      'id': 'e1',
      'title': '知识岛探秘',
      'description': '探索中医养生知识的海洋，收集稀有的知识宝藏',
      'category': '健康知识',
      'imageUrl': 'assets/images/knowledge_island.jpg',
      'color': AppColors.primaryColor,
      'author': '索克团队',
      'publishDate': '2023-10-05',
      'viewCount': 3458,
      'hasKnowledgeGraph': true,
    },
    {
      'id': 'e2',
      'title': '玉米迷宫',
      'description': '在迷宫中寻找健康食材，学习均衡饮食知识',
      'category': '游戏挑战',
      'imageUrl': 'assets/images/corn_maze.jpg',
      'color': AppColors.aiLaoke,
      'author': '老克',
      'publishDate': '2023-09-28',
      'viewCount': 2187,
      'hasKnowledgeGraph': false,
    },
    {
      'id': 'e3',
      'title': '咖啡时光',
      'description': '探索咖啡中的有益成分，以及适合不同体质的饮用方式',
      'category': '养生技巧',
      'imageUrl': 'assets/images/coffee_time.jpg',
      'color': AppColors.accentColor,
      'author': '小艾',
      'publishDate': '2023-09-20',
      'viewCount': 4562,
      'hasKnowledgeGraph': true,
    },
    {
      'id': 'e4',
      'title': '美食探店',
      'description': '寻找城市中的健康美食，了解食材的营养价值',
      'category': '美食探店',
      'imageUrl': 'assets/images/food_exploration.jpg',
      'color': AppColors.successColor,
      'author': '小克',
      'publishDate': '2023-09-15',
      'viewCount': 3876,
      'hasKnowledgeGraph': false,
    },
    {
      'id': 'e5',
      'title': '花之物语',
      'description': '探索花卉的药用价值，学习中医花草养生知识',
      'category': '健康知识',
      'imageUrl': 'assets/images/flower_story.jpg',
      'color': AppColors.aiXiaoai,
      'author': '索克团队',
      'publishDate': '2023-09-10',
      'viewCount': 2943,
      'hasKnowledgeGraph': true,
    },
    {
      'id': 'e6',
      'title': '菌食记',
      'description': '了解菌类食材的营养特性，以及对人体的益处',
      'category': '美食探店',
      'imageUrl': 'assets/images/mushroom_diary.jpg',
      'color': AppColors.warningColor,
      'author': '小艾',
      'publishDate': '2023-09-05',
      'viewCount': 2156,
      'hasKnowledgeGraph': false,
    },
    {
      'id': 'e7',
      'title': '寻宿雅居',
      'description': '探访适合养生的住宿环境，学习居住环境对健康的影响',
      'category': '打卡地点',
      'imageUrl': 'assets/images/stay_places.jpg',
      'color': AppColors.secondaryColor,
      'author': '老克',
      'publishDate': '2023-08-30',
      'viewCount': 1892,
      'hasKnowledgeGraph': false,
    },
    {
      'id': 'e8',
      'title': '网红打卡',
      'description': '探访适合拍照的健康生活场所，分享健康生活方式',
      'category': '打卡地点',
      'imageUrl': 'assets/images/check_in_places.jpg',
      'color': AppColors.aiXiaoke,
      'author': '小克',
      'publishDate': '2023-08-25',
      'viewCount': 4321,
      'hasKnowledgeGraph': false,
    },
    {
      'id': 'e9',
      'title': '老克寻宝游戏',
      'description': '跟随老克寻找传统中医宝藏，了解中医药材知识',
      'category': '游戏挑战',
      'imageUrl': 'assets/images/laoke_treasure.jpg',
      'color': AppColors.aiLaoke,
      'author': '老克',
      'publishDate': '2023-08-20',
      'viewCount': 3654,
      'hasKnowledgeGraph': true,
    },
    {
      'id': 'e10',
      'title': '四季养生法则',
      'description': '根据四季变化调整生活习惯，掌握中医养生精髓',
      'category': '养生技巧',
      'imageUrl': 'assets/images/seasonal_health.jpg',
      'color': AppColors.primaryColor,
      'author': '索克团队',
      'publishDate': '2023-08-15',
      'viewCount': 5782,
      'hasKnowledgeGraph': true,
    },
  ];
  
  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }
  
  // 获取过滤后的探索项目
  List<Map<String, dynamic>> get _filteredItems {
    if (_selectedCategory == '全部') {
      return _exploreItems;
    }
    
    return _exploreItems.where((item) => 
      item['category'] == _selectedCategory).toList();
  }
  
  // 搜索内容
  List<Map<String, dynamic>> _searchItems(String query) {
    if (query.isEmpty) {
      return [];
    }
    
    final lowerCaseQuery = query.toLowerCase();
    
    return _exploreItems.where((item) => 
      item['title'].toString().toLowerCase().contains(lowerCaseQuery) ||
      item['description'].toString().toLowerCase().contains(lowerCaseQuery) ||
      item['category'].toString().toLowerCase().contains(lowerCaseQuery)
    ).toList();
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: _isSearching
            ? TextField(
                controller: _searchController,
                decoration: const InputDecoration(
                  hintText: '搜索探索内容...',
                  border: InputBorder.none,
                ),
                onChanged: (value) {
                  setState(() {});
                },
                autofocus: true,
              )
            : const Text('探索'),
        actions: [
          IconButton(
            icon: Icon(_isSearching ? Icons.cancel : Icons.search),
            onPressed: () {
              setState(() {
                _isSearching = !_isSearching;
                if (!_isSearching) {
                  _searchController.clear();
                }
              });
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // 分类选择器
          if (!_isSearching) _buildCategorySelector(),
          
          // 内容列表
          Expanded(
            child: _isSearching
                ? _buildSearchResults()
                : _buildExploreGrid(),
          ),
        ],
      ),
      // AI代理气泡和加号按钮
      floatingActionButton: Column(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          // 加号按钮
          FloatingActionButton(
            heroTag: 'add_content',
            onPressed: () {
              // 显示内容生成页面
              _showAddContentDialog();
            },
            child: const Icon(Icons.add),
          ),
          
          const SizedBox(height: 16),
          
          // AI代理气泡
          FloatingActionButton(
            heroTag: 'ai_agent',
            backgroundColor: AppColors.aiLaoke.withOpacity(0.9),
            onPressed: () {
              // 进入与老克的多模态自然交互界面
              _showAIAgentDialog();
            },
            child: CircleAvatar(
              radius: 20,
              backgroundColor: Colors.transparent,
              backgroundImage: AssetImage(AIAgent.laoke.avatarUrl),
            ),
          ),
        ],
      ),
    );
  }
  
  // 构建分类选择器
  Widget _buildCategorySelector() {
    return Container(
      height: 50,
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: _categories.length,
        separatorBuilder: (context, index) => const SizedBox(width: 16),
        itemBuilder: (context, index) {
          final category = _categories[index];
          final isSelected = category == _selectedCategory;
          
          return GestureDetector(
            onTap: () {
              setState(() {
                _selectedCategory = category;
              });
            },
            child: Center(
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: isSelected
                      ? AppColors.primaryColor
                      : Colors.transparent,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: isSelected
                        ? AppColors.primaryColor
                        : Colors.grey.shade300,
                  ),
                ),
                child: Text(
                  category,
                  style: TextStyle(
                    color: isSelected ? Colors.white : null,
                    fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }
  
  // 构建搜索结果
  Widget _buildSearchResults() {
    final results = _searchItems(_searchController.text);
    
    if (_searchController.text.isEmpty) {
      return const Center(
        child: Text('请输入搜索关键词'),
      );
    }
    
    if (results.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.search_off,
              size: 60,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: 16),
            Text(
              '未找到相关内容',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey.shade600,
              ),
            ),
          ],
        ),
      );
    }
    
    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
        childAspectRatio: 0.75,
      ),
      itemCount: results.length,
      itemBuilder: (context, index) {
        return _buildExploreItemCard(results[index]);
      },
    );
  }
  
  // 构建探索网格
  Widget _buildExploreGrid() {
    if (_filteredItems.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.category_outlined,
              size: 60,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: 16),
            Text(
              '该分类下暂无内容',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey.shade600,
              ),
            ),
          ],
        ),
      );
    }
    
    // 使用瀑布流展示探索项目
    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
        childAspectRatio: 0.75,
      ),
      itemCount: _filteredItems.length,
      itemBuilder: (context, index) {
        return _buildExploreItemCard(_filteredItems[index]);
      },
    );
  }
  
  // 构建探索项目卡片
  Widget _buildExploreItemCard(Map<String, dynamic> item) {
    return Card(
      clipBehavior: Clip.antiAlias,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      elevation: 3,
      shadowColor: Colors.black.withOpacity(0.2),
      child: InkWell(
        onTap: () {
          // 点击后进入详情页面
          if (item['hasKnowledgeGraph'] as bool) {
            // 如果有知识图谱，导航到知识图谱页面
            context.router.push(const KnowledgeGraphRoute());
          } else {
            // 否则显示详情对话框
            _showItemDetailDialog(item);
          }
        },
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 图片
            AspectRatio(
              aspectRatio: 3 / 2,
              child: Stack(
                fit: StackFit.expand,
                children: [
                  // 使用占位符替代实际图片
                  Container(
                    color: (item['color'] as Color).withOpacity(0.2),
                    child: Center(
                      child: Icon(
                        Icons.image,
                        size: 40,
                        color: (item['color'] as Color).withOpacity(0.6),
                      ),
                    ),
                  ),
                  
                  // 分类标签
                  Positioned(
                    top: 8,
                    left: 8,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.7),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        item['category'] as String,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                  
                  // 知识图谱标识
                  if (item['hasKnowledgeGraph'] as bool)
                    Positioned(
                      top: 8,
                      right: 8,
                      child: Container(
                        padding: const EdgeInsets.all(4),
                        decoration: BoxDecoration(
                          color: AppColors.primaryColor,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.account_tree,
                          color: Colors.white,
                          size: 16,
                        ),
                      ),
                    ),
                ],
              ),
            ),
            
            // 内容部分
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 标题
                    Text(
                      item['title'] as String,
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    
                    const SizedBox(height: 4),
                    
                    // 描述
                    Expanded(
                      child: Text(
                        item['description'] as String,
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade600,
                        ),
                        maxLines: 3,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    
                    // 底部信息
                    Row(
                      children: [
                        // 作者
                        Text(
                          item['author'] as String,
                          style: TextStyle(
                            fontSize: 10,
                            color: Colors.grey.shade700,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        
                        const Spacer(),
                        
                        // 查看次数
                        Icon(
                          Icons.visibility,
                          size: 12,
                          color: Colors.grey.shade500,
                        ),
                        
                        const SizedBox(width: 2),
                        
                        Text(
                          _formatNumber(item['viewCount'] as int),
                          style: TextStyle(
                            fontSize: 10,
                            color: Colors.grey.shade500,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  // 格式化数字
  String _formatNumber(int number) {
    if (number >= 10000) {
      return '${(number / 10000).toStringAsFixed(1)}万';
    } else if (number >= 1000) {
      return '${(number / 1000).toStringAsFixed(1)}千';
    } else {
      return number.toString();
    }
  }
  
  // 显示内容详情对话框
  void _showItemDetailDialog(Map<String, dynamic> item) {
    showDialog(
      context: context,
      builder: (context) {
        return Dialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // 图片头部
              AspectRatio(
                aspectRatio: 16 / 9,
                child: Container(
                  decoration: BoxDecoration(
                    color: (item['color'] as Color).withOpacity(0.2),
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(16),
                      topRight: Radius.circular(16),
                    ),
                  ),
                  child: Center(
                    child: Icon(
                      Icons.image,
                      size: 60,
                      color: (item['color'] as Color).withOpacity(0.6),
                    ),
                  ),
                ),
              ),
              
              // 内容部分
              Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 标题和类别
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            item['title'] as String,
                            style: const TextStyle(
                              fontSize: 20,
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
                            color: (item['color'] as Color).withOpacity(0.1),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            item['category'] as String,
                            style: TextStyle(
                              fontSize: 12,
                              color: item['color'] as Color,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                    
                    const SizedBox(height: 8),
                    
                    // 作者和发布日期
                    Row(
                      children: [
                        Text(
                          item['author'] as String,
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey.shade700,
                          ),
                        ),
                        
                        const SizedBox(width: 8),
                        
                        Text(
                          item['publishDate'] as String,
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey.shade500,
                          ),
                        ),
                        
                        const Spacer(),
                        
                        // 查看次数
                        Icon(
                          Icons.visibility,
                          size: 16,
                          color: Colors.grey.shade500,
                        ),
                        
                        const SizedBox(width: 4),
                        
                        Text(
                          _formatNumber(item['viewCount'] as int),
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey.shade500,
                          ),
                        ),
                      ],
                    ),
                    
                    const SizedBox(height: 16),
                    
                    // 描述
                    Text(
                      item['description'] as String,
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.grey.shade800,
                        height: 1.5,
                      ),
                    ),
                    
                    const SizedBox(height: 16),
                    
                    // 功能不可用提示
                    Text(
                      '内容详情功能尚在开发中...',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey.shade600,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                    
                    const SizedBox(height: 24),
                    
                    // 操作按钮
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        OutlinedButton.icon(
                          icon: const Icon(Icons.share),
                          label: const Text('分享'),
                          onPressed: () {
                            Navigator.pop(context);
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('分享功能暂未实现'),
                              ),
                            );
                          },
                        ),
                        
                        ElevatedButton.icon(
                          icon: const Icon(Icons.play_arrow),
                          label: const Text('开始探索'),
                          onPressed: () {
                            Navigator.pop(context);
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('探索功能暂未实现'),
                              ),
                            );
                          },
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
  
  // 显示添加内容对话框
  void _showAddContentDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('创建探索内容'),
          content: const Text('此功能允许您创建自己的探索内容，分享给其他用户。目前该功能尚在开发中...'),
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
  
  // 显示AI代理对话框
  void _showAIAgentDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          contentPadding: EdgeInsets.zero,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // AI代理头部
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.aiLaoke.withOpacity(0.1),
                  borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(16),
                    topRight: Radius.circular(16),
                  ),
                ),
                child: Row(
                  children: [
                    // AI头像
                    CircleAvatar(
                      radius: 24,
                      backgroundImage: AssetImage(AIAgent.laoke.avatarUrl),
                    ),
                    
                    const SizedBox(width: 16),
                    
                    // AI名称和描述
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            AIAgent.laoke.name,
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          
                          Text(
                            AIAgent.laoke.description,
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey.shade700,
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              
              // 对话内容
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    // AI消息气泡
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.grey.shade100,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Text(
                        '你好！我是老克，我可以帮你探索健康生活的奥秘。你想了解什么呢？',
                        style: TextStyle(fontSize: 16),
                      ),
                    ),
                    
                    const SizedBox(height: 16),
                    
                    // 快捷回复按钮
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        _buildQuickReplyChip('健康生活的秘诀'),
                        _buildQuickReplyChip('推荐一些探索活动'),
                        _buildQuickReplyChip('今日养生建议'),
                      ],
                    ),
                  ],
                ),
              ),
              
              // 底部输入框
              Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        decoration: InputDecoration(
                          hintText: '输入消息...',
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(24),
                            borderSide: BorderSide.none,
                          ),
                          filled: true,
                          fillColor: Colors.grey.shade200,
                          contentPadding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 8,
                          ),
                        ),
                      ),
                    ),
                    
                    const SizedBox(width: 8),
                    
                    CircleAvatar(
                      radius: 20,
                      backgroundColor: AppColors.primaryColor,
                      child: const Icon(
                        Icons.send,
                        color: Colors.white,
                        size: 18,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
  
  // 构建快捷回复芯片
  Widget _buildQuickReplyChip(String text) {
    return InkWell(
      onTap: () {
        // 处理快捷回复
        Navigator.pop(context);
        
        // 导航到RAG演示页面
        context.router.push(const RAGDemoRoute());
      },
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: 12,
          vertical: 8,
        ),
        decoration: BoxDecoration(
          color: AppColors.primaryColor.withOpacity(0.1),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: AppColors.primaryColor.withOpacity(0.3),
          ),
        ),
        child: Text(
          text,
          style: TextStyle(
            fontSize: 14,
            color: AppColors.primaryColor,
          ),
        ),
      ),
    );
  }
} 