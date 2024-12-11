import 'package:flutter/material.dart';
import '../../core/routes/route_paths.dart';

class GamesPage extends StatelessWidget {
  const GamesPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('游戏'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // 老克寻宝记
          _buildGameCard(
            context,
            title: '老克寻宝记',
            subtitle: '和老克一起探索神秘宝藏',
            description: '在云南大地上，跟随老克的脚步，探索神秘宝藏，收集珍稀物品，结识志同道合的朋友。',
            imagePath: 'assets/images/games/treasure_quest.jpg',
            route: RoutePaths.treasureQuest,
            features: const [
              '实时AR探索',
              '丰富的收藏品',
              '有趣的任务',
              '社交互动',
            ],
            tags: const [
              '探险',
              'AR游戏',
              '收藏',
              '社交',
            ],
          ),

          const SizedBox(height: 16),

          // 即将推出的游戏
          _buildComingSoonCard(
            context,
            title: '花语图鉴',
            subtitle: '发现花卉的奥秘',
            description: '通过AR技术识别花卉，收集花语，记录生长过程，分享美好时刻。',
            imagePath: 'assets/images/games/flower_quest.jpg',
            features: const [
              'AR花卉识别',
              '花语收集',
              '养护指南',
              '社区分享',
            ],
            tags: const [
              '园艺',
              'AR识别',
              '图鉴',
              '分享',
            ],
          ),

          const SizedBox(height: 16),

          _buildComingSoonCard(
            context,
            title: '咖啡之旅',
            subtitle: '探索咖啡文化',
            description: '走访云南咖啡产地，了解咖啡知识，品鉴特色咖啡，记录咖啡故事。',
            imagePath: 'assets/images/games/coffee_quest.jpg',
            features: const [
              '咖啡地图',
              '品鉴指南',
              '故事收集',
              '咖啡师认证',
            ],
            tags: const [
              '咖啡',
              '文化',
              '品鉴',
              '认证',
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildGameCard(
    BuildContext context, {
    required String title,
    required String subtitle,
    required String description,
    required String imagePath,
    required String route,
    required List<String> features,
    required List<String> tags,
  }) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () => Navigator.pushNamed(context, route),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 游戏封面图
            AspectRatio(
              aspectRatio: 16 / 9,
              child: Image.asset(
                imagePath,
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) {
                  return Container(
                    color: Colors.grey[300],
                    child: const Icon(
                      Icons.image_not_supported,
                      size: 48,
                      color: Colors.grey,
                    ),
                  );
                },
              ),
            ),

            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 标题和副标题
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Colors.grey[600],
                        ),
                  ),
                  const SizedBox(height: 8),

                  // 描述
                  Text(
                    description,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 16),

                  // 特色功能
                  Wrap(
                    spacing: 16,
                    runSpacing: 8,
                    children: features.map((feature) {
                      return Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.check_circle_outline,
                            size: 16,
                            color: Colors.green,
                          ),
                          const SizedBox(width: 4),
                          Text(feature),
                        ],
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 16),

                  // 标签
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: tags.map((tag) {
                      return Chip(
                        label: Text(tag),
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      );
                    }).toList(),
                  ),

                  const SizedBox(height: 16),

                  // 开始游戏按钮
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () => Navigator.pushNamed(context, route),
                      child: const Text('开始游戏'),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildComingSoonCard(
    BuildContext context, {
    required String title,
    required String subtitle,
    required String description,
    required String imagePath,
    required List<String> features,
    required List<String> tags,
  }) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: Stack(
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 游戏封面图
              AspectRatio(
                aspectRatio: 16 / 9,
                child: ColorFiltered(
                  colorFilter: ColorFilter.mode(
                    Colors.grey,
                    BlendMode.saturation,
                  ),
                  child: Image.asset(
                    imagePath,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) {
                      return Container(
                        color: Colors.grey[300],
                        child: const Icon(
                          Icons.image_not_supported,
                          size: 48,
                          color: Colors.grey,
                        ),
                      );
                    },
                  ),
                ),
              ),

              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 标题和副标题
                    Text(
                      title,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            color: Colors.grey[600],
                          ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: Colors.grey[600],
                          ),
                    ),
                    const SizedBox(height: 8),

                    // 描述
                    Text(
                      description,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: Colors.grey[600],
                          ),
                    ),
                    const SizedBox(height: 16),

                    // 特色功能
                    Wrap(
                      spacing: 16,
                      runSpacing: 8,
                      children: features.map((feature) {
                        return Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              Icons.check_circle_outline,
                              size: 16,
                              color: Colors.grey,
                            ),
                            const SizedBox(width: 4),
                            Text(
                              feature,
                              style: TextStyle(color: Colors.grey[600]),
                            ),
                          ],
                        );
                      }).toList(),
                    ),
                    const SizedBox(height: 16),

                    // 标签
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: tags.map((tag) {
                        return Chip(
                          label: Text(
                            tag,
                            style: TextStyle(color: Colors.grey[600]),
                          ),
                          backgroundColor: Colors.grey[200],
                        );
                      }).toList(),
                    ),
                  ],
                ),
              ),
            ],
          ),
          Positioned.fill(
            child: Container(
              alignment: Alignment.center,
              color: Colors.black.withOpacity(0.1),
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 8,
                ),
                decoration: BoxDecoration(
                  color: Colors.black.withOpacity(0.6),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Text(
                  '即将推出',
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
} 