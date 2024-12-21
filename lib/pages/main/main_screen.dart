import 'package:flutter/material.dart';
import '../../core/routes/route_paths.dart';
import '../chat/chat_list_page.dart';
import '../service/service_page.dart';
import '../games/games_page.dart';
import '../community/community_page.dart';
import '../profile/profile_page.dart';

class MainScreen extends StatelessWidget {
  final List<BottomNavigationBarItem> navigationItems = [
    BottomNavigationBarItem(
      icon: Icon(Icons.chat),
      label: '首页',
    ),
    BottomNavigationBarItem(
      icon: Icon(Icons.medical_services),
      label: 'SUOKE',
    ),
    BottomNavigationBarItem(
      icon: Icon(Icons.explore),
      label: '探索',
    ),
    BottomNavigationBarItem(
      icon: Icon(Icons.lifestyle),
      label: 'LIFE',
    ),
    BottomNavigationBarItem(
      icon: Icon(Icons.person),
      label: '我的',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _pages,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.chat_outlined),
            selectedIcon: Icon(Icons.chat),
            label: '聊天',
          ),
          NavigationDestination(
            icon: Icon(Icons.storefront_outlined),
            selectedIcon: Icon(Icons.storefront),
            label: '服务',
          ),
          NavigationDestination(
            icon: Icon(Icons.sports_esports_outlined),
            selectedIcon: Icon(Icons.sports_esports),
            label: '游戏',
          ),
          NavigationDestination(
            icon: Icon(Icons.people_outline),
            selectedIcon: Icon(Icons.people),
            label: '社群',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person),
            label: '我的',
          ),
        ],
      ),
    );
  }
} 