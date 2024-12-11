import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'home/home_page.dart';
import 'explore/explore_page.dart';
import 'community/community_page.dart';
import 'profile/profile_page.dart';
import 'service/service_page.dart';

class AppPage extends StatefulWidget {
  const AppPage({Key? key}) : super(key: key);

  @override
  State<AppPage> createState() => _AppPageState();
}

class _AppPageState extends State<AppPage> {
  int _currentIndex = 0;

  final _pages = const [
    HomePage(),
    ExplorePage(),
    ServicePage(),
    CommunityPage(),
    ProfilePage(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: '首页',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.explore),
            label: '探索',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.medical_services),
            label: '服务',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.people),
            label: '社区',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: '我的',
          ),
        ],
      ),
    );
  }
} 