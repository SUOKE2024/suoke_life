import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:core/core.dart';

class AppBottomNavigationBar extends StatelessWidget {
  const AppBottomNavigationBar({super.key});

  @override
  Widget build(BuildContext context) {
    return BottomNavigationBar(
      type: BottomNavigationBarType.fixed,
      items: const <BottomNavigationBarItem>[
        BottomNavigationBarItem(
          icon: Icon(Icons.home),
          label: '首页',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.business),
          label: 'SUOKE',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.explore),
          label: '探索',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.book),
          label: 'LIFE',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.person),
          label: '我的',
        ),
      ],
      currentIndex: _calculateSelectedIndex(context),
      onTap: (int index) => _onItemTapped(context, index),
    );
  }

  int _calculateSelectedIndex(BuildContext context) {
    final String location = GoRouterState.of(context).uri.toString();
    if (location.startsWith(AppRoutes.home)) {
      return 0;
    }
    if (location.startsWith(AppRoutes.suoke)) {
      return 1;
    }
    if (location.startsWith(AppRoutes.explore)) {
      return 2;
    }
    if (location.startsWith(AppRoutes.life)) {
      return 3;
    }
    if (location.startsWith(AppRoutes.profile)) {
      return 4;
    }
    return 0;
  }

  void _onItemTapped(BuildContext context, int index) {
    switch (index) {
      case 0:
        context.go(AppRoutes.home);
        break;
      case 1:
        context.go(AppRoutes.suoke);
        break;
      case 2:
        context.go(AppRoutes.explore);
        break;
      case 3:
        context.go(AppRoutes.life);
        break;
      case 4:
        context.go(AppRoutes.profile);
        break;
    }
  }
} 