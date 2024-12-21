import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:suoke_life/presentation/controllers/analytics_controller.dart';

class AnalyticsPage extends GetView<AnalyticsController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('数据统计'),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: controller.loadAllStats,
          ),
        ],
      ),
      body: Obx(() => ListView(
        padding: EdgeInsets.all(16),
        children: [
          // 基础统计卡片
          _buildStatsCard(),
          SizedBox(height: 16),
          
          // 标签使用频率图表
          _buildTagFrequencyChart(),
          SizedBox(height: 16),
          
          // 月度记录趋势图
          _buildMonthlyTrendChart(),
          SizedBox(height: 16),
          
          // 时间分布热力图
          _buildHourlyDistributionChart(),
          SizedBox(height: 16),
          
          // 内容长度分布饼图
          _buildLengthDistributionChart(),
          SizedBox(height: 16),
          
          // 情感分析图表
          _buildEmotionChart(),
        ],
      )),
    );
  }

  Widget _buildStatsCard() {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '基础统计',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 16),
            _buildStatRow('总记录数', '${controller.stats['total'] ?? 0}'),
            _buildStatRow('包含图片', '${controller.stats['hasImage'] ?? 0}'),
            _buildStatRow('包含标签', '${controller.stats['hasTags'] ?? 0}'),
            _buildStatRow(
              '平均标签数',
              '${(controller.stats['avgTagsPerRecord'] ?? 0).toStringAsFixed(1)}',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTagFrequencyChart() {
    final topTags = controller.getTopTags();
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '热门标签',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: BarChart(
                BarChartData(
                  alignment: BarChartAlignment.spaceAround,
                  maxY: topTags.isEmpty ? 1 : 
                        topTags.map((e) => e.value.toDouble()).reduce((a, b) => a > b ? a : b),
                  titlesData: FlTitlesData(
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: true),
                    ),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (value, meta) {
                          if (value.toInt() >= topTags.length) return Text('');
                          return Padding(
                            padding: EdgeInsets.only(top: 8),
                            child: Text(
                              topTags[value.toInt()].key,
                              style: TextStyle(fontSize: 12),
                            ),
                          );
                        },
                      ),
                    ),
                  ),
                  barGroups: List.generate(
                    topTags.length,
                    (index) => BarChartGroupData(
                      x: index,
                      barRods: [
                        BarChartRodData(
                          toY: topTags[index].value.toDouble(),
                          color: Colors.blue,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMonthlyTrendChart() {
    final monthlyData = controller.monthlyCount.entries.toList()
      ..sort((a, b) => a.key.compareTo(b.key));
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '月度趋势',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: LineChart(
                LineChartData(
                  lineBarsData: [
                    LineChartBarData(
                      spots: List.generate(
                        monthlyData.length,
                        (index) => FlSpot(
                          index.toDouble(),
                          monthlyData[index].value.toDouble(),
                        ),
                      ),
                      color: Colors.blue,
                      dotData: FlDotData(show: true),
                    ),
                  ],
                  titlesData: FlTitlesData(
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (value, meta) {
                          if (value.toInt() >= monthlyData.length) return Text('');
                          return Padding(
                            padding: EdgeInsets.only(top: 8),
                            child: Text(
                              monthlyData[value.toInt()].key,
                              style: TextStyle(fontSize: 10),
                            ),
                          );
                        },
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHourlyDistributionChart() {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '时间分布',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 16),
            GridView.count(
              shrinkWrap: true,
              physics: NeverScrollableScrollPhysics(),
              crossAxisCount: 6,
              children: List.generate(24, (hour) {
                final count = controller.hourlyDistribution[hour] ?? 0;
                final maxCount = controller.hourlyDistribution.values
                    .fold(0, (max, value) => value > max ? value : max);
                final opacity = maxCount == 0 ? 0.1 : count / maxCount;
                
                return Container(
                  margin: EdgeInsets.all(2),
                  decoration: BoxDecoration(
                    color: Colors.blue.withOpacity(opacity),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Center(
                    child: Text(
                      '$hour:00',
                      style: TextStyle(
                        color: opacity > 0.5 ? Colors.white : Colors.black,
                        fontSize: 12,
                      ),
                    ),
                  ),
                );
              }),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLengthDistributionChart() {
    final data = controller.lengthDistribution;
    final total = data.values.fold(0, (sum, value) => sum + value);
    
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '内容长度分布',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: PieChart(
                PieChartData(
                  sections: data.entries.map((e) {
                    final percentage = total == 0 ? 0 : e.value / total * 100;
                    return PieChartSectionData(
                      value: e.value.toDouble(),
                      title: '${e.key}\n${percentage.toStringAsFixed(1)}%',
                      radius: 100,
                      titleStyle: TextStyle(
                        fontSize: 12,
                        color: Colors.white,
                      ),
                    );
                  }).toList(),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmotionChart() {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '情感分析',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 8),
            Text(
              '主要情感倾向: ${controller.getDominantEmotion()}',
              style: TextStyle(
                color: Colors.grey[600],
              ),
            ),
            SizedBox(height: 16),
            LinearProgressIndicator(
              value: controller.emotionStats['positive'] ?? 0,
              backgroundColor: Colors.grey[200],
              color: Colors.green,
            ),
            SizedBox(height: 4),
            Text('积极 ${((controller.emotionStats['positive'] ?? 0) * 100).toStringAsFixed(1)}%'),
            SizedBox(height: 8),
            LinearProgressIndicator(
              value: controller.emotionStats['neutral'] ?? 0,
              backgroundColor: Colors.grey[200],
              color: Colors.blue,
            ),
            SizedBox(height: 4),
            Text('平和 ${((controller.emotionStats['neutral'] ?? 0) * 100).toStringAsFixed(1)}%'),
            SizedBox(height: 8),
            LinearProgressIndicator(
              value: controller.emotionStats['negative'] ?? 0,
              backgroundColor: Colors.grey[200],
              color: Colors.red,
            ),
            SizedBox(height: 4),
            Text('消极 ${((controller.emotionStats['negative'] ?? 0) * 100).toStringAsFixed(1)}%'),
          ],
        ),
      ),
    );
  }

  Widget _buildStatRow(String label, String value) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
} 