import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';

import '../../../core/theme/app_colors.dart';

@RoutePage()
class LifeScreen extends ConsumerStatefulWidget {
  const LifeScreen({super.key});

  @override
  ConsumerState<LifeScreen> createState() => _LifeScreenState();
}

class _LifeScreenState extends ConsumerState<LifeScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  
  // 当前展示的健康数据类型
  String _selectedDataType = '睡眠';
  
  // 健康数据时间范围
  String _selectedTimeRange = '一周';
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }
  
  // 健康数据类型列表
  final List<String> _dataTypes = ['睡眠', '步数', '心率', '血压', '体重'];
  
  // 时间范围列表
  final List<String> _timeRanges = ['一天', '一周', '一月', '三月', '一年'];
  
  // 健康文章列表
  final List<Map<String, dynamic>> _healthArticles = [
    {
      'id': 'a1',
      'title': '秋季养生：如何安然度过燥热交替的季节',
      'summary': '秋季气候多变，昼夜温差大，是呼吸道疾病的高发期。本文介绍了秋季养生的关键点...',
      'author': '王医生',
      'publishDate': '2023-09-15',
      'imageUrl': 'assets/images/autumn_health.jpg',
      'readCount': 1254,
      'likeCount': 89,
      'tags': ['秋季养生', '中医', '饮食调理'],
    },
    {
      'id': 'a2',
      'title': '科学睡眠：提高睡眠质量的8个小技巧',
      'summary': '睡眠对健康至关重要，但现代人普遍存在睡眠问题。本文分享了改善睡眠质量的实用方法...',
      'author': '李睡眠专家',
      'publishDate': '2023-08-22',
      'imageUrl': 'assets/images/sleep_health.jpg',
      'readCount': 3621,
      'likeCount': 245,
      'tags': ['睡眠', '健康生活', '压力管理'],
    },
    {
      'id': 'a3',
      'title': '中医体质辨识：你是哪种体质？',
      'summary': '中医认为体质差异导致疾病易感性和养生方法的不同。了解自己的体质类型，对症调养...',
      'author': '张中医',
      'publishDate': '2023-07-30',
      'imageUrl': 'assets/images/tcm_body_type.jpg',
      'readCount': 2897,
      'likeCount': 176,
      'tags': ['中医', '体质', '辨证养生'],
    },
  ];
  
  // 生活记录列表
  final List<Map<String, dynamic>> _lifeRecords = [
    {
      'id': 'r1',
      'title': '晨跑',
      'description': '沿着河边慢跑30分钟，感觉精神焕发',
      'datetime': '今天 07:30',
      'type': '运动',
      'icon': Icons.directions_run,
      'color': AppColors.successColor,
    },
    {
      'id': 'r2',
      'title': '早餐',
      'description': '全麦面包、煮鸡蛋、牛奶和香蕉',
      'datetime': '今天 08:15',
      'type': '饮食',
      'icon': Icons.restaurant,
      'color': AppColors.accentColor,
    },
    {
      'id': 'r3',
      'title': '工作会议',
      'description': '项目进度讨论，有些紧张但顺利完成',
      'datetime': '今天 10:00',
      'type': '工作',
      'icon': Icons.work,
      'color': AppColors.aiLaoke,
    },
    {
      'id': 'r4',
      'title': '午餐',
      'description': '蔬菜沙拉、糙米饭和清蒸鱼',
      'datetime': '今天 12:30',
      'type': '饮食',
      'icon': Icons.restaurant,
      'color': AppColors.accentColor,
    },
    {
      'id': 'r5',
      'title': '冥想',
      'description': '使用索克生活APP进行了15分钟的引导冥想',
      'datetime': '今天 15:45',
      'type': '放松',
      'icon': Icons.self_improvement,
      'color': AppColors.aiXiaoai,
    },
  ];
  
  // 睡眠数据
  final List<Map<String, dynamic>> _sleepData = [
    {'day': '周一', 'hours': 7.5, 'quality': 0.85},
    {'day': '周二', 'hours': 6.8, 'quality': 0.75},
    {'day': '周三', 'hours': 7.2, 'quality': 0.8},
    {'day': '周四', 'hours': 8.0, 'quality': 0.9},
    {'day': '周五', 'hours': 6.5, 'quality': 0.7},
    {'day': '周六', 'hours': 8.5, 'quality': 0.95},
    {'day': '周日', 'hours': 7.8, 'quality': 0.85},
  ];
  
  // 步数数据
  final List<Map<String, dynamic>> _stepsData = [
    {'day': '周一', 'steps': 8523},
    {'day': '周二', 'steps': 7241},
    {'day': '周三', 'steps': 9654},
    {'day': '周四', 'steps': 6325},
    {'day': '周五', 'steps': 8975},
    {'day': '周六', 'steps': 12354},
    {'day': '周日', 'steps': 11256},
  ];
  
  // 心率数据
  final List<Map<String, dynamic>> _heartRateData = [
    {'day': '周一', 'resting': 65, 'average': 72},
    {'day': '周二', 'resting': 64, 'average': 75},
    {'day': '周三', 'resting': 66, 'average': 78},
    {'day': '周四', 'resting': 63, 'average': 71},
    {'day': '周五', 'resting': 65, 'average': 74},
    {'day': '周六', 'resting': 62, 'average': 70},
    {'day': '周日', 'resting': 64, 'average': 73},
  ];
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('生活记录'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: '健康数据'),
            Tab(text: '养生知识'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          // 健康数据页
          _buildHealthDataTab(),
          
          // 养生知识页
          _buildHealthKnowledgeTab(),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // 添加生活记录
          _showAddRecordDialog();
        },
        child: const Icon(Icons.add),
      ),
    );
  }
  
  // 构建健康数据标签页
  Widget _buildHealthDataTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 健康服务卡片
          _buildHealthServicesCard(),
          
          const SizedBox(height: 24),
          
          // 数据类型选择器
          _buildDataTypeSelector(),
          
          const SizedBox(height: 16),
          
          // 时间范围选择器
          _buildTimeRangeSelector(),
          
          const SizedBox(height: 24),
          
          // 数据图表
          _buildDataChart(),
          
          const SizedBox(height: 24),
          
          // 今日摘要
          _buildTodaySummary(),
          
          const SizedBox(height: 24),
          
          // 生活记录列表
          const Text(
            '生活记录',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          
          const SizedBox(height: 16),
          
          _buildLifeRecordsList(),
        ],
      ),
    );
  }
  
  // 构建健康服务卡片
  Widget _buildHealthServicesCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '健康服务',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildServiceItem(
                  icon: Icons.calendar_today,
                  label: '预约服务',
                  color: AppColors.primaryColor,
                  onTap: () {
                    // 导航到预约列表页面
                    context.router.pushNamed('/appointment');
                  },
                ),
                _buildServiceItem(
                  icon: Icons.medical_services,
                  label: '健康咨询',
                  color: AppColors.accentColor,
                  onTap: () {
                    // 导航到健康咨询页面
                    // TODO: 实现健康咨询页面
                  },
                ),
                _buildServiceItem(
                  icon: Icons.spa,
                  label: '养生方案',
                  color: AppColors.aiLaoke,
                  onTap: () {
                    // 导航到养生方案页面
                    // TODO: 实现养生方案页面
                  },
                ),
                _buildServiceItem(
                  icon: Icons.local_hospital,
                  label: '健康档案',
                  color: AppColors.aiXiaoai,
                  onTap: () {
                    // 导航到健康档案页面
                    // TODO: 实现健康档案页面
                  },
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  // 构建服务项
  Widget _buildServiceItem({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        children: [
          Container(
            width: 50,
            height: 50,
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
          const SizedBox(height: 8),
          Text(
            label,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
  
  // 构建养生知识标签页
  Widget _buildHealthKnowledgeTab() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _healthArticles.length,
      itemBuilder: (context, index) {
        final article = _healthArticles[index];
        
        return Card(
          margin: const EdgeInsets.only(bottom: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: 2,
          child: InkWell(
            onTap: () {
              // 导航到文章详情页
              _showArticleDetailDialog(article);
            },
            borderRadius: BorderRadius.circular(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // 文章封面图
                ClipRRect(
                  borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(12),
                    topRight: Radius.circular(12),
                  ),
                  child: AspectRatio(
                    aspectRatio: 16 / 9,
                    child: Container(
                      color: Colors.grey.shade200,
                      child: Center(
                        child: Icon(
                          Icons.photo,
                          size: 40,
                          color: Colors.grey.shade400,
                        ),
                      ),
                    ),
                  ),
                ),
                
                // 文章内容
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // 标题
                      Text(
                        article['title'] as String,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      
                      const SizedBox(height: 8),
                      
                      // 摘要
                      Text(
                        article['summary'] as String,
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey.shade600,
                        ),
                        maxLines: 3,
                        overflow: TextOverflow.ellipsis,
                      ),
                      
                      const SizedBox(height: 12),
                      
                      // 底部信息
                      Row(
                        children: [
                          // 作者信息
                          Text(
                            article['author'] as String,
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey.shade700,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          
                          const SizedBox(width: 8),
                          
                          // 发布日期
                          Text(
                            article['publishDate'] as String,
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey.shade500,
                            ),
                          ),
                          
                          const Spacer(),
                          
                          // 阅读数
                          Icon(
                            Icons.visibility,
                            size: 14,
                            color: Colors.grey.shade500,
                          ),
                          
                          const SizedBox(width: 4),
                          
                          Text(
                            '${article['readCount']}',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey.shade500,
                            ),
                          ),
                          
                          const SizedBox(width: 8),
                          
                          // 点赞数
                          Icon(
                            Icons.thumb_up,
                            size: 14,
                            color: Colors.grey.shade500,
                          ),
                          
                          const SizedBox(width: 4),
                          
                          Text(
                            '${article['likeCount']}',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey.shade500,
                            ),
                          ),
                        ],
                      ),
                      
                      const SizedBox(height: 12),
                      
                      // 标签
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: (article['tags'] as List<String>).map((tag) {
                          return Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: AppColors.primaryColor.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              tag,
                              style: TextStyle(
                                fontSize: 10,
                                color: AppColors.primaryColor,
                              ),
                            ),
                          );
                        }).toList(),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
  
  // 构建数据类型选择器
  Widget _buildDataTypeSelector() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: _dataTypes.map((type) {
          final isSelected = type == _selectedDataType;
          
          return Padding(
            padding: const EdgeInsets.only(right: 12),
            child: ChoiceChip(
              label: Text(type),
              selected: isSelected,
              onSelected: (selected) {
                if (selected) {
                  setState(() {
                    _selectedDataType = type;
                  });
                }
              },
              backgroundColor: Colors.grey.shade200,
              selectedColor: AppColors.primaryColor.withOpacity(0.8),
              labelStyle: TextStyle(
                color: isSelected ? Colors.white : null,
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
  
  // 构建时间范围选择器
  Widget _buildTimeRangeSelector() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: _timeRanges.map((range) {
        final isSelected = range == _selectedTimeRange;
        
        return GestureDetector(
          onTap: () {
            setState(() {
              _selectedTimeRange = range;
            });
          },
          child: Container(
            padding: const EdgeInsets.symmetric(
              horizontal: 12,
              vertical: 6,
            ),
            decoration: BoxDecoration(
              color: isSelected
                  ? AppColors.primaryColor
                  : Colors.transparent,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: isSelected
                    ? AppColors.primaryColor
                    : Colors.grey.shade300,
              ),
            ),
            child: Text(
              range,
              style: TextStyle(
                fontSize: 12,
                color: isSelected ? Colors.white : null,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
  
  // 构建数据图表
  Widget _buildDataChart() {
    Widget chart;
    
    switch (_selectedDataType) {
      case '睡眠':
        chart = _buildSleepChart();
        break;
      case '步数':
        chart = _buildStepsChart();
        break;
      case '心率':
        chart = _buildHeartRateChart();
        break;
      default:
        chart = Container(
          height: 250,
          alignment: Alignment.center,
          child: Text('$_selectedDataType 数据图表暂未实现'),
        );
    }
    
    return Container(
      height: 250,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: chart,
    );
  }
  
  // 构建睡眠图表
  Widget _buildSleepChart() {
    return BarChart(
      BarChartData(
        alignment: BarChartAlignment.spaceAround,
        maxY: 10,
        minY: 0,
        barTouchData: BarTouchData(
          enabled: true,
          touchTooltipData: BarTouchTooltipData(
            tooltipBgColor: Colors.blueGrey,
            getTooltipItem: (group, groupIndex, rod, rodIndex) {
              return BarTooltipItem(
                '${_sleepData[groupIndex]['hours']}小时\n质量: ${(_sleepData[groupIndex]['quality'] * 100).toInt()}%',
                const TextStyle(color: Colors.white),
              );
            },
          ),
        ),
        titlesData: FlTitlesData(
          show: true,
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                if (value < 0 || value >= _sleepData.length) {
                  return const SizedBox.shrink();
                }
                return Padding(
                  padding: const EdgeInsets.only(top: 8.0),
                  child: Text(
                    _sleepData[value.toInt()]['day'] as String,
                    style: const TextStyle(
                      color: Colors.grey,
                      fontSize: 10,
                    ),
                  ),
                );
              },
            ),
          ),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                if (value % 2 != 0) {
                  return const SizedBox.shrink();
                }
                return Text(
                  '${value.toInt()}',
                  style: const TextStyle(
                    color: Colors.grey,
                    fontSize: 10,
                  ),
                );
              },
            ),
          ),
          topTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          rightTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
        ),
        borderData: FlBorderData(show: false),
        gridData: const FlGridData(show: false),
        barGroups: _sleepData.asMap().entries.map((entry) {
          final index = entry.key;
          final data = entry.value;
          final hours = data['hours'] as double;
          final quality = data['quality'] as double;
          
          return BarChartGroupData(
            x: index,
            barRods: [
              BarChartRodData(
                toY: hours,
                color: Color.lerp(
                  AppColors.warningColor,
                  AppColors.healthGood,
                  quality,
                ),
                width: 16,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(4),
                  topRight: Radius.circular(4),
                ),
              ),
            ],
          );
        }).toList(),
      ),
    );
  }
  
  // 构建步数图表
  Widget _buildStepsChart() {
    return BarChart(
      BarChartData(
        alignment: BarChartAlignment.spaceAround,
        maxY: 15000,
        minY: 0,
        barTouchData: BarTouchData(
          enabled: true,
          touchTooltipData: BarTouchTooltipData(
            tooltipBgColor: Colors.blueGrey,
            getTooltipItem: (group, groupIndex, rod, rodIndex) {
              return BarTooltipItem(
                '${_stepsData[groupIndex]['steps']} 步',
                const TextStyle(color: Colors.white),
              );
            },
          ),
        ),
        titlesData: FlTitlesData(
          show: true,
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                if (value < 0 || value >= _stepsData.length) {
                  return const SizedBox.shrink();
                }
                return Padding(
                  padding: const EdgeInsets.only(top: 8.0),
                  child: Text(
                    _stepsData[value.toInt()]['day'] as String,
                    style: const TextStyle(
                      color: Colors.grey,
                      fontSize: 10,
                    ),
                  ),
                );
              },
            ),
          ),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                if (value % 5000 != 0) {
                  return const SizedBox.shrink();
                }
                return Text(
                  '${value.toInt()}',
                  style: const TextStyle(
                    color: Colors.grey,
                    fontSize: 10,
                  ),
                );
              },
            ),
          ),
          topTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          rightTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
        ),
        borderData: FlBorderData(show: false),
        gridData: const FlGridData(show: false),
        barGroups: _stepsData.asMap().entries.map((entry) {
          final index = entry.key;
          final data = entry.value;
          final steps = data['steps'] as int;
          
          // 根据步数与目标(10000)的比例计算颜色
          final ratio = steps / 10000;
          
          return BarChartGroupData(
            x: index,
            barRods: [
              BarChartRodData(
                toY: steps.toDouble(),
                color: ratio < 0.6
                    ? AppColors.warningColor
                    : (ratio < 1.0 ? AppColors.accentColor : AppColors.healthGood),
                width: 16,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(4),
                  topRight: Radius.circular(4),
                ),
              ),
            ],
          );
        }).toList(),
      ),
    );
  }
  
  // 构建心率图表
  Widget _buildHeartRateChart() {
    return LineChart(
      LineChartData(
        lineTouchData: LineTouchData(
          enabled: true,
          touchTooltipData: LineTouchTooltipData(
            tooltipBgColor: Colors.blueGrey,
            getTooltipItems: (touchedSpots) {
              return touchedSpots.map((spot) {
                final dataIndex = spot.x.toInt();
                if (dataIndex < 0 || dataIndex >= _heartRateData.length) {
                  return null;
                }
                
                final data = _heartRateData[dataIndex];
                final value = spot.y.toInt();
                
                return LineTooltipItem(
                  spot.barIndex == 0
                      ? '静息心率: $value'
                      : '平均心率: $value',
                  const TextStyle(color: Colors.white),
                );
              }).toList();
            },
          ),
        ),
        titlesData: FlTitlesData(
          show: true,
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                if (value < 0 || value >= _heartRateData.length) {
                  return const SizedBox.shrink();
                }
                return Padding(
                  padding: const EdgeInsets.only(top: 8.0),
                  child: Text(
                    _heartRateData[value.toInt()]['day'] as String,
                    style: const TextStyle(
                      color: Colors.grey,
                      fontSize: 10,
                    ),
                  ),
                );
              },
            ),
          ),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                if (value % 20 != 0 || value == 0) {
                  return const SizedBox.shrink();
                }
                return Text(
                  '${value.toInt()}',
                  style: const TextStyle(
                    color: Colors.grey,
                    fontSize: 10,
                  ),
                );
              },
            ),
          ),
          topTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          rightTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
        ),
        borderData: FlBorderData(show: false),
        gridData: const FlGridData(show: false),
        minY: 50,
        maxY: 100,
        lineBarsData: [
          // 静息心率
          LineChartBarData(
            spots: _heartRateData.asMap().entries.map((entry) {
              final index = entry.key;
              final data = entry.value;
              return FlSpot(index.toDouble(), (data['resting'] as int).toDouble());
            }).toList(),
            isCurved: true,
            color: AppColors.primaryColor,
            barWidth: 3,
            isStrokeCapRound: true,
            dotData: const FlDotData(show: true),
            belowBarData: BarAreaData(
              show: true,
              color: AppColors.primaryColor.withOpacity(0.1),
            ),
          ),
          
          // 平均心率
          LineChartBarData(
            spots: _heartRateData.asMap().entries.map((entry) {
              final index = entry.key;
              final data = entry.value;
              return FlSpot(index.toDouble(), (data['average'] as int).toDouble());
            }).toList(),
            isCurved: true,
            color: AppColors.accentColor,
            barWidth: 3,
            isStrokeCapRound: true,
            dotData: const FlDotData(show: true),
            belowBarData: BarAreaData(
              show: true,
              color: AppColors.accentColor.withOpacity(0.1),
            ),
          ),
        ],
      ),
    );
  }
  
  // 构建今日摘要
  Widget _buildTodaySummary() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '今日摘要',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          
          const SizedBox(height: 16),
          
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              // 睡眠
              _buildSummaryItem(
                icon: Icons.bedtime,
                value: '7.8',
                unit: '小时',
                label: '睡眠',
                color: AppColors.aiXiaoai,
              ),
              
              // 步数
              _buildSummaryItem(
                icon: Icons.directions_walk,
                value: '6,241',
                unit: '步',
                label: '步数',
                color: AppColors.accentColor,
              ),
              
              // 心率
              _buildSummaryItem(
                icon: Icons.favorite,
                value: '72',
                unit: 'BPM',
                label: '心率',
                color: AppColors.aiLaoke,
              ),
              
              // 活动
              _buildSummaryItem(
                icon: Icons.local_fire_department,
                value: '258',
                unit: '千卡',
                label: '消耗',
                color: AppColors.successColor,
              ),
            ],
          ),
        ],
      ),
    );
  }
  
  // 构建摘要项
  Widget _buildSummaryItem({
    required IconData icon,
    required String value,
    required String unit,
    required String label,
    required Color color,
  }) {
    return Column(
      children: [
        Container(
          width: 50,
          height: 50,
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
        
        const SizedBox(height: 8),
        
        Text(
          value,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        
        Text(
          unit,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey.shade600,
          ),
        ),
        
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey.shade600,
          ),
        ),
      ],
    );
  }
  
  // 构建生活记录列表
  Widget _buildLifeRecordsList() {
    return ListView.separated(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: _lifeRecords.length,
      separatorBuilder: (context, index) => const Divider(),
      itemBuilder: (context, index) {
        final record = _lifeRecords[index];
        
        return ListTile(
          leading: CircleAvatar(
            backgroundColor: (record['color'] as Color).withOpacity(0.2),
            child: Icon(
              record['icon'] as IconData,
              color: record['color'] as Color,
              size: 20,
            ),
          ),
          title: Text(record['title'] as String),
          subtitle: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(record['description'] as String),
              const SizedBox(height: 4),
              Row(
                children: [
                  Text(
                    record['datetime'] as String,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade500,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 6,
                      vertical: 2,
                    ),
                    decoration: BoxDecoration(
                      color: (record['color'] as Color).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      record['type'] as String,
                      style: TextStyle(
                        fontSize: 10,
                        color: record['color'] as Color,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
          onTap: () {
            // 查看记录详情
          },
          trailing: IconButton(
            icon: const Icon(Icons.more_vert),
            onPressed: () {
              // 显示操作菜单
            },
          ),
        );
      },
    );
  }
  
  // 显示添加记录对话框
  void _showAddRecordDialog() {
    final titleController = TextEditingController();
    final descriptionController = TextEditingController();
    String selectedType = '运动';
    
    showDialog(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              title: const Text('添加生活记录'),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 标题输入
                    TextField(
                      controller: titleController,
                      decoration: const InputDecoration(
                        labelText: '标题',
                        hintText: '输入记录标题',
                      ),
                    ),
                    
                    const SizedBox(height: 16),
                    
                    // 描述输入
                    TextField(
                      controller: descriptionController,
                      decoration: const InputDecoration(
                        labelText: '描述',
                        hintText: '输入记录详情',
                      ),
                      maxLines: 3,
                    ),
                    
                    const SizedBox(height: 16),
                    
                    // 类型选择
                    const Text('记录类型'),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      children: [
                        '运动',
                        '饮食',
                        '工作',
                        '放松',
                        '睡眠',
                        '其他',
                      ].map((type) {
                        return ChoiceChip(
                          label: Text(type),
                          selected: selectedType == type,
                          onSelected: (selected) {
                            if (selected) {
                              setState(() {
                                selectedType = type;
                              });
                            }
                          },
                        );
                      }).toList(),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () {
                    Navigator.pop(context);
                  },
                  child: const Text('取消'),
                ),
                TextButton(
                  onPressed: () {
                    // 添加记录
                    if (titleController.text.isNotEmpty) {
                      Navigator.pop(context);
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('记录已添加'),
                        ),
                      );
                    }
                  },
                  child: const Text('添加'),
                ),
              ],
            );
          },
        );
      },
    );
  }
  
  // 显示文章详情对话框
  void _showArticleDetailDialog(Map<String, dynamic> article) {
    showDialog(
      context: context,
      builder: (context) {
        return Dialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // 文章标题
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: AppColors.primaryColor,
                  borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(16),
                    topRight: Radius.circular(16),
                  ),
                ),
                child: Column(
                  children: [
                    Text(
                      article['title'] as String,
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    
                    const SizedBox(height: 8),
                    
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          article['author'] as String,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 14,
                          ),
                        ),
                        
                        const SizedBox(width: 16),
                        
                        Text(
                          article['publishDate'] as String,
                          style: const TextStyle(
                            color: Colors.white70,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              
              // 文章内容 - 只显示摘要
              Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      article['summary'] as String,
                      style: const TextStyle(
                        fontSize: 16,
                        height: 1.6,
                      ),
                    ),
                    
                    const SizedBox(height: 16),
                    
                    Text(
                      '本文仅显示摘要，完整内容请订阅索克生活会员...',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey.shade600,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                    
                    const SizedBox(height: 24),
                    
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        OutlinedButton.icon(
                          icon: const Icon(Icons.bookmark_border),
                          label: const Text('收藏'),
                          onPressed: () {
                            Navigator.pop(context);
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('文章已收藏'),
                              ),
                            );
                          },
                        ),
                        
                        ElevatedButton.icon(
                          icon: const Icon(Icons.subscriptions),
                          label: const Text('订阅会员'),
                          onPressed: () {
                            Navigator.pop(context);
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('会员订阅功能暂未实现'),
                              ),
                            );
                          },
                        ),
                      ],
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
} 