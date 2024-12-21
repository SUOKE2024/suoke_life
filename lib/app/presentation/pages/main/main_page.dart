import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/main_controller.dart';
import '../../widgets/navigation/main_bottom_nav_bar.dart';
import '../message/message_page.dart';
import '../suoke/suoke_page.dart';
import '../explore/explore_page.dart';
import '../life/life_page.dart';
import '../profile/profile_page.dart';

class MainPage extends GetView<MainController> {
  const MainPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Obx(() => Scaffold(
      body: IndexedStack(
        index: controller.currentIndex.value,
        children: const [
          MessagePage(),
          SuokePage(),
          ExplorePage(),
          LifePage(),
          ProfilePage(),
        ],
      ),
      bottomNavigationBar: MainBottomNavBar(
        currentIndex: controller.currentIndex.value,
        onTap: controller.changePage,
      ),
    ));
  }
} 