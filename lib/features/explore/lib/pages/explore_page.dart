import 'package:flutter/material.dart';
import 'package:suoke_life/ui_components/navigation/bottom_navigation_bar.dart';
import 'package:suoke_life/features/explore/lib/widgets/explore_item_card.dart';
import 'package:suoke_life/core/utils/app_localizations.dart';

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

  void _onTabTapped(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(
        title: Text(localizations.translate('explore_title')),
      ),
      body: ListView(
        children: _exploreItems
            .map((item) => ExploreItemCard(
                  title: item.title,
                  description: item.description,
                  imageUrl: item.imageUrl,
                ))
            .toList(),
      ),
      bottomNavigationBar: AppBottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: _onTabTapped,
      ),
    );
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