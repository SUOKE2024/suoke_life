import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import 'package:suoke_life/di/providers/explore_providers.dart';
import 'package:suoke_life/domain/usecases/laoke/get_knowledge_article_by_id.dart';
import 'package:suoke_life/domain/usecases/laoke/text_to_speech.dart';
import 'package:suoke_life/presentation/common/widgets/custom_app_bar.dart';
import 'package:suoke_life/presentation/common/widgets/error_message.dart';
import 'package:suoke_life/presentation/common/widgets/loading_indicator.dart';

/// 知识文章详情页面
@RoutePage()
class KnowledgeArticleDetailPage extends ConsumerWidget {
  final String articleId;

  const KnowledgeArticleDetailPage({
    Key? key,
    @PathParam('articleId') required this.articleId,
  }) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: const CustomAppBar(
        title: Text('文章详情'),
      ),
      body: _buildArticleDetail(context, ref),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _textToSpeech(context, ref),
        tooltip: '朗读文章',
        child: const Icon(Icons.volume_up),
      ),
    );
  }

  Widget _buildArticleDetail(BuildContext context, WidgetRef ref) {
    final articleDetail = ref.watch(
      articleDetailProvider(articleId),
    );

    return articleDetail.when(
      data: (article) => SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 封面图片
            if (article.coverImageUrl != null)
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: AspectRatio(
                  aspectRatio: 16 / 9,
                  child: Image.network(
                    article.coverImageUrl!,
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

            const SizedBox(height: 16),
            
            // 文章标题
            Text(
              article.title,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            
            const SizedBox(height: 8),
            
            // 文章信息
            Row(
              children: [
                // 分类标签
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
                    article.categoryName,
                    style: TextStyle(
                      color: Colors.green[700],
                      fontSize: 12,
                    ),
                  ),
                ),
                
                const SizedBox(width: 8),
                
                // 作者
                Text(
                  article.authorName,
                  style: TextStyle(
                    color: Colors.grey[700],
                    fontSize: 12,
                  ),
                ),
                
                const Spacer(),
                
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
                      '${article.viewCount}',
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(width: 8),
                
                // 点赞量
                Row(
                  children: [
                    Icon(
                      Icons.thumb_up_outlined,
                      size: 16,
                      color: Colors.grey[600],
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '${article.likeCount}',
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            
            const Divider(height: 32),
            
            // 文章内容
            Text(
              article.content,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            
            const SizedBox(height: 16),
            
            // 标签
            if (article.tags.isNotEmpty) ...[
              const Divider(),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: article.tags.map((tag) => Chip(
                  label: Text(tag),
                  backgroundColor: Colors.grey[200],
                )).toList(),
              ),
            ],
            
            const SizedBox(height: 32),
          ],
        ),
      ),
      loading: () => const Center(
        child: LoadingIndicator(),
      ),
      error: (error, stackTrace) => Center(
        child: ErrorMessage(
          message: '获取文章失败: ${error.toString()}',
          onRetry: () => ref.refresh(articleDetailProvider(articleId)),
        ),
      ),
    );
  }
  
  Future<void> _textToSpeech(BuildContext context, WidgetRef ref) async {
    final articleDetail = ref.read(articleDetailProvider(articleId));
    
    articleDetail.whenData((article) async {
      final textToSpeech = ref.read(textToSpeechProvider);
      
      // 显示加载中对话框
      final messenger = ScaffoldMessenger.of(context);
      messenger.showSnackBar(
        const SnackBar(
          content: Text('正在将文章转换为语音，请稍候...'),
          duration: Duration(seconds: 2),
        ),
      );
      
      // 调用文字转语音服务
      final result = await textToSpeech(
        params: TextToSpeechParams(
          text: article.title + '\n\n' + article.content,
        ),
      );
      
      result.fold(
        (failure) {
          messenger.showSnackBar(
            SnackBar(
              content: Text('语音转换失败: ${failure.message}'),
              backgroundColor: Colors.red,
            ),
          );
        },
        (audioData) {
          // 这里应该播放语音数据
          // 实际实现可能需要使用音频播放插件
          messenger.showSnackBar(
            const SnackBar(
              content: Text('语音转换成功，开始播放...'),
              duration: Duration(seconds: 2),
            ),
          );
          
          // TODO: 实现音频播放功能
        },
      );
    });
  }
}

/// 文章详情Provider
final articleDetailProvider = FutureProvider.family<dynamic, String>((ref, articleId) async {
  final getArticleById = ref.watch(getKnowledgeArticleByIdProvider);
  final result = await getArticleById(
    params: KnowledgeArticleParams(id: articleId),
  );
  
  return result.fold(
    (failure) => throw Exception(failure.message),
    (article) => article,
  );
}); 