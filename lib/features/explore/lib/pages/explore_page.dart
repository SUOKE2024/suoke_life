import 'package:flutter/material.dart';
import 'package:suoke_life/lib/core/widgets/common_scaffold.dart';
import 'package:suoke_life/features/explore/lib/widgets/explore_item_card.dart';
import 'package:suoke_life/lib/core/utils/app_localizations.dart';
import 'package:suoke_life/lib/core/widgets/common_bottom_navigation_bar.dart';

class ExplorePage extends StatefulWidget {
  const ExplorePage({Key? key}) : super(key: key);

  @override
  State<ExplorePage> createState() => _ExplorePageState();
}

class _ExplorePageState extends State<ExplorePage> {
  int _currentIndex = 2;
  final List<ExploreItem> _exploreItems = [
    ExploreItem(
      title: 'Hiking Trail',
      description: 'Explore a beautiful hiking trail.',
      imageUrl: 'assets/images/hiking.jpg',
    ),
    ExploreItem(
      title: 'Local Park',
      description: 'Visit a local park for relaxation.',
      imageUrl: 'assets/images/park.jpg',
    ),
    ExploreItem(
      title: 'City Museum',
      description: 'Discover the city\'s history.',
      imageUrl: 'assets/images/museum.jpg',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return CommonScaffold(
      title: AppLocalizations.of(context)!.translate('explore') ?? 'Explore',
      body: GridView.builder(
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          crossAxisSpacing: 10,
          mainAxisSpacing: 10,
        ),
        itemCount: _exploreItems.length,
        itemBuilder: (context, index) {
          final item = _exploreItems[index];
          return ExploreItemCard(
            title: item.title,
            description: item.description,
            imageUrl: item.imageUrl,
            onTap: () {
              // 实现探索项目详情逻辑
              Navigator.pushNamed(context, '/exploreDetail', arguments: item);
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // 实现内容生成逻辑
          _generateContent();
        },
        child: const Icon(Icons.add),
      ),
      bottomNavigationBar: CommonBottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
            // TODO: 实现底部导航逻辑
          });
        },
      ),
    );
  }

  void _generateContent() {
    // TODO: 实现内容生成逻辑
    print('内容生成成功');
  }
}

class ExploreItem {
  final String title;
  final String description;
  final String imageUrl;

  ExploreItem({
    required this.title,
    required this.description,
    required this.imageUrl,
  });
} 