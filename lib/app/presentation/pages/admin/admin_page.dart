import 'package:flutter/material.dart';
import 'package:get/get.dart';

class AdminPage extends GetView {
  const AdminPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('管理后台'),
      ),
      body: const Center(
        child: Text('管理后台页面'),
      ),
    );
  }
} 