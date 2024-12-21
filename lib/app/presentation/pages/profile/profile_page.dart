import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/base/base_page.dart';
import '../../controllers/profile_controller.dart';
import '../../widgets/profile_header.dart';
import '../../widgets/settings_tile.dart';
import '../../routes/app_routes.dart';
import '../../services/auth_service.dart';

class ProfilePage extends BasePage<ProfileController> {
  const ProfilePage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('个人中心'),
      actions: [
        IconButton(
          icon: const Icon(Icons.settings_outlined),
          onPressed: () => controller.navigateToSettings(),
        ),
      ],
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        children: [
          // 用户信息头部
          Obx(() => ProfileHeader(
            avatar: controller.userInfo.value.avatar,
            name: controller.userInfo.value.name,
            role: controller.userInfo.value.role,
            onAvatarTap: controller.updateAvatar,
            onNameTap: controller.updateName,
          )),
          
          // 功能列表
          const SizedBox(height: 16),
          Card(
            child: Column(
              children: [
                SettingsTile(
                  icon: Icons.person_outline,
                  title: '账号管理',
                  onTap: controller.navigateToAccount,
                ),
                const Divider(height: 1),
                SettingsTile(
                  icon: Icons.privacy_tip_outlined,
                  title: '隐私设置',
                  onTap: controller.navigateToPrivacy,
                ),
                const Divider(height: 1),
                SettingsTile(
                  icon: Icons.devices_outlined,
                  title: '设备管理',
                  onTap: controller.navigateToDevices,
                ),
                ListTile(
                  leading: const Icon(Icons.settings),
                  title: const Text('设置'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => Get.toNamed(Routes.SETTINGS),
                ),
                ListTile(
                  leading: const Icon(Icons.logout),
                  title: const Text('退出登录'),
                  onTap: () async {
                    final confirmed = await Get.dialog<bool>(
                      AlertDialog(
                        title: const Text('退出登录'),
                        content: const Text('确定要退出登录吗？'),
                        actions: [
                          TextButton(
                            onPressed: () => Get.back(result: false),
                            child: const Text('取消'),
                          ),
                          TextButton(
                            onPressed: () => Get.back(result: true),
                            child: const Text('确定'),
                          ),
                        ],
                      ),
                    );
                    
                    if (confirmed == true) {
                      await Get.find<AuthService>().logout();
                      Get.offAllNamed(Routes.LOGIN);
                    }
                  },
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 16),
          Card(
            child: Column(
              children: [
                SettingsTile(
                  icon: Icons.help_outline,
                  title: '帮助与反馈',
                  onTap: controller.navigateToHelp,
                ),
                const Divider(height: 1),
                SettingsTile(
                  icon: Icons.info_outline,
                  title: '关于我们',
                  onTap: controller.navigateToAbout,
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 32),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: controller.logout,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                ),
                child: const Text('退出登录'),
              ),
            ),
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }
} 