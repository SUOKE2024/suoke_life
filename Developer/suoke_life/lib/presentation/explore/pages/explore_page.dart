import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_staggered_grid_view/flutter_staggered_grid_view.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/core/router/app_router.dart';
import 'package:suoke_life/presentation/explore/providers/explore_providers.dart';
import 'package:suoke_life/presentation/explore/widgets/exploration_card.dart';
import 'package:suoke_life/presentation/explore/widgets/ai_agent_avatar.dart';
import 'package:suoke_life/presentation/explore/pages/exploration_detail_page.dart';
import 'package:suoke_life/core/widgets/app_widgets.dart' as app_widgets;
import 'dart:ui';
import 'package:suoke_life/presentation/common/widgets/custom_app_bar.dart';
import 'package:suoke_life/presentation/explore/widgets/knowledge_list.dart';
import 'package:suoke_life/presentation/explore/widgets/training_course_list.dart';
import 'package:suoke_life/presentation/explore/widgets/blog_post_list.dart';

/// 探索页面（探索频道）
@RoutePage()
class ExplorePage extends ConsumerStatefulWidget {
  const ExplorePage({Key? key}) : super(key: key);

  @override
  ConsumerState<ExplorePage> createState() => _ExplorePageState();
}

class _ExplorePageState extends ConsumerState<ExplorePage> with SingleTickerProviderStateMixin {
  final TextEditingController _searchController = TextEditingController();
  late TabController _tabController;
  String? _selectedKnowledgeCategoryId;
  String? _selectedTrainingCategoryId;
  String? _selectedBlogCategoryId;
  String? _selectedTrainingLevel;
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    
    // 添加Tab切换监听器
    _tabController.addListener(() {
      setState(() {
        // 在这里可以处理Tab切换事件
      });
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CustomAppBar(
        title: const Text('探索'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: '知识专区'),
            Tab(text: '培训课程'),
            Tab(text: '老克博客'),
          ],
          labelColor: Theme.of(context).primaryColor,
          unselectedLabelColor: Colors.grey,
          indicatorColor: Theme.of(context).primaryColor,
        ),
      ),
      body: Column(
        children: [
          // 搜索区域
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '中医知识检索',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 4),
                Text(
                  '提问任何关于中医健康养生的问题，获取专业知识解答',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.grey[700],
                      ),
                ),
                const SizedBox(height: 16),
                // 搜索框
                TextField(
                  controller: _searchController,
                  decoration: InputDecoration(
                    hintText: '例如: 阴虚体质的调理方法',
                    prefixIcon: const Icon(Icons.search),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    suffixIcon: IconButton(
                      icon: const Icon(Icons.clear),
                      onPressed: () {
                        _searchController.clear();
                      },
                    ),
                  ),
                  textInputAction: TextInputAction.search,
                  onSubmitted: (query) {
                    if (query.trim().isNotEmpty) {
                      _navigateToRagSearch(query);
                    }
                  },
                ),
              ],
            ),
          ),
          
          // 分类选择器 (根据当前Tab显示不同的选择器)
          _buildCategorySelector(),
          
          // 标签页内容
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                // 知识专区
                KnowledgeList(categoryId: _selectedKnowledgeCategoryId),
                
                // 培训课程
                TrainingCourseList(
                  categoryId: _selectedTrainingCategoryId,
                  level: _selectedTrainingLevel,
                ),
                
                // 老克博客
                BlogPostList(
                  categoryId: _selectedBlogCategoryId,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildCategorySelector() {
    // 根据当前选中的Tab返回对应的分类选择器
    switch (_tabController.index) {
      case 0:
        return KnowledgeCategorySelector(
          selectedCategoryId: _selectedKnowledgeCategoryId,
          onCategorySelected: (categoryId) {
            setState(() {
              _selectedKnowledgeCategoryId = categoryId;
            });
          },
        );
      case 1:
        return Column(
          children: [
            // 课程分类选择器
            KnowledgeCategorySelector(
              selectedCategoryId: _selectedTrainingCategoryId,
              onCategorySelected: (categoryId) {
                setState(() {
                  _selectedTrainingCategoryId = categoryId;
                });
              },
            ),
            // 课程难度选择器
            TrainingLevelSelector(
              selectedLevel: _selectedTrainingLevel,
              onLevelSelected: (level) {
                setState(() {
                  _selectedTrainingLevel = level;
                });
              },
            ),
          ],
        );
      case 2:
        return KnowledgeCategorySelector(
          selectedCategoryId: _selectedBlogCategoryId,
          onCategorySelected: (categoryId) {
            setState(() {
              _selectedBlogCategoryId = categoryId;
            });
          },
        );
      default:
        return const SizedBox.shrink();
    }
  }
  
  void _navigateToRagSearch(String query) {
    context.router.push(RagSearchRoute(initialQuery: query));
  }
}
