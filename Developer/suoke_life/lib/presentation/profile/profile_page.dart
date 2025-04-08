import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/core/router/app_router.dart';
import 'package:suoke_life/core/widgets/app_widgets.dart';

@RoutePage()
class ProfilePage extends ConsumerWidget {
  const ProfilePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('我的'),
        elevation: 0,
      ),
      body: ListView(
        children: [
          _buildUserInfoSection(context),
          const Divider(),
          _buildSettingsSection(context),
        ],
      ),
    );
  }

  Widget _buildUserInfoSection(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Row(
        children: [
          CircleAvatar(
            radius: 40,
            backgroundColor: Theme.of(context).colorScheme.primary,
            child: const Text(
              '索',
              style: TextStyle(fontSize: 32, color: Colors.white),
            ),
          ),
          const SizedBox(width: 16),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '索克用户',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 4),
              Text(
                '健康生活，从现在开始',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            ],
          ),
          const Spacer(),
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () {
              // 编辑个人资料
            },
          ),
        ],
      ),
    );
  }

  Widget _buildSettingsSection(BuildContext context) {
    return Column(
      children: [
        ListTile(
          leading: const Icon(Icons.sensors, color: Colors.green),
          title: const Text('传感器与数据采集'),
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () {
            // 暂时注释掉路由跳转，直到SensingControlRoute正确定义
            // context.router.push(const SensingControlRoute());
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('传感器控制页面暂未实现')),
            );
          },
        ),
        ListTile(
          leading: const Icon(Icons.person, color: Colors.blue),
          title: const Text('个人信息'),
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () {
            // 导航到个人信息页面
          },
        ),
        ListTile(
          leading: const Icon(Icons.color_lens, color: Colors.purple),
          title: const Text('主题设置'),
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () {
            // 导航到主题设置页面
          },
        ),
        ListTile(
          leading: const Icon(Icons.settings, color: Colors.grey),
          title: const Text('应用设置'),
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () {
            // 导航到应用设置页面
          },
        ),
        ListTile(
          leading: const Icon(Icons.info, color: Colors.amber),
          title: const Text('关于索克生活'),
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () {
            // 显示关于信息
          },
        ),
      ],
    );
  }
}
