import 'package:flutter/material.dart';
import 'package:suoke_life/libs/ui_components/lib/navigation/bottom_navigation_bar.dart';
import 'package:suoke_life/core/navigation/app_routes.dart';

class ExplorePage extends StatefulWidget {
  const ExplorePage({Key? key}) : super(key: key);

  @override
  _ExplorePageState createState() => _ExplorePageState();
}

class _ExplorePageState extends State<ExplorePage> {
  int _currentIndex = 2;

  void _onTabTapped(int index) {
    setState(() {
      _currentIndex = index;
    });
    switch (index) {
      case 0:
        Navigator.pushReplacementNamed(context, AppRoutes.chat);
        break;
      case 1:
        Navigator.pushReplacementNamed(context, AppRoutes.suoke);
        break;
      case 2:
        Navigator.pushReplacementNamed(context, AppRoutes.explore);
        break;
      case 3:
        Navigator.pushReplacementNamed(context, AppRoutes.life);
        break;
      case 4:
        Navigator.pushReplacementNamed(context, AppRoutes.settings);
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Explore'),
      ),
      body: const Center(
        child: Text('Explore Page Content'),
      ),
      bottomNavigationBar: AppBottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: _onTabTapped,
      ),
    );
  }
}
