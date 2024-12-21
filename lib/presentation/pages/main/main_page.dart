import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/main_controller.dart';
import 'package:suoke_life/presentation/widgets/bottom_nav_bar.dart';
import 'package:suoke_life/presentation/pages/home/home_page.dart';
import 'package:suoke_life/presentation/pages/chat/chat_page.dart';
import 'package:suoke_life/presentation/pages/ai/ai_page.dart';
import 'package:suoke_life/presentation/pages/games/games_page.dart';
import 'package:suoke_life/presentation/pages/profile/profile_page.dart';

class MainPage extends GetView<MainController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Obx(() => IndexedStack(
        index: controller.currentIndex,
        children: [
          HomePage(),
          ChatPage(),
          AIPage(),
          GamesPage(), 
          ProfilePage(),
        ],
      )),
      bottomNavigationBar: Obx(() => BottomNavBar(
        currentIndex: controller.currentIndex,
        onTap: controller.changePage,
      )),
    );
  }
} 