import 'package:flutter/material.dart';
import 'package:suoke_life/core/models/rag_result.dart';
import 'package:suoke_life/core/theme/app_colors.dart';

/// RAG查询结果卡片组件
///
/// 用于显示检索增强生成的结果项，并支持用户反馈
class RagResultCard extends StatelessWidget {
  /// 检索结果数据
  final RagResult result;

  /// 最大展示内容长度
  final int maxContentLength;

  /// 用户反馈回调（true=有用，false=无用）
  final Function(bool isHelpful)? onFeedback;

  /// 点击卡片回调
  final VoidCallback? onTap;

  /// 是否显示评分
  final bool showScore;

  /// 是否显示来源
  final bool showSource;

  const RagResultCard({
    Key? key,
    required this.result,
    this.maxContentLength = 200,
    this.onFeedback,
    this.onTap,
    this.showScore = false,
    this.showSource = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textTheme = theme.textTheme;

    // 获取来源信息
    final source = result.metadata['source'] as String? ?? '知识库';

    // 处理内容显示（如果过长则截断）
    final content = result.content.length > maxContentLength
        ? '${result.content.substring(0, maxContentLength)}...'
        : result.content;

    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 0),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.grey.withAlpha(30)),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 内容
              Text(
                content,
                style: textTheme.bodyMedium,
              ),

              const SizedBox(height: 12),

              // 元数据信息和反馈按钮
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // 左侧：来源和评分
                  Expanded(
                    child: Row(
                      children: [
                        if (showSource) ...[
                          Icon(
                            Icons.source_outlined,
                            size: 16,
                            color: Colors.grey[600],
                          ),
                          const SizedBox(width: 4),
                          Text(
                            source,
                            style: textTheme.bodySmall?.copyWith(
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                        if (showSource && showScore) const SizedBox(width: 12),
                        if (showScore) ...[
                          Icon(
                            Icons.trending_up,
                            size: 16,
                            color: Colors.grey[600],
                          ),
                          const SizedBox(width: 4),
                          Text(
                            '匹配度: ${(result.score * 100).toInt()}%',
                            style: textTheme.bodySmall?.copyWith(
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),

                  // 右侧：反馈按钮
                  if (onFeedback != null)
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        // 有用
                        IconButton(
                          icon: const Icon(Icons.thumb_up_alt_outlined),
                          iconSize: 18,
                          padding: EdgeInsets.zero,
                          constraints: const BoxConstraints(),
                          color: Colors.grey[600],
                          onPressed: () => onFeedback!(true),
                        ),
                        const SizedBox(width: 12),

                        // 无用
                        IconButton(
                          icon: const Icon(Icons.thumb_down_alt_outlined),
                          iconSize: 18,
                          padding: EdgeInsets.zero,
                          constraints: const BoxConstraints(),
                          color: Colors.grey[600],
                          onPressed: () => onFeedback!(false),
                        ),
                      ],
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// 详细RAG结果对话框
class RagResultDetailDialog extends StatelessWidget {
  /// 检索结果数据
  final RagResult result;

  /// 用户反馈回调（true=有用，false=无用）
  final Function(bool isHelpful)? onFeedback;

  const RagResultDetailDialog({
    Key? key,
    required this.result,
    this.onFeedback,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textTheme = theme.textTheme;

    return Dialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 标题
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '详细信息',
                  style: textTheme.titleLarge,
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.of(context).pop(),
                ),
              ],
            ),

            const Divider(),
            const SizedBox(height: 12),

            // 内容
            Flexible(
              child: SingleChildScrollView(
                child: Text(
                  result.content,
                  style: textTheme.bodyMedium,
                ),
              ),
            ),

            const SizedBox(height: 16),

            // 元数据展示
            if (result.metadata.isNotEmpty) ...[
              Text(
                '来源详情',
                style: textTheme.titleSmall,
              ),
              const SizedBox(height: 8),
              ...result.metadata.entries.map((entry) {
                if (entry.value == null) return const SizedBox.shrink();
                if (entry.key == 'text') return const SizedBox.shrink();

                return Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${entry.key}:',
                        style: textTheme.bodySmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.grey[700],
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          entry.value.toString(),
                          style: textTheme.bodySmall?.copyWith(
                            color: Colors.grey[700],
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ],

            const SizedBox(height: 20),

            // 反馈按钮
            if (onFeedback != null)
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    '这条信息对您有帮助吗？',
                    style: textTheme.bodySmall,
                  ),
                  const SizedBox(width: 16),

                  // 有用
                  ElevatedButton.icon(
                    icon: const Icon(Icons.thumb_up_alt_outlined, size: 16),
                    label: const Text('有用'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.brandPrimary,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 8),
                    ),
                    onPressed: () {
                      onFeedback!(true);
                      Navigator.of(context).pop();
                    },
                  ),

                  const SizedBox(width: 8),

                  // 无用
                  OutlinedButton.icon(
                    icon: const Icon(Icons.thumb_down_alt_outlined, size: 16),
                    label: const Text('无用'),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 8),
                    ),
                    onPressed: () {
                      onFeedback!(false);
                      Navigator.of(context).pop();
                    },
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}
