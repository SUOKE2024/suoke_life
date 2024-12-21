import 'package:get/get.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../core/base/base_controller.dart';
import '../../services/group_statistics_service.dart';
import '../../data/models/active_member.dart';

class GroupStatisticsController extends BaseController {
  final _statisticsService = Get.find<GroupStatisticsService>();
  final String groupId;

  // 基础统计数据
  final totalMessages = 0.obs;
  final todayMessages = 0.obs;
  final activeMembers = 0.obs;

  // 时间范围
  final timeRange = 'week'.obs;

  // 活跃成员列表
  final topMembers = <ActiveMember>[].obs;

  // 图表数据
  late final messageChart = LineChartData().obs;
  late final messageTypeChart = PieChartData().obs;
  late final activeTimeChart = BarChartData().obs;

  GroupStatisticsController({required this.groupId});

  @override
  void onInit() {
    super.onInit();
    _loadStatistics();
  }

  void setTimeRange(String range) {
    timeRange.value = range;
    _loadStatistics();
  }

  Future<void> _loadStatistics() async {
    try {
      isLoading.value = true;

      // 加载基础统计数据
      final overview = await _statisticsService.getOverview(groupId);
      totalMessages.value = overview['totalMessages'];
      todayMessages.value = overview['todayMessages'];
      activeMembers.value = overview['activeMembers'];

      // 加载活跃成员
      final members = await _statisticsService.getTopMembers(
        groupId,
        timeRange: timeRange.value,
      );
      topMembers.value = members;

      // 加载消息趋势
      final trend = await _statisticsService.getMessageTrend(
        groupId,
        timeRange: timeRange.value,
      );
      messageChart.value = _buildMessageChart(trend);

      // 加载消息类型分布
      final types = await _statisticsService.getMessageTypes(
        groupId,
        timeRange: timeRange.value,
      );
      messageTypeChart.value = _buildMessageTypeChart(types);

      // 加载活跃时段分析
      final activeTime = await _statisticsService.getActiveTime(
        groupId,
        timeRange: timeRange.value,
      );
      activeTimeChart.value = _buildActiveTimeChart(activeTime);
    } catch (e) {
      showError('加载统计数据失败');
    } finally {
      isLoading.value = false;
    }
  }

  LineChartData _buildMessageChart(List<Map<String, dynamic>> data) {
    return LineChartData(
      gridData: FlGridData(show: false),
      titlesData: FlTitlesData(
        leftTitles: AxisTitles(
          sideTitles: SideTitles(showTitles: false),
        ),
        bottomTitles: AxisTitles(
          sideTitles: SideTitles(
            showTitles: true,
            getTitlesWidget: (value, meta) {
              return Text(data[value.toInt()]['date']);
            },
          ),
        ),
      ),
      borderData: FlBorderData(show: false),
      lineBarsData: [
        LineChartBarData(
          spots: data.asMap().entries.map((entry) {
            return FlSpot(
              entry.key.toDouble(),
              entry.value['count'].toDouble(),
            );
          }).toList(),
          isCurved: true,
          color: Get.theme.primaryColor,
          barWidth: 3,
          dotData: FlDotData(show: false),
        ),
      ],
    );
  }

  PieChartData _buildMessageTypeChart(Map<String, int> data) {
    final total = data.values.fold(0, (sum, count) => sum + count);
    return PieChartData(
      sections: data.entries.map((entry) {
        final percent = entry.value / total * 100;
        return PieChartSectionData(
          value: entry.value.toDouble(),
          title: '${entry.key}\n${percent.toStringAsFixed(1)}%',
          radius: 100,
          titleStyle: const TextStyle(
            fontSize: 12,
            color: Colors.white,
          ),
        );
      }).toList(),
    );
  }

  BarChartData _buildActiveTimeChart(Map<String, int> data) {
    return BarChartData(
      gridData: FlGridData(show: false),
      titlesData: FlTitlesData(
        leftTitles: AxisTitles(
          sideTitles: SideTitles(showTitles: false),
        ),
        bottomTitles: AxisTitles(
          sideTitles: SideTitles(
            showTitles: true,
            getTitlesWidget: (value, meta) {
              return Text('${value.toInt()}时');
            },
          ),
        ),
      ),
      borderData: FlBorderData(show: false),
      barGroups: data.entries.map((entry) {
        return BarChartGroupData(
          x: int.parse(entry.key),
          barRods: [
            BarChartRodData(
              toY: entry.value.toDouble(),
              color: Get.theme.primaryColor,
              width: 16,
            ),
          ],
        );
      }).toList(),
    );
  }
} 