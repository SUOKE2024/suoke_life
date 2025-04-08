import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import 'package:suoke_life/core/router/app_router.dart';
import 'package:suoke_life/di/providers/explore_providers.dart';
import 'package:suoke_life/presentation/common/widgets/error_message.dart';
import 'package:suoke_life/presentation/common/widgets/loading_indicator.dart';
import 'package:intl/intl.dart';

class BlogPostList extends ConsumerWidget {
  final String? authorId;
  final String? categoryId;
  final String? tag;
  final String? status;
  
  const BlogPostList({
    Key? key,
    this.authorId,
    this.categoryId,
    this.tag,
    this.status,
  }) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 监听博客文章列表状态
    final postsState = ref.watch(blogPostsProvider);
    
    // 初始加载或切换条件时重新加载数据
    ref.listen(blogPostsProvider, (previous, current) {
      if (previous?.currentPage == 1 && !current.isLoading && current.posts.isEmpty) {
        ref.read(blogPostsProvider.notifier).fetchPosts(
          authorId: authorId,
          categoryId: categoryId,
          tag: tag,
          status: status,
        );
      }
    });
    
    // 显示加载中状态
    if (postsState.isLoading && postsState.posts.isEmpty) {
      return const Center(
        child: LoadingIndicator(),
      );
    }
    
    // 显示错误信息
    if (postsState.errorMessage != null && postsState.posts.isEmpty) {
      return Center(
        child: ErrorMessage(
          message: postsState.errorMessage!,
          onRetry: () => ref.read(blogPostsProvider.notifier).fetchPosts(
            authorId: authorId,
            categoryId: categoryId,
            tag: tag,
            status: status,
          ),
        ),
      );
    }
    
    // 显示空数据状态
    if (postsState.posts.isEmpty) {
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
              '暂无博客文章',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 8),
            TextButton(
              onPressed: () => ref.read(blogPostsProvider.notifier).fetchPosts(
                authorId: authorId,
                categoryId: categoryId,
                tag: tag,
                status: status,
              ),
              child: const Text('刷新'),
            ),
          ],
        ),
      );
    }
    
    // 显示博客文章列表
    return RefreshIndicator(
      onRefresh: () async {
        ref.read(blogPostsProvider.notifier).refreshPosts(
          authorId: authorId,
          categoryId: categoryId,
          tag: tag,
          status: status,
        );
      },
      child: NotificationListener<ScrollNotification>(
        onNotification: (ScrollNotification scrollInfo) {
          if (scrollInfo.metrics.pixels == scrollInfo.metrics.maxScrollExtent) {
            // 滚动到底部时加载更多
            ref.read(blogPostsProvider.notifier).loadMorePosts(
              authorId: authorId,
              categoryId: categoryId,
              tag: tag,
              status: status,
            );
          }
          return false;
        },
        child: ListView.builder(
          padding: const EdgeInsets.symmetric(vertical: 8),
          itemCount: postsState.isLoading 
              ? postsState.posts.length + 1 
              : postsState.posts.length,
          itemBuilder: (context, index) {
            // 显示加载更多指示器
            if (index == postsState.posts.length && postsState.isLoading) {
              return const Padding(
                padding: EdgeInsets.all(16.0),
                child: Center(
                  child: CircularProgressIndicator(),
                ),
              );
            }
            
            // 显示博客文章项
            final post = postsState.posts[index];
            
            return BlogPostItem(
              id: post['id'],
              title: post['title'],
              summary: post['summary'] ?? '',
              authorName: post['author_name'] ?? '',
              authorAvatarUrl: post['author_avatar_url'],
              coverImageUrl: post['cover_image_url'],
              publishedAt: post['published_at'] != null
                  ? DateTime.parse(post['published_at'])
                  : null,
              viewCount: post['view_count'] ?? 0,
              commentCount: post['comment_count'] ?? 0,
              likeCount: post['like_count'] ?? 0,
              tags: post['tags'] != null
                  ? List<String>.from(post['tags'])
                  : <String>[],
            );
          },
        ),
      ),
    );
  }
}

class BlogPostItem extends StatelessWidget {
  final String id;
  final String title;
  final String summary;
  final String authorName;
  final String? authorAvatarUrl;
  final String? coverImageUrl;
  final DateTime? publishedAt;
  final int viewCount;
  final int commentCount;
  final int likeCount;
  final List<String> tags;
  
  const BlogPostItem({
    Key? key,
    required this.id,
    required this.title,
    required this.summary,
    required this.authorName,
    this.authorAvatarUrl,
    this.coverImageUrl,
    this.publishedAt,
    required this.viewCount,
    required this.commentCount,
    required this.likeCount,
    required this.tags,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final dateFormatter = DateFormat('yyyy-MM-dd');
    
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        onTap: () {
          // 导航到博客文章详情页
          // 当我们创建了博客文章详情页后，应该更新这里的导航
          // context.router.push(BlogPostDetailRoute(postId: id));
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
                  // 作者信息和发布日期
                  Row(
                    children: [
                      // 作者头像
                      CircleAvatar(
                        radius: 16,
                        backgroundImage: authorAvatarUrl != null
                            ? NetworkImage(authorAvatarUrl!)
                            : null,
                        child: authorAvatarUrl == null
                            ? const Icon(Icons.person, size: 16)
                            : null,
                      ),
                      
                      const SizedBox(width: 8),
                      
                      // 作者名称
                      Text(
                        authorName,
                        style: TextStyle(
                          color: Colors.grey[800],
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      
                      const Spacer(),
                      
                      // 发布日期
                      if (publishedAt != null)
                        Text(
                          dateFormatter.format(publishedAt!),
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: 12,
                          ),
                        ),
                    ],
                  ),
                  
                  const SizedBox(height: 12),
                  
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
                  
                  // 标签
                  if (tags.isNotEmpty) ...[
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 8,
                      runSpacing: 4,
                      children: tags.take(3).map((tag) => Chip(
                        label: Text(
                          tag,
                          style: const TextStyle(fontSize: 10),
                        ),
                        backgroundColor: Colors.grey[200],
                        padding: EdgeInsets.zero,
                        labelPadding: const EdgeInsets.symmetric(horizontal: 8),
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      )).toList(),
                    ),
                  ],
                  
                  const SizedBox(height: 8),
                  
                  // 统计信息
                  Row(
                    children: [
                      // 阅读量
                      Icon(
                        Icons.remove_red_eye_outlined,
                        size: 16,
                        color: Colors.grey[600],
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '$viewCount',
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 12,
                        ),
                      ),
                      
                      const SizedBox(width: 16),
                      
                      // 评论数
                      Icon(
                        Icons.comment_outlined,
                        size: 16,
                        color: Colors.grey[600],
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '$commentCount',
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 12,
                        ),
                      ),
                      
                      const SizedBox(width: 16),
                      
                      // 点赞数
                      Icon(
                        Icons.thumb_up_outlined,
                        size: 16,
                        color: Colors.grey[600],
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '$likeCount',
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