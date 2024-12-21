import 'package:flutter/material.dart';

class CustomBottomNavBar extends StatelessWidget {
  final int currentIndex;
  final ValueChanged<int> onTap;

  const CustomBottomNavBar({
    Key? key,
    required this.currentIndex,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return NavigationBar(
      selectedIndex: currentIndex,
      onDestinationSelected: onTap,
      destinations: const [
        NavigationDestination(
          icon: Icon(Icons.home_outlined),
          selectedIcon: Icon(Icons.home),
          label: '首页',
        ),
        NavigationDestination(
          icon: Icon(Icons.smart_toy_outlined),
          selectedIcon: Icon(Icons.smart_toy),
          label: 'SUOKE',
        ),
        NavigationDestination(
          icon: Icon(Icons.explore_outlined),
          selectedIcon: Icon(Icons.explore),
          label: '探索',
        ),
        NavigationDestination(
          icon: Icon(Icons.favorite_outline),
          selectedIcon: Icon(Icons.favorite),
          label: 'LIFE',
        ),
        NavigationDestination(
          icon: Icon(Icons.person_outline),
          selectedIcon: Icon(Icons.person),
          label: '我的',
        ),
      ],
    );
  }
} 