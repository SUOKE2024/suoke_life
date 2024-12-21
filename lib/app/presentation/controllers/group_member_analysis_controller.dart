import 'package:get/get.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../core/base/base_controller.dart';
import '../../services/group_statistics_service.dart';
import '../../data/models/active_member.dart';

class GroupMemberAnalysisController extends BaseController {
  final _statisticsService = Get.find<GroupStatisticsService>();
  final String groupId;

  // 时间范围
  final timeRange = 'week'.obs;

  // 活跃成员列表
  final topMembers = <ActiveMember>[].obs;

  // 图表数据
  late final activeTimeChart = BarChartData().obs;
  late final messageTypeChart = PieChartData().obs;

  // 成员互动数据
  final interactions = <Map<String, dynamic>>[].obs;

  GroupMemberAnalysisController({required this.groupId});

  @override
  void onInit() {
    super.onInit();
    _loadAnalysis();
    ever(timeRange, (_) => _loadAnalysis());
  }

  void setTimeRange(String range) {
    timeRange.value = range;
  }

  Future<void> _loadAnalysis() async {
    try {
      isLoading.value = true;

      // 加载活跃成员
      final members = await _statisticsService.getTopMembers(
        groupId,
        timeRange: timeRange.value,
      );
      topMembers.value = members;

      // 加载活跃时段分析
      final activeTime = await _statisticsService.getActiveTime(
        groupId,
        timeRange: timeRange.value,
      );
      activeTimeChart.value = _buildActiveTimeChart(activeTime);

      // 加载消息类型分布
      final types = await _statisticsService.getMessageTypes(
        groupId,
        timeRange: timeRange.value,
      );
      messageTypeChart.value = _buildMessageTypeChart(types);

      // 加载成员互动分析
      final memberInteractions = await _statisticsService.getMemberInteractions(
        groupId,
        timeRange: timeRange.value,
      );
      interactions.value = memberInteractions;
    } catch (e) {
      showError('加载分析数据失败');
    } finally {
      isLoading.value = false;
    }
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
} 