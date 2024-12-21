import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/group_member_analysis_controller.dart';
import '../../../core/base/base_page.dart';
import 'package:fl_chart/fl_chart.dart';

class GroupMemberAnalysisPage extends BasePage<GroupMemberAnalysisController> {
  const GroupMemberAnalysisPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('成员分析'),
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
        // 成员活跃度排行
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('活跃度排行', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
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
                      subtitle: Text('活跃度: ${member.activeScore.toStringAsFixed(1)}'),
                      trailing: Text('${member.messageCount}条消息'),
                    );
                  },
                )),
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),

        // 成员活跃时段分布
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('活跃时段分布', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
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

        // 成员消息类型分布
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('消息类型分布', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
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

        // 成员互动关系
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('互动关系', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                Obx(() => ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: controller.interactions.length,
                  itemBuilder: (context, index) {
                    final interaction = controller.interactions[index];
                    return ListTile(
                      title: Text('${interaction['from']} → ${interaction['to']}'),
                      subtitle: Text('互动次数: ${interaction['count']}'),
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
} 