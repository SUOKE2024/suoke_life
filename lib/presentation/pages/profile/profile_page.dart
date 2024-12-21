import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/profile_controller.dart';
import 'package:suoke_life/routes/app_routes.dart';

class ProfilePage extends GetView<ProfileController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('我的'),
      ),
      body: Center(
        child: Text('个人中心'),
      ),
    );
  }
} 