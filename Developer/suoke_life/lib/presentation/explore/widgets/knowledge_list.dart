import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import 'package:suoke_life/core/router/app_router.dart';
import 'package:suoke_life/di/providers/explore_providers.dart';
import 'package:suoke_life/domain/entities/laoke/knowledge_category.dart';
import 'package:suoke_life/presentation/common/widgets/error_message.dart';
import 'package:suoke_life/presentation/common/widgets/loading_indicator.dart';

class KnowledgeList extends ConsumerWidget {
  final String? categoryId;
  
  const KnowledgeList({
    Key? key,
    this.categoryId,
  }) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 监听知识文章列表状态
    final articlesState = ref.watch(knowledgeArticlesProvider);
    
    // 初始加载或切换分类时重新加载数据
    ref.listen(knowledgeArticlesProvider, (previous, current) {
      if (previous?.currentPage == 1 && !current.isLoading && current.articles.isEmpty) {
        ref.read(knowledgeArticlesProvider.notifier).fetchArticles(
          categoryId: categoryId,
        );
      }
    });
    
    // 显示加载中状态
    if (articlesState.isLoading && articlesState.articles.isEmpty) {
      return const Center(
        child: LoadingIndicator(),
      );
    }
    
    // 显示错误信息
    if (articlesState.errorMessage != null && articlesState.articles.isEmpty) {
      return Center(
        child: ErrorMessage(
          message: articlesState.errorMessage!,
          onRetry: () => ref.read(knowledgeArticlesProvider.notifier).fetchArticles(
            categoryId: categoryId,
          ),
        ),
      );
    }
    
    // 显示空数据状态
    if (articlesState.articles.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.article_outlined,
              size: 64,
              color: Colors.grey,
            ),
            const SizedBox(height: 16),
            Text(
              '暂无文章',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 8),
            TextButton(
              onPressed: () => ref.read(knowledgeArticlesProvider.notifier).fetchArticles(
                categoryId: categoryId,
              ),
              child: const Text('刷新'),
            ),
          ],
        ),
      );
    }
    
    // 显示文章列表
    return RefreshIndicator(
      onRefresh: () async {
        ref.read(knowledgeArticlesProvider.notifier).refreshArticles(
          categoryId: categoryId,
        );
      },
      child: NotificationListener<ScrollNotification>(
        onNotification: (ScrollNotification scrollInfo) {
          if (scrollInfo.metrics.pixels == scrollInfo.metrics.maxScrollExtent) {
            // 滚动到底部时加载更多
            ref.read(knowledgeArticlesProvider.notifier).loadMoreArticles(
              categoryId: categoryId,
            );
          }
          return false;
        },
        child: ListView.builder(
          padding: const EdgeInsets.symmetric(vertical: 8),
          itemCount: articlesState.isLoading 
              ? articlesState.articles.length + 1 
              : articlesState.articles.length,
          itemBuilder: (context, index) {
            // 显示加载更多指示器
            if (index == articlesState.articles.length && articlesState.isLoading) {
              return const Padding(
                padding: EdgeInsets.all(16.0),
                child: Center(
                  child: CircularProgressIndicator(),
                ),
              );
            }
            
            // 显示文章项
            final article = articlesState.articles[index];
            
            return KnowledgeArticleItem(
              id: article['id'],
              title: article['title'],
              summary: article['summary'] ?? '',
              coverImageUrl: article['cover_image_url'],
              viewCount: article['view_count'] ?? 0,
              categoryName: article['category_name'] ?? '',
            );
          },
        ),
      ),
    );
  }
}

class KnowledgeArticleItem extends StatelessWidget {
  final String id;
  final String title;
  final String summary;
  final String? coverImageUrl;
  final int viewCount;
  final String categoryName;
  
  const KnowledgeArticleItem({
    Key? key,
    required this.id,
    required this.title,
    required this.summary,
    this.coverImageUrl,
    required this.viewCount,
    required this.categoryName,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        onTap: () {
          context.router.push(
            KnowledgeArticleDetailRoute(articleId: id),
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 封面图片
            if (coverImageUrl != null)
              ClipRRect(
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(12),
                ),
                child: AspectRatio(
                  aspectRatio: 16 / 9,
                  child: Image.network(
                    coverImageUrl!,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) {
                      return Container(
                        color: Colors.grey[200],
                        child: const Center(
                          child: Icon(
                            Icons.broken_image,
                            color: Colors.grey,
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ),
              
            // 文章内容
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 分类标签
                  if (categoryName.isNotEmpty)
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.green[50],
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        categoryName,
                        style: TextStyle(
                          color: Colors.green[700],
                          fontSize: 12,
                        ),
                      ),
                    ),
                  
                  const SizedBox(height: 8),
                  
                  // 标题
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  
                  const SizedBox(height: 8),
                  
                  // 摘要
                  Text(
                    summary,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Colors.grey[700],
                    ),
                    maxLines: 3,
                    overflow: TextOverflow.ellipsis,
                  ),
                  
                  const SizedBox(height: 8),
                  
                  // 阅读量
                  Row(
                    children: [
                      Icon(
                        Icons.remove_red_eye_outlined,
                        size: 16,
                        color: Colors.grey[600],
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '$viewCount 阅读',
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// 知识分类选择器
class KnowledgeCategorySelector extends ConsumerWidget {
  final String? selectedCategoryId;
  final ValueChanged<String?> onCategorySelected;
  
  const KnowledgeCategorySelector({
    Key? key,
    this.selectedCategoryId,
    required this.onCategorySelected,
  }) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final categoriesAsync = ref.watch(knowledgeCategoriesProvider);
    
    return categoriesAsync.when(
      data: (categories) => SizedBox(
        height: 48,
        child: ListView.builder(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 8),
          itemCount: categories.length + 1, // +1 for "全部" 选项
          itemBuilder: (context, index) {
            if (index == 0) {
              // "全部" 选项
              return _buildCategoryChip(
                context,
                null,
                '全部',
                selectedCategoryId == null,
              );
            }
            
            final category = categories[index - 1];
            return _buildCategoryChip(
              context,
              category.id,
              category.name,
              selectedCategoryId == category.id,
            );
          },
        ),
      ),
      loading: () => const Center(
        child: SizedBox(
          height: 48,
          child: Center(
            child: CircularProgressIndicator(),
          ),
        ),
      ),
      error: (error, stackTrace) => SizedBox(
        height: 48,
        child: Center(
          child: TextButton.icon(
            onPressed: () => ref.refresh(knowledgeCategoriesProvider),
            icon: const Icon(Icons.refresh),
            label: const Text('加载失败，点击重试'),
          ),
        ),
      ),
    );
  }
  
  Widget _buildCategoryChip(
    BuildContext context, 
    String? categoryId, 
    String name, 
    bool isSelected,
  ) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: ChoiceChip(
        label: Text(name),
        selected: isSelected,
        onSelected: (selected) {
          if (selected) {
            onCategorySelected(categoryId);
          }
        },
        backgroundColor: Colors.grey[200],
        selectedColor: Colors.green[100],
        labelStyle: TextStyle(
          color: isSelected ? Colors.green[700] : Colors.grey[700],
          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
        ),
      ),
    );
  }
} 