import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import 'package:suoke_life/core/router/app_router.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/core/widgets/app_widgets.dart' as app_widgets;
import 'dart:ui';

/// 个人资料页面（我的频道）
@RoutePage()
class ProfilePage extends ConsumerStatefulWidget {
  const ProfilePage({super.key});

  @override
  ConsumerState<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends ConsumerState<ProfilePage> {
  // 用户信息
  final Map<String, dynamic> _userInfo = {
    'name': '张三',
    'avatar':
        'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1080&q=80',
    'level': '普通会员',
    'points': 580,
    'registrationDate': '2023年5月15日',
  };

  // 设置项列表
  final List<Map<String, dynamic>> _settingsList = [
    {
      'title': '个人信息',
      'icon': Icons.person,
      'color': Color(0xFF35BB78),
    },
    {
      'title': '账号安全',
      'icon': Icons.lock,
      'color': Color(0xFF6A88E5),
    },
    {
      'title': '隐私设置',
      'icon': Icons.visibility,
      'color': Color(0xFF9E7FDE),
    },
    {
      'title': '通知设置',
      'icon': Icons.notifications,
      'color': Color(0xFFFF6800),
    },
    {
      'title': '主题设置',
      'icon': Icons.color_lens,
      'color': Color(0xFF424242),
    },
    {
      'title': '设计系统',
      'icon': Icons.palette,
      'color': Color(0xFF00BCD4),
    },
    {
      'title': '关于我们',
      'icon': Icons.info,
      'color': Color(0xFF607D8B),
    },
    {
      'title': '帮助中心',
      'icon': Icons.help,
      'color': Color(0xFF03A9F4),
    },
  ];

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.background,
      body: Stack(
        children: [
          // 背景装饰
          Positioned.fill(
            child: _buildBackground(),
          ),

          // 内容
          SafeArea(
            child: CustomScrollView(
              slivers: [
                // 个人资料头部
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: _buildProfileHeader(),
                  ),
                ),

                // 统计信息卡片
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16.0),
                    child: _buildStatsCard(),
                  ),
                ),

                // 设置标题
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Text(
                      '设置',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: isDarkMode
                                ? AppColors.darkTextPrimary
                                : AppColors.lightTextPrimary,
                          ),
                    ),
                  ),
                ),

                // 设置列表
                SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (context, index) {
                      final setting = _settingsList[index];
                      return Padding(
                        padding: const EdgeInsets.only(
                            left: 16, right: 16, bottom: 12),
                        child: _buildSettingCard(setting),
                      );
                    },
                    childCount: _settingsList.length,
                  ),
                ),

                // 退出登录按钮
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: _buildLogoutButton(),
                  ),
                ),

                // 底部留白
                const SliverToBoxAdapter(
                  child: SizedBox(height: 32),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 构建背景装饰
  Widget _buildBackground() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Stack(
      children: [
        // 顶部装饰圆形
        Positioned(
          top: -100,
          right: -100,
          child: Container(
            width: 300,
            height: 300,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: AppColors.primaryColor.withAlpha(isDarkMode ? 50 : 30),
            ),
          ),
        ),

        // 底部装饰圆形
        Positioned(
          bottom: -150,
          left: -80,
          child: Container(
            width: 350,
            height: 350,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: AppColors.secondaryColor.withAlpha(isDarkMode ? 50 : 30),
            ),
          ),
        ),
      ],
    );
  }

  /// 构建个人资料头部
  Widget _buildProfileHeader() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return app_widgets.BasicCard(
      height: 130,
      content: Row(
        children: [
          // 头像
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(
                color: AppColors.primaryColor,
                width: 2,
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withAlpha(20),
                  blurRadius: 10,
                  offset: const Offset(0, 5),
                ),
              ],
              image: DecorationImage(
                image: NetworkImage(_userInfo['avatar']),
                fit: BoxFit.cover,
              ),
            ),
          ),

          const SizedBox(width: 16),

          // 用户信息
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  _userInfo['name'],
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: isDarkMode
                        ? AppColors.darkTextPrimary
                        : AppColors.lightTextPrimary,
                  ),
                ),

                const SizedBox(height: 4),

                // 会员等级标签
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: AppColors.primaryColor.withAlpha(30),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    _userInfo['level'],
                    style: TextStyle(
                      color: AppColors.primaryColor,
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),

                const SizedBox(height: 8),

                Text(
                  '注册时间: ${_userInfo['registrationDate']}',
                  style: TextStyle(
                    color: isDarkMode
                        ? AppColors.darkTextSecondary
                        : AppColors.lightTextSecondary,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),

          // 编辑按钮
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: AppColors.primaryColor.withAlpha(30),
              borderRadius: BorderRadius.circular(12),
            ),
            child: IconButton(
              icon: Icon(
                Icons.edit,
                color: AppColors.primaryColor,
                size: 20,
              ),
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('编辑个人资料功能正在开发中')),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  /// 构建统计卡片
  Widget _buildStatsCard() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return app_widgets.BasicCard(
      title: '我的数据',
      height: 120,
      content: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildStatItem('积分', '${_userInfo['points']}'),
          _buildStatItem('优惠券', '3张'),
          _buildStatItem('收藏', '12'),
          _buildStatItem('关注', '5'),
        ],
      ),
    );
  }

  /// 构建统计项
  Widget _buildStatItem(String title, String value) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: isDarkMode
                ? AppColors.darkTextPrimary
                : AppColors.lightTextPrimary,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          title,
          style: TextStyle(
            fontSize: 13,
            color: isDarkMode
                ? AppColors.darkTextSecondary
                : AppColors.lightTextSecondary,
          ),
        ),
      ],
    );
  }

  /// 构建设置卡片
  Widget _buildSettingCard(Map<String, dynamic> setting) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final isSwitch = setting['isSwitch'] == true;

    // 处理点击事件
    void Function()? onTapHandler;
    if (setting['title'] == '主题设置') {
      onTapHandler = () => context.router.push(const ThemeSettingsRoute());
    } else if (setting['title'] == '设计系统') {
      onTapHandler =
          () => context.router.push(const DesignSystemShowcaseRoute());
    } else if (!isSwitch) {
      onTapHandler = () {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('${setting['title']}功能正在开发中')),
        );
      };
    }

    return app_widgets.BasicCard(
      title: setting['title'],
      leadingIcon: setting['icon'],
      onTap: onTapHandler,
      content: Row(
        children: [
          // 图标容器
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: setting['color'].withAlpha(isDarkMode ? 40 : 20),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              setting['icon'],
              color: setting['color'],
              size: 20,
            ),
          ),

          const SizedBox(width: 16),

          // 标题
          Expanded(
            child: Text(
              setting['title'],
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w500,
                color: isDarkMode
                    ? AppColors.darkTextPrimary
                    : AppColors.lightTextPrimary,
              ),
            ),
          ),

          // 开关或箭头
          isSwitch
              ? Switch(
                  value: isDarkMode,
                  onChanged: (value) {
                    // 切换主题
                    // TODO: 实现主题切换逻辑
                  },
                  activeColor: AppColors.primaryColor,
                )
              : Icon(
                  Icons.arrow_forward_ios,
                  size: 16,
                  color: isDarkMode
                      ? AppColors.darkTextSecondary
                      : AppColors.lightTextSecondary,
                ),
        ],
      ),
    );
  }

  /// 构建退出登录按钮
  Widget _buildLogoutButton() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(10),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 5, sigmaY: 5),
          child: Container(
            decoration: BoxDecoration(
              color: Colors.red.withAlpha(isDarkMode ? 40 : 20),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: Colors.red.withAlpha(50),
                width: 0.5,
              ),
            ),
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                borderRadius: BorderRadius.circular(16),
                onTap: _showLogoutDialog,
                child: Container(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  alignment: Alignment.center,
                  child: const Text(
                    '退出登录',
                    style: TextStyle(
                      color: Colors.red,
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// 显示退出登录对话框
  void _showLogoutDialog() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    showDialog(
      context: context,
      builder: (context) {
        return BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 5, sigmaY: 5),
          child: AlertDialog(
            backgroundColor: isDarkMode
                ? Colors.grey.shade900.withAlpha(220)
                : Colors.white.withAlpha(230),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(20),
            ),
            title: const Text('确认退出'),
            content: const Text('您确定要退出登录吗？'),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.pop(context);
                },
                child: const Text('取消'),
              ),
              ElevatedButton(
                onPressed: () {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('已退出登录')),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                ),
                child: const Text('确认退出'),
              ),
            ],
          ),
        );
      },
    );
  }

  /// 构建系统设置部分
  Widget _buildSystemSettings() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 标题
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Text(
            '系统设置',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Theme.of(context).brightness == Brightness.dark
                  ? AppColors.darkTextPrimary
                  : AppColors.lightTextSecondary,
            ),
          ),
        ),

        // 设置项列表
        Card(
          elevation: 0,
          margin: const EdgeInsets.all(8),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            children: [
              // 暗色模式
              _buildSettingItem(
                context: context,
                setting: {
                  'icon': Icons.dark_mode,
                  'title': '暗色模式',
                  'isSwitch': true,
                },
                onTap: () {},
              ),

              // 隐私设置
              _buildSettingItem(
                context: context,
                setting: {
                  'icon': Icons.privacy_tip,
                  'title': '隐私设置',
                  'isSwitch': false,
                },
                onTap: () {},
              ),

              // 语言设置
              _buildSettingItem(
                context: context,
                setting: {
                  'icon': Icons.language,
                  'title': '语言设置',
                  'isSwitch': false,
                },
                onTap: () {},
              ),

              // 网络测试
              _buildSettingItem(
                context: context,
                setting: {
                  'icon': Icons.network_check,
                  'title': '网络连接测试',
                  'isSwitch': false,
                },
                onTap: () {
                  // 导航到网络测试页面
                  context.router.push(const NetworkTestRoute());
                },
              ),

              // 关于我们
              _buildSettingItem(
                context: context,
                setting: {
                  'icon': Icons.info,
                  'title': '关于我们',
                  'isSwitch': false,
                },
                onTap: () {},
              ),
            ],
          ),
        ),
      ],
    );
  }

  /// 构建设置项
  Widget _buildSettingItem({
    required BuildContext context,
    required Map<String, dynamic> setting,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Icon(setting['icon']),
      title: Text(setting['title']),
      onTap: onTap,
    );
  }
}
