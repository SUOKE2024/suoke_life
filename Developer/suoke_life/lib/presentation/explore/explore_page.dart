import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import 'package:suoke_life/core/router/app_router.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/presentation/common/widgets/custom_app_bar.dart';

@RoutePage()
class ExplorePage extends ConsumerStatefulWidget {
  const ExplorePage({Key? key}) : super(key: key);

  @override
  ConsumerState<ExplorePage> createState() => _ExplorePageState();
}

class _ExplorePageState extends ConsumerState<ExplorePage> {
  final TextEditingController _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const CustomAppBar(
        title: Text('探索'),
      ),
      body: CustomScrollView(
        slivers: [
          // 搜索区域
          SliverToBoxAdapter(
            child: Padding(
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
          ),

          // 推荐搜索标签
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 8),
                  Text(
                    '热门话题',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      _buildSearchChip('春季养生方法'),
                      _buildSearchChip('阴虚体质调理'),
                      _buildSearchChip('艾灸的作用与禁忌'),
                      _buildSearchChip('心火旺盛的表现'),
                      _buildSearchChip('湿热体质食疗'),
                      _buildSearchChip('脾胃虚弱的调理'),
                    ],
                  ),
                ],
              ),
            ),
          ),

          // 专题搜索区域
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 16),
                  Text(
                    '专题检索',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 16),
                  GridView.count(
                    crossAxisCount: 2,
                    crossAxisSpacing: 16,
                    mainAxisSpacing: 16,
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    children: [
                      _buildCategoryCard(
                        context: context,
                        title: '体质调理',
                        icon: Icons.accessibility_new,
                        color: Colors.green[700]!,
                        onTap: () => _navigateToSpecialSearch('constitution'),
                      ),
                      _buildCategoryCard(
                        context: context,
                        title: '穴位经络',
                        icon: Icons.bloodtype,
                        color: Colors.red[700]!,
                        onTap: () => _navigateToSpecialSearch('meridians'),
                      ),
                      _buildCategoryCard(
                        context: context,
                        title: '中药方剂',
                        icon: Icons.spa,
                        color: Colors.amber[800]!,
                        onTap: () => _navigateToSpecialSearch('herbs'),
                      ),
                      _buildCategoryCard(
                        context: context,
                        title: '养生食疗',
                        icon: Icons.restaurant,
                        color: Colors.blue[700]!,
                        onTap: () => _navigateToSpecialSearch('regimen'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // 构建搜索标签
  Widget _buildSearchChip(String label) {
    return ActionChip(
      label: Text(label),
      onPressed: () {
        _navigateToRagSearch(label);
      },
    );
  }

  // 构建分类卡片
  Widget _buildCategoryCard({
    required BuildContext context,
    required String title,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                size: 48,
                color: color,
              ),
              const SizedBox(height: 12),
              Text(
                title,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // 导航到专题搜索
  void _navigateToSpecialSearch(String type) {
    // 暂时使用通用搜索，实际应用中可以导航到特定的搜索页面
    context.router.push(
      RagSearchRoute(searchType: type),
    );
  }

  void _navigateToRagSearch(String query) {
    context.router.push(RagSearchRoute(initialQuery: query));
  }
}
