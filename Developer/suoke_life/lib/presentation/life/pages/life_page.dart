import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/core/widgets/app_widgets.dart';

/// LIFE页面（健康生活方式）
@RoutePage()
class LifePage extends ConsumerStatefulWidget {
  const LifePage({super.key});

  @override
  ConsumerState<LifePage> createState() => _LifePageState();
}

class _LifePageState extends ConsumerState<LifePage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  // 健康模块列表
  final List<Map<String, dynamic>> _healthModules = [
    {
      'title': '中医体质',
      'icon': Icons.person_outline,
      'color': Color(0xFF35BB78),
      'description': '基于中医理论的个人体质分析',
    },
    {
      'title': '食疗推荐',
      'icon': Icons.restaurant,
      'color': Color(0xFFFF6800),
      'description': '根据体质特点的个性化食疗方案',
    },
    {
      'title': '穴位指导',
      'icon': Icons.touch_app,
      'color': Color(0xFF6A88E5),
      'description': '常用穴位保健按摩指导',
    },
    {
      'title': '冥想放松',
      'icon': Icons.self_improvement,
      'color': Color(0xFF9E7FDE),
      'description': '引导式冥想和呼吸练习',
    },
  ];

  // 节气健康信息
  final List<Map<String, dynamic>> _seasonalHealthInfo = [
    {
      'title': '谷雨养生',
      'subtitle': '当前节气',
      'imageUrl':
          'https://images.unsplash.com/photo-1599940824399-b87987ceb72a?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2940&q=80',
      'description': '谷雨时节阳气生发，宜清补肝肾，健脾养胃',
    },
    {
      'title': '立夏饮食',
      'subtitle': '即将到来',
      'imageUrl':
          'https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2940&q=80',
      'description': '立夏养生宜养心，饮食宜清淡，多食蔬果',
    },
    {
      'title': '小满调理',
      'subtitle': '即将到来',
      'imageUrl':
          'https://images.unsplash.com/photo-1529599087-9f6aeddb8bba?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2940&q=80',
      'description': '小满时节湿热渐盛，宜健脾祛湿，清热解毒',
    },
  ];

  // 今日健康建议
  final List<Map<String, dynamic>> _dailyHealthTips = [
    {
      'title': '晨起喝杯温开水',
      'description': '补充水分，促进新陈代谢',
      'icon': Icons.water_drop,
    },
    {
      'title': '午后适度运动',
      'description': '建议进行30分钟有氧运动',
      'icon': Icons.directions_run,
    },
    {
      'title': '睡前泡脚放松',
      'description': '促进血液循环，改善睡眠质量',
      'icon': Icons.spa,
    },
  ];

  // 统计数据
  final Map<String, dynamic> _healthStats = {
    'steps': {
      'value': '8,542',
      'icon': Icons.directions_walk,
      'color': Colors.green
    },
    'sleep': {
      'value': '7.2小时',
      'icon': Icons.nightlight_round,
      'color': Colors.indigo
    },
    'water': {'value': '1200毫升', 'icon': Icons.opacity, 'color': Colors.blue},
    'heartRate': {
      'value': '72次/分',
      'icon': Icons.favorite,
      'color': Colors.red
    },
  };

  // 健康建议
  final List<Map<String, dynamic>> _healthTips = [
    {
      'title': '今日养生建议',
      'content': '根据您的体质特点和当前气候，建议多喝温水，适当进行户外活动。',
      'icon': Icons.insights,
      'color': AppColors.primaryColor,
    },
    {
      'title': '体质调理方案',
      'content': '您的湿热体质特征较为明显，建议饮食清淡，少食辛辣油腻食物。',
      'icon': Icons.spa,
      'color': Colors.purple,
    },
    {
      'title': '节气养生提醒',
      'content': '当前节气：处暑。注意防暑降温，饮食宜清淡，可适当食用梨、苦瓜等食物。',
      'icon': Icons.wb_sunny,
      'color': Colors.orange,
    },
  ];

  // 生活活动
  final List<Map<String, dynamic>> _lifeActivities = [
    {
      'title': '晨间太极',
      'time': '每日 06:30-07:30',
      'location': '城市公园',
      'participants': 12,
      'color': Colors.teal,
    },
    {
      'title': '健康饮食工坊',
      'time': '周四 19:00-21:00',
      'location': '社区活动中心',
      'participants': 8,
      'color': Colors.amber,
    },
    {
      'title': '中医养生讲座',
      'time': '周六 15:00-16:30',
      'location': '线上直播',
      'participants': 36,
      'color': Colors.deepOrange,
    },
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.background,
      appBar: AppBar(
        title: const Text('LIFE'),
        centerTitle: true,
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: '健康生活'),
            Tab(text: '体质管理'),
            Tab(text: '健康数据'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildHealthyLifeTab(),
          _buildConstitutionTab(),
          _buildHealthDataTab(),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: AppColors.primaryColor,
        onPressed: _showHealthAssessmentDialog,
        child: const Icon(Icons.add_task),
      ),
    );
  }

  /// 构建健康生活标签页
  Widget _buildHealthyLifeTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          // 个人健康状态卡片
          _buildHealthStatusCard(),

          const SizedBox(height: 24),

          // 今日健康建议
          const Text(
            '今日健康建议',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          _buildDailyHealthTips(),

          const SizedBox(height: 24),

          // 节气健康信息
          const Text(
            '节气健康',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          _buildSeasonalHealthCards(),

          const SizedBox(height: 24),

          // 健康模块
          const Text(
            '健康养生',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          _buildHealthModules(),
        ],
      ),
    );
  }

  /// 构建体质管理标签页
  Widget _buildConstitutionTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          // 体质评估入口卡片
          GradientCard(
            title: '中医体质评估',
            leadingIcon: Icons.analytics,
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                AppColors.primaryColor,
                AppColors.primaryColor.withAlpha(180),
              ],
            ),
            content: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              mainAxisSize: MainAxisSize.min,
              children: [
                const SizedBox(height: 8.0),
                const Text(
                  '通过九种体质分类系统，了解您的体质特点，获取个性化调理方案。',
                  style: TextStyle(
                    color: Colors.white,
                    height: 1.5,
                  ),
                ),
                const SizedBox(height: 16.0),
                PrimaryButton(
                  label: '开始评估',
                  prefixIcon: Icons.play_arrow,
                  onPressed: () {
                    context.router.pushNamed('/life/constitution-assessment');
                  },
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // 体质知识卡片
          BasicCard(
            title: '中医体质知识',
            leadingIcon: Icons.menu_book,
            content: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 8.0),
                const Text(
                  '中医体质学说是中医学对人体体质特性的认识和总结，共分为九种基本体质类型。',
                  style: TextStyle(height: 1.5),
                ),
                const SizedBox(height: 8.0),
                Wrap(
                  spacing: 8.0,
                  runSpacing: 8.0,
                  children: const [
                    Chip(label: Text('平和质')),
                    Chip(label: Text('气虚质')),
                    Chip(label: Text('阳虚质')),
                    Chip(label: Text('阴虚质')),
                    Chip(label: Text('痰湿质')),
                    Chip(label: Text('湿热质')),
                    Chip(label: Text('血瘀质')),
                    Chip(label: Text('气郁质')),
                    Chip(label: Text('特禀质')),
                  ],
                ),
                const SizedBox(height: 8.0),
                AppTextButton(
                  label: '了解更多',
                  onPressed: () {},
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // 已进行的评估记录
          OutlineCard(
            title: '我的评估记录',
            leadingIcon: Icons.history,
            content: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 8.0),
                // 评估记录列表
                ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: 1,
                  itemBuilder: (context, index) {
                    return ListTile(
                      leading: CircleAvatar(
                        backgroundColor: AppColors.waterColor.withAlpha(50),
                        child: Icon(Icons.person, color: AppColors.waterColor),
                      ),
                      title: const Text('初次体质评估'),
                      subtitle: const Text('2023-08-15 · 阳虚质、气虚质倾向'),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () {
                        context.router.pushNamed('/life/constitution-result');
                      },
                    );
                  },
                ),
                if (true) // 如果没有评估记录
                  const Padding(
                    padding: EdgeInsets.all(16.0),
                    child: Center(
                      child: Text(
                        '暂无评估记录，点击"开始评估"进行体质测试',
                        style: TextStyle(color: Colors.grey),
                      ),
                    ),
                  ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // 五行养生卡片
          BasicCard(
            title: '五行养生',
            leadingIcon: Icons.category,
            content: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 8.0),
                const Text(
                  '中医五行学说认为木、火、土、金、水五种元素相生相克，对应人体的五脏。根据五行特性进行养生，可以达到阴阳平衡。',
                  style: TextStyle(height: 1.5),
                ),
                const SizedBox(height: 16.0),
                SizedBox(
                  height: 100,
                  child: ListView(
                    scrollDirection: Axis.horizontal,
                    children: [
                      _buildFiveElementCard('木', '疏肝理气', Colors.green),
                      _buildFiveElementCard('火', '心安神宁', Colors.red),
                      _buildFiveElementCard('土', '健脾和胃', Colors.amber),
                      _buildFiveElementCard('金', '润肺清肃', Colors.grey),
                      _buildFiveElementCard('水', '滋肾固本', Colors.blue),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 构建五行养生卡片
  Widget _buildFiveElementCard(
      String element, String description, Color color) {
    return Container(
      width: 100,
      height: 80,
      margin: const EdgeInsets.only(right: 12),
      decoration: BoxDecoration(
        color: color.withAlpha(50),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            element,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            description,
            style: TextStyle(
              color: color,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  /// 构建健康数据标签页
  Widget _buildHealthDataTab() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.bar_chart,
            size: 80,
            color: AppColors.primaryColor.withAlpha(100),
          ),
          const SizedBox(height: 16),
          const Text(
            '健康数据功能即将上线',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            '敬请期待！',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 32),
          ElevatedButton.icon(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('健康数据记录功能正在开发中')),
              );
            },
            icon: const Icon(Icons.add_chart),
            label: const Text('记录数据'),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primaryColor,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(
                horizontal: 24,
                vertical: 12,
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 构建个人健康状态卡片
  Widget _buildHealthStatusCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppColors.primaryColor,
            AppColors.primaryColor.withAlpha(180),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: AppColors.primaryColor.withAlpha(50),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  color: Colors.white.withAlpha(50),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.person,
                  color: Colors.white,
                  size: 36,
                ),
              ),
              const SizedBox(width: 16),
              const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    '今日健康指数',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                    ),
                  ),
                  SizedBox(height: 4),
                  Text(
                    '85分',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const Spacer(),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.white.withAlpha(50),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Text(
                      '平和质偏湿热',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    '点击查看详情',
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildHealthMetric('睡眠', '7.2小时', '良好'),
              _buildHealthMetric('活动', '3200步', '偏低'),
              _buildHealthMetric('心情', '愉悦', '良好'),
            ],
          ),
        ],
      ),
    );
  }

  /// 构建健康指标项
  Widget _buildHealthMetric(String title, String value, String status) {
    Color statusColor;
    if (status == '良好') {
      statusColor = Colors.greenAccent;
    } else if (status == '偏低') {
      statusColor = Colors.orangeAccent;
    } else {
      statusColor = Colors.redAccent;
    }

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          title,
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 12,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 4),
        Container(
          padding: const EdgeInsets.symmetric(
            horizontal: 8,
            vertical: 2,
          ),
          decoration: BoxDecoration(
            color: statusColor.withAlpha(100),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            status,
            style: TextStyle(
              color: statusColor,
              fontSize: 10,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
    );
  }

  /// 构建今日健康建议
  Widget _buildDailyHealthTips() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: _dailyHealthTips.map((tip) {
        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: AppColors.primaryColor.withAlpha(30),
              child: Icon(
                tip['icon'] as IconData,
                color: AppColors.primaryColor,
              ),
            ),
            title: Text(tip['title'] as String),
            subtitle: Text(tip['description'] as String),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('健康建议：${tip['title']}')),
              );
            },
          ),
        );
      }).toList(),
    );
  }

  /// 构建节气健康卡片
  Widget _buildSeasonalHealthCards() {
    return SizedBox(
      height: 180,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: _seasonalHealthInfo.length,
        itemBuilder: (context, index) {
          final info = _seasonalHealthInfo[index];
          return Container(
            width: 280,
            margin: const EdgeInsets.only(right: 16),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
            ),
            clipBehavior: Clip.antiAlias,
            child: Stack(
              fit: StackFit.expand,
              children: [
                // 背景图片
                Image.network(
                  info['imageUrl'] as String,
                  fit: BoxFit.cover,
                  errorBuilder: (context, error, stackTrace) {
                    debugPrint('Error loading image: ${info['imageUrl']}');
                    return Container(
                      color: Colors.grey.withAlpha(50),
                      child: const Center(
                        child:
                            Icon(Icons.image_not_supported, color: Colors.grey),
                      ),
                    );
                  },
                ),

                // 渐变叠加层
                Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        Colors.transparent,
                        Colors.black.withAlpha(160),
                      ],
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                    ),
                  ),
                ),

                // 内容
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: AppColors.secondaryColor,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          info['subtitle'] as String,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        info['title'] as String,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        info['description'] as String,
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  /// 构建健康模块
  Widget _buildHealthModules() {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
        childAspectRatio: 1.5,
      ),
      itemCount: _healthModules.length,
      itemBuilder: (context, index) {
        final module = _healthModules[index];
        return InkWell(
          onTap: () {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('${module['title']}功能正在开发中')),
            );
          },
          borderRadius: BorderRadius.circular(16),
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: module['color'].withAlpha(30),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: module['color'].withAlpha(60),
                width: 1,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Icon(
                  module['icon'] as IconData,
                  color: module['color'] as Color,
                  size: 32,
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      module['title'] as String,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      module['description'] as String,
                      style: const TextStyle(
                        fontSize: 12,
                        color: Colors.grey,
                      ),
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

  /// 显示健康评估对话框
  void _showHealthAssessmentDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('健康评估'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('选择您想要进行的评估类型'),
              const SizedBox(height: 16),
              ListTile(
                leading: const Icon(Icons.person_outline),
                title: const Text('体质测评'),
                subtitle: const Text('基于中医理论的九种体质评估'),
                onTap: () {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('体质测评功能正在开发中')),
                  );
                },
              ),
              ListTile(
                leading: const Icon(Icons.spa),
                title: const Text('亚健康评估'),
                subtitle: const Text('评估当前身体亚健康状态'),
                onTap: () {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('亚健康评估功能正在开发中')),
                  );
                },
              ),
              ListTile(
                leading: const Icon(Icons.restaurant),
                title: const Text('饮食习惯评估'),
                subtitle: const Text('分析日常饮食模式和营养状况'),
                onTap: () {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('饮食习惯评估功能正在开发中')),
                  );
                },
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context);
              },
              child: const Text('取消'),
            ),
          ],
        );
      },
    );
  }
}
