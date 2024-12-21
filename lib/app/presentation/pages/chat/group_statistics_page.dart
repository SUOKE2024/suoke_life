import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/group_statistics_controller.dart';
import '../../../core/base/base_page.dart';
import 'package:fl_chart/fl_chart.dart';

class GroupStatisticsPage extends BasePage<GroupStatisticsController> {
  const GroupStatisticsPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('群聊统计'),
      actions: [
        PopupMenuButton<String>(
          onSelected: controller.setTimeRange,
          itemBuilder: (context) => [
            const PopupMenuItem(value: 'week', child: Text('最近一周')),
            const PopupMenuItem(value: 'month', child: Text('最近一月')),
            const PopupMenuItem(value: 'year', child: Text('最近一年')),
          ],
        ),
      ],
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // 消息总览
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('消息总览', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildStatItem('总消息数', controller.totalMessages),
                    _buildStatItem('今日消息', controller.todayMessages),
                    _buildStatItem('活跃成员', controller.activeMembers),
                  ],
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),

        // 消息趋势图
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('消息趋势', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                SizedBox(
                  height: 200,
                  child: Obx(() => LineChart(
                    controller.messageChart,
                    swapAnimationDuration: const Duration(milliseconds: 250),
                  )),
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),

        // 消息类型分布
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('消息类型', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                SizedBox(
                  height: 200,
                  child: Obx(() => PieChart(
                    controller.messageTypeChart,
                    swapAnimationDuration: const Duration(milliseconds: 250),
                  )),
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),

        // 活跃时段分析
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('活跃时段', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                SizedBox(
                  height: 200,
                  child: Obx(() => BarChart(
                    controller.activeTimeChart,
                    swapAnimationDuration: const Duration(milliseconds: 250),
                  )),
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),

        // 活跃成员排行
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('活跃成员', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                Obx(() => ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: controller.topMembers.length,
                  itemBuilder: (context, index) {
                    final member = controller.topMembers[index];
                    return ListTile(
                      leading: CircleAvatar(
                        backgroundImage: NetworkImage(member.avatar),
                      ),
                      title: Text(member.name),
                      trailing: Text('${member.messageCount}条消息'),
                    );
                  },
                )),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildStatItem(String label, RxInt value) {
    return Column(
      children: [
        Text(
          value.toString(),
          style: const TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }
} 