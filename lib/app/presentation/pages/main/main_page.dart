import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import '../../core/router/router_config.dart';

@RoutePage()
class MainPage extends StatelessWidget {
  const MainPage({super.key});

  @override
  Widget build(BuildContext context) {
    return AutoTabsScaffold(
      routes: const [
        HomeRoute(),
        SuokeRoute(),
        ExploreRoute(),
        LifeRoute(),
        ProfileRoute(),
      ],
      bottomNavigationBuilder: (_, tabsRouter) {
        return BottomNavigationBar(
          currentIndex: tabsRouter.activeIndex,
          onTap: tabsRouter.setActiveIndex,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.home),
              label: '首页',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.search),
              label: '搜客',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.explore),
              label: '探索',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.favorite),
              label: '生活',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person),
              label: '我的',
            ),
          ],
        );
      },
    );
  }
} 