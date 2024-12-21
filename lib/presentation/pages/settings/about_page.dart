import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:suoke_life/routes/app_routes.dart';

class AboutPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('关于'),
      ),
      body: FutureBuilder<PackageInfo>(
        future: PackageInfo.fromPlatform(),
        builder: (context, snapshot) {
          if (!snapshot.hasData) {
            return Center(child: CircularProgressIndicator());
          }

          final info = snapshot.data!;
          return ListView(
            children: [
              // Logo和版本信息
              Container(
                padding: EdgeInsets.symmetric(vertical: 32),
                child: Column(
                  children: [
                    Image.asset(
                      'assets/images/logo.png',
                      width: 100,
                      height: 100,
                    ),
                    SizedBox(height: 16),
                    Text(
                      '索克生活',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    SizedBox(height: 8),
                    Text(
                      '版本 ${info.version}',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ],
                ),
              ),
              Divider(),
              // 功能列表
              ListTile(
                leading: Icon(Icons.update),
                title: Text('检查更新'),
                trailing: Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () => _checkUpdate(),
              ),
              ListTile(
                leading: Icon(Icons.description),
                title: Text('用户协议'),
                trailing: Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () => Get.toNamed(AppRoutes.USER_AGREEMENT),
              ),
              ListTile(
                leading: Icon(Icons.privacy_tip),
                title: Text('隐私政策'),
                trailing: Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () => Get.toNamed(AppRoutes.PRIVACY_POLICY),
              ),
              ListTile(
                leading: Icon(Icons.feedback),
                title: Text('意见反馈'),
                trailing: Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () => Get.toNamed(AppRoutes.FEEDBACK),
              ),
              // 联系方式
              Padding(
                padding: EdgeInsets.all(16),
                child: Column(
                  children: [
                    Text(
                      '联系我们',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    SizedBox(height: 8),
                    Text('邮箱: support@suoke.life'),
                    Text('电话: 400-xxx-xxxx'),
                  ],
                ),
              ),
              // 版权信息
              Padding(
                padding: EdgeInsets.all(16),
                child: Text(
                  '© 2024 索克生活 版权所有',
                  style: Theme.of(context).textTheme.bodySmall,
                  textAlign: TextAlign.center,
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  Future<void> _checkUpdate() async {
    try {
      Get.dialog(
        Center(child: CircularProgressIndicator()),
        barrierDismissible: false,
      );
      // TODO: 实现检查更新逻辑
      await Future.delayed(Duration(seconds: 1));
      Get.back();
      Get.snackbar('提示', '当前已是最新版本');
    } catch (e) {
      Get.back();
      Get.snackbar('错误', '检查更新失败: $e');
    }
  }
} 