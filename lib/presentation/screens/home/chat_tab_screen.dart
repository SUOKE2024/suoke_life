import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/router/app_routes.dart';
import '../../../di/providers/health_providers.dart';
import '../../../ai_agents/models/ai_agent.dart';
import '../../widgets/feature_card.dart';
import '../../widgets/agent_assistant_card.dart';

@RoutePage()
class ChatTabScreen extends ConsumerStatefulWidget {
  const ChatTabScreen({super.key});

  @override
  ConsumerState<ChatTabScreen> createState() => _ChatTabScreenState();
}

class _ChatTabScreenState extends ConsumerState<ChatTabScreen> {
  late final PageController _agentPageController;
  int _currentAgentPage = 0;

  @override
  void initState() {
    super.initState();
    _agentPageController = PageController(
      initialPage: _currentAgentPage,
      viewportFraction: 0.85,
    );
  }

  @override
  void dispose() {
    _agentPageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // 模拟获取用户健康评分数据
    final healthScoreAsync = ref.watch(userHealthScoreProvider('current_user'));

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // 自定义APP Bar，带有渐变背景
          _buildAppBar(context),
          
          // 内容区域
          SliverPadding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                const SizedBox(height: 16),
                
                // 健康评分卡片
                healthScoreAsync.when(
                  data: (score) => _buildHealthScoreCard(context, score),
                  loading: () => const Center(child: CircularProgressIndicator()),
                  error: (_, __) => _buildHealthScoreErrorCard(context),
                ),
                const SizedBox(height: 24),
                
                // 构建AI助手轮播
                _buildSectionHeader(context, 'AI助手'),
                const SizedBox(height: 16),
                _buildAgentCarousel(context),
                const SizedBox(height: 24),
                
                // 健康服务特色功能
                _buildSectionHeader(context, '健康服务'),
                const SizedBox(height: 16),
                _buildFeatureGrid(context),
                const SizedBox(height: 24),
                
                // 知识图谱入口
                _buildSectionHeader(context, '知识图谱'),
                const SizedBox(height: 16),
                _buildKnowledgeGraphEntry(context),
                const SizedBox(height: 32),
              ]),
            ),
          ),
        ],
      ),
    );
  }

  // 构建自定义APP Bar
  Widget _buildAppBar(BuildContext context) {
    return SliverAppBar(
      expandedHeight: 120,
      pinned: true,
      flexibleSpace: FlexibleSpaceBar(
        background: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                AppColors.primary,
                AppColors.primary.withOpacity(0.7),
              ],
            ),
          ),
        ),
        title: const Text(
          '索克生活',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 20,
          ),
        ),
        centerTitle: false,
        titlePadding: const EdgeInsets.only(left: 16, bottom: 16),
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.notifications_none),
          onPressed: () {
            // 处理通知按钮点击
          },
        ),
        IconButton(
          icon: const Icon(Icons.search),
          onPressed: () {
            // 跳转到搜索页面
          },
        ),
      ],
    );
  }

  // 构建区块标题
  Widget _buildSectionHeader(BuildContext context, String title) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          title,
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        TextButton(
          onPressed: () {
            // 查看更多
          },
          child: const Text('查看更多'),
        ),
      ],
    );
  }

  // 构建健康评分卡片
  Widget _buildHealthScoreCard(BuildContext context, double score) {
    // 根据分数确定状态文本和颜色
    final (statusText, statusColor) = switch (score) {
      >= 85 => ('优秀', Colors.green),
      >= 70 => ('良好', Colors.blue),
      >= 60 => ('一般', Colors.orange),
      _ => ('需注意', Colors.red),
    };

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  '今日健康评分',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: statusColor.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    statusText,
                    style: TextStyle(
                      color: statusColor,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                // 健康评分圆形进度条
                SizedBox(
                  width: 80,
                  height: 80,
                  child: Stack(
                    children: [
                      CircularProgressIndicator(
                        value: score / 100,
                        strokeWidth: 8,
                        backgroundColor: Colors.grey.shade200,
                        valueColor: AlwaysStoppedAnimation<Color>(statusColor),
                      ),
                      Center(
                        child: Text(
                          score.round().toString(),
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: statusColor,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                // 健康指标列表
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildHealthMetric('睡眠质量', '良好', Icons.nightlight_round),
                      const SizedBox(height: 8),
                      _buildHealthMetric('活动水平', '适中', Icons.directions_run),
                      const SizedBox(height: 8),
                      _buildHealthMetric('饮食平衡', '需改善', Icons.restaurant),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                // 查看详细健康报告
              },
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(double.infinity, 48),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
              child: const Text('查看详细报告'),
            ),
          ],
        ),
      ),
    );
  }

  // 构建健康评分错误卡片
  Widget _buildHealthScoreErrorCard(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '健康评分未能加载',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            const Text('无法获取您的健康数据，请检查网络连接或稍后再试。'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                // 刷新健康数据
                ref.refresh(userHealthScoreProvider('current_user'));
              },
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(double.infinity, 48),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
              child: const Text('重新加载'),
            ),
          ],
        ),
      ),
    );
  }

  // 构建健康指标项
  Widget _buildHealthMetric(String title, String value, IconData icon) {
    final Color color = switch (value) {
      '优秀' => Colors.green,
      '良好' => Colors.blue,
      '适中' => Colors.blue.shade300,
      '一般' => Colors.orange,
      _ => Colors.red,
    };

    return Row(
      children: [
        Icon(icon, size: 16, color: color),
        const SizedBox(width: 8),
        Text(
          title,
          style: TextStyle(
            color: Colors.grey.shade700,
          ),
        ),
        const Spacer(),
        Text(
          value,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }

  // 构建AI助手轮播
  Widget _buildAgentCarousel(BuildContext context) {
    // 模拟AI助手数据
    final List<AIAgent> agents = [
      AIAgent(
        id: '1',
        name: '健康顾问',
        description: '为您提供个性化健康建议',
        avatarUrl: 'assets/images/health_advisor.png',
        capabilities: ['健康评估', '饮食建议', '运动指导'],
        type: AgentType.healthAdvisor,
      ),
      AIAgent(
        id: '2',
        name: '中医辨识',
        description: '基于中医理论的体质辨识',
        avatarUrl: 'assets/images/tcm_advisor.png',
        capabilities: ['体质辨识', '穴位指导', '药膳推荐'],
        type: AgentType.tcmAdvisor,
      ),
      AIAgent(
        id: '3',
        name: '睡眠专家',
        description: '帮助您改善睡眠质量',
        avatarUrl: 'assets/images/sleep_expert.png',
        capabilities: ['睡眠分析', '放松技巧', '环境优化'],
        type: AgentType.sleepExpert,
      ),
    ];

    return Column(
      children: [
        SizedBox(
          height: 180,
          child: PageView.builder(
            controller: _agentPageController,
            itemCount: agents.length,
            onPageChanged: (index) {
              setState(() {
                _currentAgentPage = index;
              });
            },
            itemBuilder: (context, index) {
              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 8),
                child: AgentAssistantCard(
                  agent: agents[index],
                  onTap: () {
                    // 打开与该AI助手的对话
                    _openAgentChat(agents[index]);
                  },
                ),
              );
            },
          ),
        ),
        const SizedBox(height: 16),
        // 页面指示器
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(
            agents.length,
            (index) => Container(
              width: 8,
              height: 8,
              margin: const EdgeInsets.symmetric(horizontal: 4),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: _currentAgentPage == index
                    ? AppColors.primary
                    : Colors.grey.shade300,
              ),
            ),
          ),
        ),
      ],
    );
  }

  // 打开与AI助手的对话
  void _openAgentChat(AIAgent agent) {
    // 在这里处理打开与AI助手的对话逻辑
  }

  // 构建特色功能网格
  Widget _buildFeatureGrid(BuildContext context) {
    // 特色功能列表
    final List<Map<String, dynamic>> features = [
      {
        'title': '健康检测',
        'description': '智能化健康状态评估',
        'icon': Icons.favorite,
        'color': Colors.red,
        'onTap': () {},
      },
      {
        'title': '睡眠优化',
        'description': '改善睡眠质量的建议',
        'icon': Icons.nightlight_round,
        'color': Colors.indigo,
        'onTap': () {},
      },
      {
        'title': '中医养生',
        'description': '传统中医的现代智能应用',
        'icon': Icons.spa,
        'color': Colors.green,
        'onTap': () {},
      },
      {
        'title': '知识库',
        'description': '健康知识和个性化建议',
        'icon': Icons.book,
        'color': Colors.purple,
        'onTap': () => context.router.push(const KnowledgeGraphRoute()),
      },
    ];
    
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 1.5,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
      ),
      itemCount: features.length,
      itemBuilder: (context, index) {
        final feature = features[index];
        return FeatureCard(
          title: feature['title'] as String,
          description: feature['description'] as String,
          icon: feature['icon'] as IconData,
          color: feature['color'] as Color,
          onTap: feature['onTap'] as VoidCallback,
        );
      },
    );
  }
  
  // 构建知识图谱入口
  Widget _buildKnowledgeGraphEntry(BuildContext context) {
    return GestureDetector(
      onTap: () {
        // 导航到知识图谱页面
        context.router.push(const KnowledgeGraphRoute());
      },
      child: Container(
        height: 120,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.purple.shade400,
              Colors.indigo.shade600,
            ],
          ),
        ),
        child: Stack(
          children: [
            // 背景装饰元素
            Positioned(
              right: -20,
              bottom: -20,
              child: Icon(
                Icons.bubble_chart,
                size: 120,
                color: Colors.white.withOpacity(0.2),
              ),
            ),
            // 内容
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text(
                    '知识图谱',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '探索健康知识网络，发现个性化的健康洞见',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.9),
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      const Text(
                        '立即探索',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(width: 4),
                      Icon(
                        Icons.arrow_forward,
                        color: Colors.white,
                        size: 16,
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
} 