import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/app_colors.dart';
import '../../../di/providers/user_providers.dart';
import '../../widgets/agent_grid_item.dart';

/// SUOKE服务频道页面
/// 超级代理生态系统的中心页面，展示所有可用的代理和功能分类
@RoutePage()
class SuokeScreen extends ConsumerStatefulWidget {
  const SuokeScreen({super.key});

  @override
  ConsumerState<SuokeScreen> createState() => _SuokeScreenState();
}

class _SuokeScreenState extends ConsumerState<SuokeScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 5, vsync: this);
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    // 用户信息（用于个性化内容）
    final userAsyncValue = ref.watch(currentUserProvider);
    
    return Scaffold(
      body: NestedScrollView(
        headerSliverBuilder: (context, innerBoxIsScrolled) {
          return <Widget>[
            SliverAppBar(
              expandedHeight: 180.0,
              floating: false,
              pinned: true,
              backgroundColor: AppColors.primaryColor,
              flexibleSpace: FlexibleSpaceBar(
                title: const Text(
                  'SUOKE 超级代理',
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                background: Stack(
                  fit: StackFit.expand,
                  children: [
                    // 渐变背景
                    Container(
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [
                            AppColors.primaryColor,
                            AppColors.primaryColor.withOpacity(0.7),
                          ],
                        ),
                      ),
                    ),
                    // 装饰元素
                    Positioned(
                      right: -50,
                      bottom: -50,
                      child: Icon(
                        Icons.hub,
                        size: 200,
                        color: Colors.white.withOpacity(0.1),
                      ),
                    ),
                    // 内容
                    Positioned(
                      left: 16,
                      bottom: 60,
                      child: userAsyncValue.when(
                        data: (user) => Text(
                          '欢迎回来，${user?.username ?? '用户'}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                          ),
                        ),
                        loading: () => const CircularProgressIndicator(
                          color: Colors.white,
                        ),
                        error: (_, __) => const Text(
                          '欢迎来到超级代理生态系统',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              actions: [
                IconButton(
                  icon: const Icon(Icons.search, color: Colors.white),
                  onPressed: () {
                    // 打开代理搜索
                  },
                ),
                IconButton(
                  icon: const Icon(Icons.filter_list, color: Colors.white),
                  onPressed: () {
                    // 打开筛选选项
                  },
                ),
              ],
              bottom: TabBar(
                controller: _tabController,
                indicatorColor: Colors.white,
                indicatorWeight: 3,
                isScrollable: true,
                tabs: const [
                  Tab(text: '全部'),
                  Tab(text: '专家代理'),
                  Tab(text: '健康管理'),
                  Tab(text: '知识增强'),
                  Tab(text: '个性化服务'),
                ],
              ),
            ),
          ];
        },
        body: TabBarView(
          controller: _tabController,
          children: [
            // 全部代理
            _buildAllAgentsTab(),
            
            // 专家代理
            _buildExpertAgentsTab(),
            
            // 健康管理
            _buildHealthManagementTab(),
            
            // 知识增强
            _buildKnowledgeEnhancementTab(),
            
            // 个性化服务
            _buildPersonalizedServiceTab(),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // 启动代理创建向导
          _showAgentCreationDialog();
        },
        backgroundColor: AppColors.primaryColor,
        child: const Icon(Icons.add),
      ),
    );
  }
  
  // 构建"全部代理"标签页
  Widget _buildAllAgentsTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 快捷功能区
          _buildQuickActionSection(),
          
          const SizedBox(height: 24),
          
          // 推荐代理
          _buildRecommendedAgentsSection(),
          
          const SizedBox(height: 24),
          
          // 最近使用
          _buildRecentlyUsedSection(),
          
          const SizedBox(height: 24),
          
          // 代理分类
          _buildAgentCategoriesSection(),
        ],
      ),
    );
  }
  
  // 构建"专家代理"标签页
  Widget _buildExpertAgentsTab() {
    // 专家代理列表
    final expertAgents = [
      {
        'id': 'tcm_expert',
        'name': '中医专家',
        'description': '提供中医辨证和养生建议',
        'icon': Icons.spa,
        'color': Colors.green,
        'bgColor': Colors.green.shade50,
        'featureTags': ['中医辨证', '体质分析', '养生方案'],
      },
      {
        'id': 'nutrition_advisor',
        'name': '营养顾问',
        'description': '帮助您制定健康饮食计划',
        'icon': Icons.restaurant,
        'color': Colors.orange,
        'bgColor': Colors.orange.shade50,
        'featureTags': ['饮食计划', '营养分析', '食谱推荐'],
      },
      {
        'id': 'sleep_coach',
        'name': '睡眠教练',
        'description': '帮助您改善睡眠质量',
        'icon': Icons.bedtime,
        'color': Colors.blue,
        'bgColor': Colors.blue.shade50,
        'featureTags': ['睡眠分析', '睡眠优化', '放松技巧'],
      },
      {
        'id': 'exercise_trainer',
        'name': '运动教练',
        'description': '制定个性化的运动计划',
        'icon': Icons.fitness_center,
        'color': Colors.red,
        'bgColor': Colors.red.shade50,
        'featureTags': ['运动计划', '姿势矫正', '康复训练'],
      },
      {
        'id': 'mental_wellness',
        'name': '心理顾问',
        'description': '提供情绪管理和压力缓解建议',
        'icon': Icons.psychology,
        'color': Colors.purple,
        'bgColor': Colors.purple.shade50,
        'featureTags': ['情绪管理', '压力缓解', '认知调整'],
      },
      {
        'id': 'health_diagnostician',
        'name': '健康诊断师',
        'description': '分析健康数据，提供健康建议',
        'icon': Icons.health_and_safety,
        'color': Colors.teal,
        'bgColor': Colors.teal.shade50,
        'featureTags': ['健康评估', '风险预警', '预防建议'],
      },
    ];
    
    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 0.75,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
      ),
      itemCount: expertAgents.length,
      itemBuilder: (context, index) {
        final agent = expertAgents[index];
        return AgentGridItem(
          title: agent['name'] as String,
          description: agent['description'] as String,
          icon: agent['icon'] as IconData,
          color: agent['color'] as Color,
          backgroundColor: agent['bgColor'] as Color,
          tags: agent['featureTags'] as List<String>,
          onTap: () => _openAgentDetail(agent['id'] as String),
        );
      },
    );
  }
  
  // 构建"健康管理"标签页
  Widget _buildHealthManagementTab() {
    // 健康管理代理列表
    final healthAgents = [
      {
        'id': 'health_monitor',
        'name': '健康监测',
        'description': '实时监测和分析您的健康指标',
        'icon': Icons.monitor_heart,
        'color': Colors.red,
        'bgColor': Colors.red.shade50,
        'featureTags': ['生命体征', '趋势分析', '异常预警'],
      },
      {
        'id': 'diet_planner',
        'name': '饮食规划',
        'description': '基于体质和健康目标定制饮食方案',
        'icon': Icons.restaurant_menu,
        'color': Colors.green,
        'bgColor': Colors.green.shade50,
        'featureTags': ['营养均衡', '热量控制', '食谱推荐'],
      },
      {
        'id': 'fitness_tracker',
        'name': '健身追踪',
        'description': '记录和分析您的运动数据',
        'icon': Icons.directions_run,
        'color': Colors.blue,
        'bgColor': Colors.blue.shade50,
        'featureTags': ['运动记录', '效果分析', '目标管理'],
      },
      {
        'id': 'medication_reminder',
        'name': '用药提醒',
        'description': '管理您的药物并提供按时服药提醒',
        'icon': Icons.medication,
        'color': Colors.orange,
        'bgColor': Colors.orange.shade50,
        'featureTags': ['用药计划', '定时提醒', '药物知识'],
      },
    ];
    
    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 0.75,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
      ),
      itemCount: healthAgents.length,
      itemBuilder: (context, index) {
        final agent = healthAgents[index];
        return AgentGridItem(
          title: agent['name'] as String,
          description: agent['description'] as String,
          icon: agent['icon'] as IconData,
          color: agent['color'] as Color,
          backgroundColor: agent['bgColor'] as Color,
          tags: agent['featureTags'] as List<String>,
          onTap: () => _openAgentDetail(agent['id'] as String),
        );
      },
    );
  }
  
  // 构建"知识增强"标签页
  Widget _buildKnowledgeEnhancementTab() {
    // 知识增强代理列表
    final knowledgeAgents = [
      {
        'id': 'rag_assistant',
        'name': 'RAG助手',
        'description': '基于检索增强生成的知识问答系统',
        'icon': Icons.psychology,
        'color': Colors.purple,
        'bgColor': Colors.purple.shade50,
        'featureTags': ['检索增强', '知识问答', '内容生成'],
      },
      {
        'id': 'knowledge_graph',
        'name': '知识图谱',
        'description': '健康养生领域的关联知识网络',
        'icon': Icons.share,
        'color': Colors.blue,
        'bgColor': Colors.blue.shade50,
        'featureTags': ['概念关联', '知识导航', '深度探索'],
      },
      {
        'id': 'research_assistant',
        'name': '研究助手',
        'description': '帮助您查找和解读专业医学文献',
        'icon': Icons.school,
        'color': Colors.green,
        'bgColor': Colors.green.shade50,
        'featureTags': ['文献检索', '内容摘要', '专业解读'],
      },
      {
        'id': 'learning_companion',
        'name': '学习伙伴',
        'description': '提供个性化的健康知识学习计划',
        'icon': Icons.book,
        'color': Colors.orange,
        'bgColor': Colors.orange.shade50,
        'featureTags': ['知识课程', '进度跟踪', '测验评估'],
      },
    ];
    
    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 0.75,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
      ),
      itemCount: knowledgeAgents.length,
      itemBuilder: (context, index) {
        final agent = knowledgeAgents[index];
        return AgentGridItem(
          title: agent['name'] as String,
          description: agent['description'] as String,
          icon: agent['icon'] as IconData,
          color: agent['color'] as Color,
          backgroundColor: agent['bgColor'] as Color,
          tags: agent['featureTags'] as List<String>,
          onTap: () => _openAgentDetail(agent['id'] as String),
        );
      },
    );
  }
  
  // 构建"个性化服务"标签页
  Widget _buildPersonalizedServiceTab() {
    // 个性化服务代理列表
    final personalizedAgents = [
      {
        'id': 'health_companion',
        'name': '健康伴侣',
        'description': '提供全方位的健康管理和陪伴服务',
        'icon': Icons.favorite,
        'color': Colors.red,
        'bgColor': Colors.red.shade50,
        'featureTags': ['健康管理', '生活建议', '情感支持'],
      },
      {
        'id': 'lifestyle_coach',
        'name': '生活方式教练',
        'description': '帮助您建立健康的生活习惯',
        'icon': Icons.lightbulb,
        'color': Colors.amber,
        'bgColor': Colors.amber.shade50,
        'featureTags': ['习惯养成', '行为干预', '进步跟踪'],
      },
      {
        'id': 'family_health_manager',
        'name': '家庭健康管家',
        'description': '管理全家人的健康状况和需求',
        'icon': Icons.family_restroom,
        'color': Colors.green,
        'bgColor': Colors.green.shade50,
        'featureTags': ['家庭协作', '健康记录', '关怀提醒'],
      },
      {
        'id': 'wellness_planner',
        'name': '养生规划师',
        'description': '根据个人体质制定养生保健方案',
        'icon': Icons.spa,
        'color': Colors.teal,
        'bgColor': Colors.teal.shade50,
        'featureTags': ['体质分析', '季节调养', '养生食疗'],
      },
    ];
    
    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 0.75,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
      ),
      itemCount: personalizedAgents.length,
      itemBuilder: (context, index) {
        final agent = personalizedAgents[index];
        return AgentGridItem(
          title: agent['name'] as String,
          description: agent['description'] as String,
          icon: agent['icon'] as IconData,
          color: agent['color'] as Color,
          backgroundColor: agent['bgColor'] as Color,
          tags: agent['featureTags'] as List<String>,
          onTap: () => _openAgentDetail(agent['id'] as String),
        );
      },
    );
  }
  
  // 构建快捷功能区
  Widget _buildQuickActionSection() {
    final quickActions = [
      {
        'name': '健康问答',
        'icon': Icons.question_answer,
        'color': Colors.blue,
      },
      {
        'name': '找代理',
        'icon': Icons.search,
        'color': Colors.green,
      },
      {
        'name': '代理推荐',
        'icon': Icons.recommend,
        'color': Colors.orange,
      },
      {
        'name': '我的代理',
        'icon': Icons.person,
        'color': Colors.purple,
      },
    ];
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '快捷功能',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: quickActions.map((action) {
            return Column(
              children: [
                Container(
                  width: 60,
                  height: 60,
                  decoration: BoxDecoration(
                    color: (action['color'] as Color).withOpacity(0.1),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    action['icon'] as IconData,
                    color: action['color'] as Color,
                    size: 30,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  action['name'] as String,
                  style: const TextStyle(
                    fontSize: 12,
                  ),
                ),
              ],
            );
          }).toList(),
        ),
      ],
    );
  }
  
  // 构建推荐代理区域
  Widget _buildRecommendedAgentsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              '推荐代理',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            TextButton(
              onPressed: () {
                // 查看更多推荐代理
              },
              child: const Text('查看更多'),
            ),
          ],
        ),
        const SizedBox(height: 12),
        SizedBox(
          height: 140,
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: [
              _buildRecommendedAgentCard(
                name: '中医专家',
                description: '提供中医辨证和养生建议',
                color: Colors.green,
                icon: Icons.spa,
              ),
              _buildRecommendedAgentCard(
                name: '睡眠教练',
                description: '帮助您改善睡眠质量',
                color: Colors.blue,
                icon: Icons.bedtime,
              ),
              _buildRecommendedAgentCard(
                name: '营养顾问',
                description: '帮助您制定健康饮食计划',
                color: Colors.orange,
                icon: Icons.restaurant,
              ),
              _buildRecommendedAgentCard(
                name: '知识图谱',
                description: '探索健康养生的关联知识',
                color: Colors.purple,
                icon: Icons.share,
              ),
            ],
          ),
        ),
      ],
    );
  }
  
  // 构建推荐代理卡片
  Widget _buildRecommendedAgentCard({
    required String name,
    required String description,
    required Color color,
    required IconData icon,
  }) {
    return Container(
      margin: const EdgeInsets.only(right: 16),
      width: 220,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.2),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  icon,
                  color: color,
                  size: 20,
                ),
              ),
              const SizedBox(width: 8),
              Text(
                name,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            description,
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[700],
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const Spacer(),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              TextButton(
                onPressed: () {
                  // 打开代理详情
                },
                style: TextButton.styleFrom(
                  minimumSize: Size.zero,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
                child: Text(
                  '了解更多',
                  style: TextStyle(
                    color: color,
                    fontSize: 12,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
  
  // 构建最近使用区域
  Widget _buildRecentlyUsedSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '最近使用',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        Card(
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          child: ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: 3,
            separatorBuilder: (context, index) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final recentAgents = [
                {
                  'name': '中医专家',
                  'lastQuery': '如何调理春季过敏体质？',
                  'time': '昨天',
                  'icon': Icons.spa,
                  'color': Colors.green,
                },
                {
                  'name': '营养顾问',
                  'lastQuery': '适合高血压患者的食谱推荐',
                  'time': '3天前',
                  'icon': Icons.restaurant,
                  'color': Colors.orange,
                },
                {
                  'name': '健康监测',
                  'lastQuery': '查看本周健康趋势报告',
                  'time': '5天前',
                  'icon': Icons.monitor_heart,
                  'color': Colors.red,
                },
              ];
              
              final agent = recentAgents[index];
              
              return ListTile(
                leading: CircleAvatar(
                  backgroundColor: (agent['color'] as Color).withOpacity(0.2),
                  child: Icon(
                    agent['icon'] as IconData,
                    color: agent['color'] as Color,
                    size: 20,
                  ),
                ),
                title: Text(agent['name'] as String),
                subtitle: Text(
                  agent['lastQuery'] as String,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                trailing: Text(
                  agent['time'] as String,
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 12,
                  ),
                ),
                onTap: () {
                  // 继续上次的对话
                },
              );
            },
          ),
        ),
      ],
    );
  }
  
  // 构建代理分类区域
  Widget _buildAgentCategoriesSection() {
    final categories = [
      {
        'name': '专家代理',
        'icon': Icons.person,
        'color': Colors.blue,
        'count': 6,
      },
      {
        'name': '健康管理',
        'icon': Icons.favorite,
        'color': Colors.red,
        'count': 4,
      },
      {
        'name': '知识增强',
        'icon': Icons.psychology,
        'color': Colors.purple,
        'count': 4,
      },
      {
        'name': '个性化服务',
        'icon': Icons.star,
        'color': Colors.amber,
        'count': 4,
      },
    ];
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '代理分类',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            childAspectRatio: 2.2,
            crossAxisSpacing: 16,
            mainAxisSpacing: 16,
          ),
          itemCount: categories.length,
          itemBuilder: (context, index) {
            final category = categories[index];
            return Card(
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: InkWell(
                onTap: () {
                  // 打开对应的分类标签页
                  _tabController.animateTo(index + 1);
                },
                borderRadius: BorderRadius.circular(12),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: (category['color'] as Color).withOpacity(0.1),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(
                          category['icon'] as IconData,
                          color: category['color'] as Color,
                          size: 20,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              category['name'] as String,
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Text(
                              '${category['count']}个代理',
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey[600],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ],
    );
  }
  
  // 打开代理详情页面
  void _openAgentDetail(String agentId) {
    // 导航到代理详情页面
  }
  
  // 显示代理创建对话框
  void _showAgentCreationDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('创建自定义代理'),
        content: const Text('即将推出！您将能够创建和定制自己的专属代理助手。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }
} 