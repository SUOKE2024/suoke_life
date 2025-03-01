import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/app_colors.dart';
import '../../../ai_agents/models/ai_agent.dart';

@RoutePage()
class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  // 用户信息
  final Map<String, dynamic> _userInfo = {
    'name': '用户123456',
    'avatarUrl': 'assets/images/default_avatar.png',
    'points': 1280,
    'level': 5,
    'memberExpiry': '2024-12-31',
    'memberType': '高级会员',
  };

  // 设置项目列表
  final List<Map<String, dynamic>> _settingGroups = [
    {
      'title': '账户安全',
      'items': [
        {
          'title': '个人信息',
          'icon': Icons.person,
          'color': AppColors.primaryColor,
        },
        {
          'title': '账号与安全',
          'icon': Icons.security,
          'color': AppColors.warningColor,
        },
        {
          'title': '隐私设置',
          'icon': Icons.privacy_tip,
          'color': AppColors.errorColor,
        },
      ],
    },
    {
      'title': '应用服务',
      'items': [
        {
          'title': '设备管理',
          'icon': Icons.devices,
          'color': AppColors.accentColor,
        },
        {
          'title': '健康应用数据共享',
          'icon': Icons.health_and_safety,
          'color': AppColors.healthGood,
        },
        {
          'title': '地方语言识别',
          'icon': Icons.translate,
          'color': AppColors.successColor,
        },
        {
          'title': '多模型集成设置',
          'icon': Icons.psychology,
          'color': AppColors.aiXiaoai,
        },
        {
          'title': '头像库',
          'icon': Icons.face,
          'color': AppColors.aiLaoke,
        },
        {
          'title': '表情库',
          'icon': Icons.emoji_emotions,
          'color': AppColors.aiXiaoke,
        },
      ],
    },
    {
      'title': '管理员',
      'items': [
        {
          'title': '微服务管理',
          'icon': Icons.cloud,
          'color': Colors.blueGrey,
        },
        {
          'title': '专家审核',
          'icon': Icons.verified_user,
          'color': Colors.indigoAccent,
        },
        {
          'title': '服务审核',
          'icon': Icons.miscellaneous_services,
          'color': Colors.deepPurpleAccent,
        },
        {
          'title': '产品审核',
          'icon': Icons.inventory,
          'color': Colors.teal,
        },
      ],
    },
    {
      'title': '大模型集成',
      'items': [
        {
          'title': 'Deepseek',
          'icon': Icons.smart_toy,
          'color': Colors.deepPurple,
          'isActivated': true,
        },
        {
          'title': 'GPT-4',
          'icon': Icons.smart_toy,
          'color': Colors.green,
          'isActivated': true,
        },
        {
          'title': 'Claude',
          'icon': Icons.smart_toy,
          'color': Colors.amber,
          'isActivated': false,
        },
        {
          'title': 'LLaMA',
          'icon': Icons.smart_toy,
          'color': Colors.red,
          'isActivated': true,
        },
      ],
    },
    {
      'title': '其他设置',
      'items': [
        {
          'title': '通用',
          'icon': Icons.settings,
          'color': Colors.grey,
        },
        {
          'title': '关于',
          'icon': Icons.info,
          'color': AppColors.primaryColor,
        },
        {
          'title': '退出登录',
          'icon': Icons.logout,
          'color': AppColors.errorColor,
        },
      ],
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('我的'),
        actions: [
          IconButton(
            icon: const Icon(Icons.qr_code),
            onPressed: () {
              // 显示二维码
              _showQRCodeDialog();
            },
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              // 滚动到设置部分
              // 实际应用中应该使用ScrollController实现
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('设置选项已在页面下方')),
              );
            },
          ),
        ],
      ),
      body: ListView(
        children: [
          // 用户信息卡片
          _buildUserInfoCard(),
          
          // 设置项目
          ..._buildSettingGroups(),
          
          // 底部版本信息
          const SizedBox(height: 16),
          Center(
            child: Text(
              'v1.0.0',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey.shade500,
              ),
            ),
          ),
          const SizedBox(height: 32),
        ],
      ),
      // AI代理气泡
      floatingActionButton: FloatingActionButton(
        backgroundColor: AppColors.aiXiaoke.withOpacity(0.9),
        onPressed: () {
          // 进入与小克的多模态自然交互界面
          _showAIAgentDialog();
        },
        child: CircleAvatar(
          radius: 20,
          backgroundColor: Colors.transparent,
          backgroundImage: AssetImage(AIAgent.xiaoke.avatarUrl),
        ),
      ),
    );
  }
  
  // 构建用户信息卡片
  Widget _buildUserInfoCard() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Card(
        elevation: 3,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              // 头像和用户名
              Row(
                children: [
                  // 头像
                  GestureDetector(
                    onTap: () {
                      // 查看/修改头像
                      _showEditProfileDialog();
                    },
                    child: Stack(
                      children: [
                        CircleAvatar(
                          radius: 40,
                          backgroundColor: Colors.grey.shade200,
                          child: Icon(
                            Icons.person,
                            size: 40,
                            color: Colors.grey.shade400,
                          ),
                        ),
                        Positioned(
                          right: 0,
                          bottom: 0,
                          child: Container(
                            padding: const EdgeInsets.all(4),
                            decoration: BoxDecoration(
                              color: AppColors.primaryColor,
                              shape: BoxShape.circle,
                              border: Border.all(
                                color: Colors.white,
                                width: 2,
                              ),
                            ),
                            child: const Icon(
                              Icons.edit,
                              size: 14,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  const SizedBox(width: 16),
                  
                  // 用户名和会员信息
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Text(
                              _userInfo['name'] as String,
                              style: const TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            
                            const SizedBox(width: 8),
                            
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 6,
                                vertical: 2,
                              ),
                              decoration: BoxDecoration(
                                color: AppColors.primaryColor.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(
                                    Icons.verified,
                                    size: 14,
                                    color: AppColors.primaryColor,
                                  ),
                                  const SizedBox(width: 2),
                                  Text(
                                    'Lv${_userInfo['level']}',
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: AppColors.primaryColor,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                        
                        const SizedBox(height: 8),
                        
                        // 会员信息
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 6,
                                vertical: 2,
                              ),
                              decoration: BoxDecoration(
                                gradient: LinearGradient(
                                  colors: [
                                    Colors.amber.shade700,
                                    Colors.amber.shade300,
                                  ],
                                ),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  const Icon(
                                    Icons.star,
                                    size: 14,
                                    color: Colors.white,
                                  ),
                                  const SizedBox(width: 2),
                                  Text(
                                    _userInfo['memberType'] as String,
                                    style: const TextStyle(
                                      fontSize: 12,
                                      color: Colors.white,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            
                            const SizedBox(width: 8),
                            
                            Text(
                              '到期：${_userInfo['memberExpiry']}',
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey.shade600,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 16),
              
              // 分割线
              Divider(color: Colors.grey.shade200),
              
              const SizedBox(height: 16),
              
              // 积分和钱包
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildUserInfoItem(
                    icon: Icons.workspace_premium,
                    title: '积分',
                    value: '${_userInfo['points']}',
                    color: Colors.amber,
                  ),
                  _buildUserInfoItem(
                    icon: Icons.card_giftcard,
                    title: '奖励',
                    value: '3',
                    color: AppColors.successColor,
                  ),
                  _buildUserInfoItem(
                    icon: Icons.account_balance_wallet,
                    title: '钱包',
                    value: '¥0.00',
                    color: AppColors.primaryColor,
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  // 构建用户信息项
  Widget _buildUserInfoItem({
    required IconData icon,
    required String title,
    required String value,
    required Color color,
  }) {
    return GestureDetector(
      onTap: () {
        // 点击对应项目
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('$title功能暂未实现')),
        );
      },
      child: Column(
        children: [
          Icon(
            icon,
            color: color,
            size: 24,
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            title,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey.shade600,
            ),
          ),
        ],
      ),
    );
  }
  
  // 构建设置组
  List<Widget> _buildSettingGroups() {
    final List<Widget> groups = [];
    
    for (final group in _settingGroups) {
      groups.add(
        Padding(
          padding: const EdgeInsets.only(left: 16, right: 16, top: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 组标题
              Text(
                group['title'] as String,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              
              const SizedBox(height: 8),
              
              // 设置项目卡片
              Card(
                elevation: 2,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: ListView.separated(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: (group['items'] as List).length,
                  separatorBuilder: (context, index) => Divider(
                    height: 1,
                    indent: 56,
                    color: Colors.grey.shade200,
                  ),
                  itemBuilder: (context, index) {
                    final item = (group['items'] as List)[index];
                    
                    return _buildSettingItem(
                      title: item['title'] as String,
                      icon: item['icon'] as IconData,
                      color: item['color'] as Color,
                      isActivated: item['isActivated'] as bool? ?? false,
                      showToggle: item.containsKey('isActivated'),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      );
    }
    
    return groups;
  }
  
  // 构建设置项
  Widget _buildSettingItem({
    required String title,
    required IconData icon,
    required Color color,
    bool isActivated = false,
    bool showToggle = false,
  }) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          shape: BoxShape.circle,
        ),
        child: Icon(
          icon,
          color: color,
          size: 24,
        ),
      ),
      title: Text(title),
      trailing: showToggle
          ? Switch(
              value: isActivated,
              activeColor: AppColors.primaryColor,
              onChanged: (value) {
                setState(() {
                  // 在实际应用中，应该更新模型状态
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(
                        value ? '已启用 $title' : '已禁用 $title',
                      ),
                    ),
                  );
                });
              },
            )
          : Icon(
              Icons.arrow_forward_ios,
              size: 16,
              color: Colors.grey.shade400,
            ),
      onTap: () {
        if (!showToggle) {
          if (title == '退出登录') {
            _showLogoutConfirmDialog();
          } else {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('$title功能暂未实现')),
            );
          }
        }
      },
    );
  }
  
  // 显示二维码对话框
  void _showQRCodeDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return Dialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  '我的二维码',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                
                const SizedBox(height: 16),
                
                // 二维码占位
                Container(
                  width: 200,
                  height: 200,
                  decoration: BoxDecoration(
                    border: Border.all(
                      color: Colors.grey.shade300,
                    ),
                  ),
                  child: Center(
                    child: Icon(
                      Icons.qr_code,
                      size: 100,
                      color: Colors.grey.shade400,
                    ),
                  ),
                ),
                
                const SizedBox(height: 16),
                
                Text(
                  _userInfo['name'] as String,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                
                const SizedBox(height: 4),
                
                Text(
                  '扫一扫上面的二维码，添加我为好友',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey.shade600,
                  ),
                ),
                
                const SizedBox(height: 24),
                
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    ElevatedButton.icon(
                      icon: const Icon(Icons.save_alt),
                      label: const Text('保存图片'),
                      onPressed: () {
                        Navigator.pop(context);
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('保存图片功能暂未实现'),
                          ),
                        );
                      },
                    ),
                    
                    ElevatedButton.icon(
                      icon: const Icon(Icons.share),
                      label: const Text('分享'),
                      onPressed: () {
                        Navigator.pop(context);
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('分享功能暂未实现'),
                          ),
                        );
                      },
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }
  
  // 显示编辑个人资料对话框
  void _showEditProfileDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return Dialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  '编辑个人资料',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                
                const SizedBox(height: 24),
                
                // 头像选择
                GestureDetector(
                  onTap: () {
                    // 修改头像
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('修改头像功能暂未实现'),
                      ),
                    );
                  },
                  child: Stack(
                    children: [
                      CircleAvatar(
                        radius: 50,
                        backgroundColor: Colors.grey.shade200,
                        child: Icon(
                          Icons.person,
                          size: 50,
                          color: Colors.grey.shade400,
                        ),
                      ),
                      Positioned(
                        right: 0,
                        bottom: 0,
                        child: Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: AppColors.primaryColor,
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: Colors.white,
                              width: 2,
                            ),
                          ),
                          child: const Icon(
                            Icons.camera_alt,
                            size: 20,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 24),
                
                // 昵称输入
                TextField(
                  decoration: const InputDecoration(
                    labelText: '昵称',
                    hintText: '请输入昵称',
                    prefixIcon: Icon(Icons.person),
                  ),
                  controller: TextEditingController(text: _userInfo['name'] as String),
                ),
                
                const SizedBox(height: 16),
                
                // 性别选择
                Row(
                  children: [
                    const Icon(
                      Icons.wc,
                      color: Colors.grey,
                    ),
                    
                    const SizedBox(width: 16),
                    
                    Expanded(
                      child: Row(
                        children: [
                          Radio<String>(
                            value: '男',
                            groupValue: '男',
                            onChanged: (value) {},
                          ),
                          const Text('男'),
                          
                          const SizedBox(width: 16),
                          
                          Radio<String>(
                            value: '女',
                            groupValue: '男',
                            onChanged: (value) {},
                          ),
                          const Text('女'),
                        ],
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 16),
                
                // 生日选择
                Row(
                  children: [
                    const Icon(
                      Icons.cake,
                      color: Colors.grey,
                    ),
                    
                    const SizedBox(width: 16),
                    
                    Expanded(
                      child: GestureDetector(
                        onTap: () {
                          // 选择生日
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('生日选择功能暂未实现'),
                            ),
                          );
                        },
                        child: Row(
                          children: [
                            const Text('出生日期'),
                            const Spacer(),
                            Text(
                              '1990-01-01',
                              style: TextStyle(
                                color: Colors.grey.shade600,
                              ),
                            ),
                            Icon(
                              Icons.arrow_forward_ios,
                              size: 16,
                              color: Colors.grey.shade400,
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 24),
                
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    TextButton(
                      onPressed: () {
                        Navigator.pop(context);
                      },
                      child: const Text('取消'),
                    ),
                    
                    const SizedBox(width: 16),
                    
                    ElevatedButton(
                      onPressed: () {
                        Navigator.pop(context);
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('个人资料已更新'),
                          ),
                        );
                      },
                      child: const Text('保存'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }
  
  // 显示AI代理对话框
  void _showAIAgentDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          contentPadding: EdgeInsets.zero,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // AI代理头部
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.aiXiaoke.withOpacity(0.1),
                  borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(16),
                    topRight: Radius.circular(16),
                  ),
                ),
                child: Row(
                  children: [
                    // AI头像
                    CircleAvatar(
                      radius: 24,
                      backgroundImage: AssetImage(AIAgent.xiaoke.avatarUrl),
                    ),
                    
                    const SizedBox(width: 16),
                    
                    // AI名称和描述
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            AIAgent.xiaoke.name,
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          
                          Text(
                            AIAgent.xiaoke.description,
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey.shade700,
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              
              // 对话内容
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    // AI消息气泡
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.grey.shade100,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Text(
                        '你好！我是小克，有什么可以帮到你的？',
                        style: TextStyle(fontSize: 16),
                      ),
                    ),
                    
                    const SizedBox(height: 16),
                    
                    // 快捷回复按钮
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        _buildQuickReplyChip('账户设置帮助'),
                        _buildQuickReplyChip('隐私问题'),
                        _buildQuickReplyChip('会员续费'),
                      ],
                    ),
                  ],
                ),
              ),
              
              // 底部输入框
              Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        decoration: InputDecoration(
                          hintText: '输入消息...',
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(24),
                            borderSide: BorderSide.none,
                          ),
                          filled: true,
                          fillColor: Colors.grey.shade200,
                          contentPadding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 8,
                          ),
                        ),
                      ),
                    ),
                    
                    const SizedBox(width: 8),
                    
                    CircleAvatar(
                      radius: 20,
                      backgroundColor: AppColors.primaryColor,
                      child: const Icon(
                        Icons.send,
                        color: Colors.white,
                        size: 18,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
  
  // 构建快捷回复芯片
  Widget _buildQuickReplyChip(String text) {
    return InkWell(
      onTap: () {
        // 处理快捷回复
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('回复"$text"功能暂未实现')),
        );
      },
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: 12,
          vertical: 8,
        ),
        decoration: BoxDecoration(
          color: AppColors.primaryColor.withOpacity(0.1),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: AppColors.primaryColor.withOpacity(0.3),
          ),
        ),
        child: Text(
          text,
          style: TextStyle(
            fontSize: 14,
            color: AppColors.primaryColor,
          ),
        ),
      ),
    );
  }
  
  // 显示退出登录确认对话框
  void _showLogoutConfirmDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('确认退出'),
          content: const Text('确定要退出登录吗？'),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context);
              },
              child: const Text('取消'),
            ),
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('退出登录功能暂未实现'),
                  ),
                );
              },
              child: const Text('确定'),
            ),
          ],
        );
      },
    );
  }
} 