import 'package:flutter/material.dart';

import '../../services/services/auth_service.dart';
import '../widgets/profile_header.dart';
import '../widgets/profile_menu_list.dart';

class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('我的'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              // TODO: 打开设置页面
            },
          ),
        ],
      ),
      body: Consumer<AuthService>(
        builder: (context, authService, child) {
          if (!authService.isAuthenticated) {
            return Center(
              child: ElevatedButton(
                onPressed: () {
                  // TODO: 打开登录页面
                },
                child: const Text('登录/注册'),
              ),
            );
          }

          return ListView(
            children: [
              ProfileHeader(userInfo: authService.userInfo!),
              const SizedBox(height: 16),
              const ProfileMenuList(),
            ],
          );
        },
      ),
    );
  }
} 