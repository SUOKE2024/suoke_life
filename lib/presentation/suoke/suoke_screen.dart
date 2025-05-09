import 'package:flutter/material.dart';
import 'package:suoke_life/presentation/life/diagnosis_navigator_screen.dart';

/// SUOKE服务屏幕
class SuokeScreen extends StatelessWidget {
  /// 构造函数
  const SuokeScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('索克服务'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // 顶部横幅
          _buildBanner(context),
          
          const SizedBox(height: 24),
          
          // 标题：我们的服务
          Padding(
            padding: const EdgeInsets.only(left: 8, bottom: 16),
            child: Text(
              '我们的服务',
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          
          // 服务卡片网格
          GridView.count(
            physics: const NeverScrollableScrollPhysics(),
            shrinkWrap: true,
            crossAxisCount: 2,
            childAspectRatio: 0.85,
            mainAxisSpacing: 16,
            crossAxisSpacing: 16,
            children: [
              _buildServiceCard(
                context,
                icon: Icons.local_hospital,
                title: '中医体质检测',
                description: '通过四诊合参，全面评估您的体质类型',
                color: const Color(0xFF35BB78),
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const DiagnosisNavigatorScreen(
                        userId: 'default_user_123',
                      ),
                    ),
                  );
                },
              ),
              _buildServiceCard(
                context,
                icon: Icons.spa,
                title: '针灸咨询',
                description: '专业医师提供针灸治疗方案',
                color: const Color(0xFFFF6800),
                onTap: () {},
              ),
              _buildServiceCard(
                context,
                icon: Icons.healing,
                title: '中药处方',
                description: '在线获取由中医师开具的中药处方',
                color: const Color(0xFF5E72E4),
                onTap: () {},
              ),
              _buildServiceCard(
                context,
                icon: Icons.health_and_safety,
                title: '养生指导',
                description: '根据体质特点提供个性化养生方案',
                color: const Color(0xFFFF9F43),
                onTap: () {},
              ),
            ],
          ),
          
          const SizedBox(height: 32),
          
          // 标题：我们的产品
          Padding(
            padding: const EdgeInsets.only(left: 8, bottom: 16),
            child: Text(
              '我们的产品',
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          
          // 产品卡片列表
          _buildProductCard(
            context,
            imageUrl: 'assets/images/products/tongue_scanner.jpg',
            title: '舌诊智能扫描仪',
            description: '高精度舌象采集设备，支持AI分析，提供专业舌诊报告',
            price: '¥2,999',
            onTap: () {},
          ),
          
          const SizedBox(height: 16),
          
          _buildProductCard(
            context,
            imageUrl: 'assets/images/products/pulse_device.jpg',
            title: '脉诊智能腕表',
            description: '佩戴式脉象监测设备，24小时记录脉象变化，AI辅助分析',
            price: '¥1,899',
            onTap: () {},
          ),
          
          const SizedBox(height: 16),
          
          _buildProductCard(
            context,
            imageUrl: 'assets/images/products/herbal_kit.jpg',
            title: '家庭中药熏蒸套装',
            description: '便捷式中药熏蒸设备，多种模式满足不同需求',
            price: '¥799',
            onTap: () {},
          ),
          
          const SizedBox(height: 24),
        ],
      ),
    );
  }

  /// 构建顶部横幅
  Widget _buildBanner(BuildContext context) {
    return Container(
      height: 150,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        gradient: const LinearGradient(
          colors: [Color(0xFF35BB78), Color(0xFF29A268)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
      ),
      child: Stack(
        children: [
          Positioned(
            right: -20,
            bottom: -20,
            child: Icon(
              Icons.spa,
              size: 140,
              color: Colors.white.withOpacity(0.2),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text(
                  '索克中医',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '传承千年智慧，科技赋能健康',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.9),
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () {},
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: const Color(0xFF35BB78),
                  ),
                  child: const Text('了解更多'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 构建服务卡片
  Widget _buildServiceCard(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String description,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Card(
      elevation: 2,
      clipBehavior: Clip.antiAlias,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  icon,
                  color: color,
                  size: 28,
                ),
              ),
              const SizedBox(height: 16),
              Text(
                title,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                description,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// 构建产品卡片
  Widget _buildProductCard(
    BuildContext context, {
    required String imageUrl,
    required String title,
    required String description,
    required String price,
    required VoidCallback onTap,
  }) {
    return Card(
      elevation: 2,
      clipBehavior: Clip.antiAlias,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: InkWell(
        onTap: onTap,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 图片占位符
            Container(
              height: 180,
              width: double.infinity,
              color: Colors.grey[300],
              child: Center(
                child: Icon(
                  Icons.image,
                  size: 64,
                  color: Colors.grey[400],
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    description,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.grey[600],
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        price,
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: const Color(0xFF35BB78),
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      ElevatedButton(
                        onPressed: () {},
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF35BB78),
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                        child: const Text('购买'),
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
