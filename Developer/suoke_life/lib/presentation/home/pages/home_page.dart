import 'package:flutter/material.dart';
import 'dart:ui';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/core/router/app_router.dart';
import 'package:suoke_life/presentation/home/widgets/chat_list_item.dart';
import 'package:suoke_life/data/models/agent_model.dart';
import 'package:suoke_life/di/providers/agent_providers.dart';
import 'package:suoke_life/presentation/home/providers/agent_state_provider.dart';

/// 首页（聊天频道）- 显示聊天列表
@RoutePage()
class HomePage extends ConsumerStatefulWidget {
  const HomePage({super.key});

  @override
  ConsumerState<HomePage> createState() => _HomePageState();
}

class _HomePageState extends ConsumerState<HomePage> {
  // 聊天列表
  final List<Map<String, dynamic>> _chatList = [
    {
      'name': '小艾',
      'avatar': 'placeholder',
      'lastMessage': '你好！我是索克AI助手，专注于中医养生和健康生活方式指导。有什么我可以帮助你的吗？',
      'time': '上午 10:23',
      'isAI': true,
      'isGroup': false,
      'unreadCount': 0,
    },
    {
      'name': '老克',
      'avatar': 'placeholder',
      'lastMessage': '近期天气多变，注意保暖。根据您的体质特点，宜多食用温性食物，如羊肉、韭菜、姜等。',
      'time': '昨天',
      'isAI': true,
      'isGroup': false,
      'unreadCount': 2,
    },
    {
      'name': '小克',
      'avatar': 'placeholder',
      'lastMessage': '您的睡眠报告已生成，点击查看详情。',
      'time': '周二',
      'isAI': true,
      'isGroup': false,
      'unreadCount': 0,
    },
    {
      'name': '张医生',
      'avatar': 'placeholder',
      'lastMessage': '您的体质报告显示有轻微阴虚症状，我给您制定了一个调理方案，请查收。',
      'time': '周一',
      'isAI': false,
      'isGroup': false,
      'unreadCount': 1,
    },
    {
      'name': '四季养生群',
      'avatar': 'placeholder',
      'lastMessage': '李医生：立夏已至，养生要点是"养心"，可多食用苦味食物如苦瓜、芹菜等。',
      'time': '5月5日',
      'isAI': false,
      'isGroup': true,
      'unreadCount': 5,
    },
    {
      'name': '营养师李明',
      'avatar': 'placeholder',
      'lastMessage': '根据您的体检报告，建议您增加优质蛋白摄入，每天至少摄入1.5g/kg体重的蛋白质。',
      'time': '4月30日',
      'isAI': false,
      'isGroup': false,
      'unreadCount': 0,
    },
    {
      'name': '中医学习群',
      'avatar': 'placeholder',
      'lastMessage': '王教授：今天讲解《黄帝内经》中关于"正气存内，邪不可干"的理论，欢迎大家讨论。',
      'time': '4月28日',
      'isAI': false,
      'isGroup': true,
      'unreadCount': 0,
    },
  ];

  // 搜索关键词
  final TextEditingController _searchController = TextEditingController();
  bool _isSearching = false;

  @override
  void initState() {
    super.initState();
    // 确保预设智能体已加载
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(agentStateProvider.notifier).loadPresetAgents();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // 获取预设智能体列表
    final presetAgents = ref.watch(presetAgentsProvider);
    
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.background,
      body: Stack(
        children: [
          // 背景装饰
          _buildBackground(),

          // 主内容
          SafeArea(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 顶部导航栏
                _buildAppBar(),

                // 智能体服务部分
                _buildAgentServices(presetAgents),
                
                // 搜索栏
                _buildSearchBar(),

                // 聊天标题
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
                  child: Text(
                    '最近会话',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Theme.of(context).brightness == Brightness.dark
                          ? AppColors.darkTextPrimary
                          : AppColors.lightTextPrimary,
                    ),
                  ),
                ),

                // 聊天列表
                Expanded(
                  child: _buildChatList(),
                ),
              ],
            ),
          ),
        ],
      ),
      // 悬浮按钮 - 新建聊天
      floatingActionButton: _buildFloatingActionButton(),
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
      ],
    );
  }

  /// 构建自定义导航栏
  Widget _buildAppBar() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            '聊天',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: isDarkMode
                  ? AppColors.darkTextPrimary
                  : AppColors.lightTextPrimary,
            ),
          ),
          Row(
            children: [
              // 新的聊天界面按钮
              _buildAppBarButton(
                Icons.chat_bubble,
                () => context.router.pushNamed('/chat'),
              ),

              const SizedBox(width: 12),
              
              // 知识图谱按钮
              _buildAppBarButton(
                Icons.bubble_chart,
                () => context.router.pushNamed('/knowledge-graph'),
              ),

              const SizedBox(width: 12),

              // 新建群聊按钮
              _buildAppBarButton(
                Icons.group_add,
                _createNewGroup,
              ),

              const SizedBox(width: 12),

              // 设置按钮
              _buildAppBarButton(
                Icons.settings,
                _showSettings,
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// 构建导航栏按钮
  Widget _buildAppBarButton(IconData icon, VoidCallback onTap) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return GestureDetector(
      onTap: onTap,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: (isDarkMode ? Colors.white : Colors.black).withAlpha(15),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: (isDarkMode ? Colors.white : Colors.black).withAlpha(30),
                width: 0.5,
              ),
            ),
            child: Icon(
              icon,
              size: 22,
              color: isDarkMode
                  ? AppColors.darkTextPrimary
                  : AppColors.lightTextPrimary,
            ),
          ),
        ),
      ),
    );
  }

  /// 构建智能体服务部分
  Widget _buildAgentServices(List<AgentModel> agents) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
          child: Text(
            '索克智能体',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Theme.of(context).brightness == Brightness.dark
                  ? AppColors.darkTextPrimary
                  : AppColors.lightTextPrimary,
            ),
          ),
        ),
        SizedBox(
          height: 150,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 12),
            itemCount: agents.length,
            itemBuilder: (context, index) {
              final agent = agents[index];
              return _buildAgentServiceCard(agent);
            },
          ),
        ),
      ],
    );
  }

  /// 构建智能体服务卡片
  Widget _buildAgentServiceCard(AgentModel agent) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    
    // 根据不同智能体设置不同的卡片颜色
    Color cardColor;
    switch (agent.id) {
      case 'xiaoke-service':
        cardColor = Colors.blue.shade600;
        break;
      case 'xiaoai-service':
        cardColor = AppColors.primaryColor;
        break;
      case 'soer-service':
        cardColor = Colors.purple.shade600;
        break;
      case 'laoke-service':
        cardColor = Colors.amber.shade800;
        break;
      default:
        cardColor = Colors.grey.shade700;
    }
    
    return GestureDetector(
      onTap: () => _selectAndNavigateToAgent(agent),
      child: Container(
        width: 250,
        margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
        decoration: BoxDecoration(
          color: isDarkMode 
              ? cardColor.withAlpha(50) 
              : cardColor.withAlpha(30),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: cardColor.withAlpha(100),
            width: 1,
          ),
        ),
        child: Stack(
          children: [
            // 卡片内容
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 头像和名称
                  Row(
                    children: [
                      Container(
                        width: 36,
                        height: 36,
                        decoration: BoxDecoration(
                          color: cardColor.withAlpha(80),
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: cardColor,
                            width: 2,
                          ),
                        ),
                        child: ClipOval(
                          child: Center(
                            child: Text(
                              agent.name.substring(0, 1),
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: cardColor,
                              ),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        agent.name,
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: isDarkMode ? Colors.white : Colors.black87,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 6,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: cardColor.withAlpha(80),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Text(
                          agent.type,
                          style: TextStyle(
                            fontSize: 10,
                            color: isDarkMode ? Colors.white70 : Colors.black87,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  // 描述
                  Text(
                    agent.description,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      fontSize: 12,
                      color: isDarkMode ? Colors.white70 : Colors.black54,
                    ),
                  ),
                  const Spacer(),
                  // 开始聊天按钮
                  Align(
                    alignment: Alignment.bottomRight,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: cardColor,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        '开始对话',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.white.withAlpha(240),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 选择智能体并导航到聊天页面
  void _selectAndNavigateToAgent(AgentModel agent) {
    // 更新当前选中的智能体
    ref.read(agentStateProvider.notifier).selectAgent(agent);
    
    // 导航到聊天界面
    context.router.push(
      ChatRoute(
        contactName: agent.name,
        contactAvatar: agent.avatarUrl,
        isAI: true,
      ),
    );
  }

  /// 构建搜索栏
  Widget _buildSearchBar() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Container(
      margin: const EdgeInsets.fromLTRB(16, 8, 16, 16),
      decoration: BoxDecoration(
        color: isDarkMode
            ? Colors.grey.shade800.withAlpha(80)
            : Colors.grey.shade200.withAlpha(80),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: isDarkMode
              ? Colors.white.withAlpha(20)
              : Colors.grey.withAlpha(50),
          width: 0.5,
        ),
      ),
      child: TextField(
        controller: _searchController,
        onChanged: (value) {
          setState(() {
            _isSearching = value.isNotEmpty;
          });
        },
        decoration: InputDecoration(
          hintText: '搜索',
          hintStyle: TextStyle(
            color: isDarkMode
                ? Colors.grey.withAlpha(150)
                : Colors.grey.withAlpha(180),
          ),
          prefixIcon: Icon(
            Icons.search,
            color: isDarkMode
                ? Colors.grey.withAlpha(150)
                : Colors.grey.withAlpha(180),
          ),
          suffixIcon: _isSearching
              ? IconButton(
                  icon: Icon(
                    Icons.clear,
                    color: isDarkMode
                        ? Colors.grey.withAlpha(150)
                        : Colors.grey.withAlpha(180),
                  ),
                  onPressed: () {
                    _searchController.clear();
                    setState(() {
                      _isSearching = false;
                    });
                  },
                )
              : null,
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(vertical: 12),
        ),
      ),
    );
  }

  /// 构建聊天列表
  Widget _buildChatList() {
    final filteredList = _isSearching
        ? _chatList
            .where((chat) =>
                chat['name']
                    .toLowerCase()
                    .contains(_searchController.text.toLowerCase()) ||
                chat['lastMessage']
                    .toLowerCase()
                    .contains(_searchController.text.toLowerCase()))
            .toList()
        : _chatList;

    if (filteredList.isEmpty && _isSearching) {
      return _buildEmptySearchResult();
    }

    return ListView.separated(
      padding: const EdgeInsets.only(bottom: 16),
      itemCount: filteredList.length,
      separatorBuilder: (context, index) => const Divider(
        height: 1,
        indent: 80,
        endIndent: 16,
      ),
      itemBuilder: (context, index) {
        final chat = filteredList[index];
        return ChatListItem(
          name: chat['name'],
          avatar: chat['avatar'],
          lastMessage: chat['lastMessage'],
          time: chat['time'],
          isAI: chat['isAI'],
          isGroup: chat['isGroup'],
          onTap: () => _navigateToChat(chat),
        );
      },
    );
  }

  /// 构建空搜索结果视图
  Widget _buildEmptySearchResult() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.search_off,
            size: 64,
            color: Colors.grey.withAlpha(120),
          ),
          const SizedBox(height: 16),
          Text(
            '未找到匹配的聊天',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey.withAlpha(180),
            ),
          ),
        ],
      ),
    );
  }

  /// 构建悬浮按钮
  Widget _buildFloatingActionButton() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // API测试入口
        Padding(
          padding: const EdgeInsets.only(bottom: 16.0),
          child: FloatingActionButton.small(
            heroTag: 'api_test_fab',
            onPressed: () {
              context.router.push(const ApiTestRoute());
            },
            backgroundColor: Colors.orange,
            child: const Icon(Icons.api),
          ),
        ),
        // 新建聊天按钮
        FloatingActionButton(
          onPressed: () {
            context.router.push(const ChatRoute());
          },
          backgroundColor: AppColors.primaryColor,
          child: const Icon(Icons.add),
        ),
      ],
    );
  }

  /// 导航到聊天页面
  void _navigateToChat(Map<String, dynamic> chat) {
    context.router.push(
      ChatRoute(
        contactName: chat['name'],
        contactAvatar: chat['avatar'],
        isAI: chat['isAI'],
      ),
    );
  }

  /// 显示新建聊天选项
  void _showNewChatOptions() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        padding: const EdgeInsets.symmetric(vertical: 24),
        decoration: BoxDecoration(
          color: isDarkMode ? Colors.grey.shade900 : Colors.white,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildNewChatOption(
              icon: Icons.psychology,
              title: '新建AI会话',
              subtitle: '与AI助手开始一段新对话',
              onTap: _createNewAIChat,
            ),
            _buildNewChatOption(
              icon: Icons.person_add,
              title: '添加联系人',
              subtitle: '添加新的联系人或好友',
              onTap: _addNewContact,
            ),
            _buildNewChatOption(
              icon: Icons.group_add,
              title: '创建群聊',
              subtitle: '创建新的群聊对话',
              onTap: _createNewGroup,
            ),
          ],
        ),
      ),
    );
  }

  /// 构建新建聊天选项项
  Widget _buildNewChatOption({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: AppColors.primaryColor.withAlpha(30),
          shape: BoxShape.circle,
        ),
        child: Icon(
          icon,
          color: AppColors.primaryColor,
        ),
      ),
      title: Text(
        title,
        style: TextStyle(
          fontWeight: FontWeight.bold,
          color: isDarkMode ? Colors.white : Colors.black,
        ),
      ),
      subtitle: Text(
        subtitle,
        style: TextStyle(
          color: isDarkMode ? Colors.grey.shade400 : Colors.grey.shade700,
        ),
      ),
      onTap: () {
        Navigator.pop(context);
        onTap();
      },
    );
  }

  /// 创建新的AI聊天
  void _createNewAIChat() {
    // TODO: 实现创建新的AI聊天功能
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('创建新的AI聊天功能开发中...'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  /// 添加新联系人
  void _addNewContact() {
    // TODO: 实现添加新联系人功能
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('添加新联系人功能开发中...'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  /// 创建新群聊
  void _createNewGroup() {
    // TODO: 实现创建新群聊功能
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('创建新群聊功能开发中...'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  /// 显示设置
  void _showSettings() {
    // TODO: 实现显示设置功能
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('设置功能开发中...'),
        duration: Duration(seconds: 2),
      ),
    );
  }
}
