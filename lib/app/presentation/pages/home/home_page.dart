import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/home_controller.dart';

class HomePage extends GetView<HomeController> {
  const HomePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Obx(() => Text(controller.title.value)),
      ),
      body: Obx(() {
        return IndexedStack(
          index: controller.currentIndex.value,
          children: const [
            Center(child: Text('Home Content')),
            Center(child: Text('Chat Content')),
            Center(child: Text('Profile Content')),
          ],
        );
      }),
      bottomNavigationBar: Obx(() {
        return BottomNavigationBar(
          currentIndex: controller.currentIndex.value,
          onTap: controller.changeTab,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.home),
              label: 'Home',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.chat),
              label: 'Chat',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person),
              label: 'Profile',
            ),
          ],
        );
      }),
    );
  }
} 