import 'package:flutter/material.dart';
import 'package:get/get.dart';

class MainBottomNavBar extends StatelessWidget {
  final int currentIndex;
  final Function(int) onTap;

  const MainBottomNavBar({
    Key? key,
    required this.currentIndex,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BottomNavigationBar(
      currentIndex: currentIndex,
      onTap: onTap,
      type: BottomNavigationBarType.fixed,
      items: const [
        BottomNavigationBarItem(
          icon: Icon(Icons.message),
          label: '消息',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.group),
          label: '索客',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.explore),
          label: '发现',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.local_activity),
          label: '生活',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.person),
          label: '我的',
        ),
      ],
    );
  }
} 