import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import '../base/base_page.dart';

@RoutePage()
class SuokePage extends StatelessWidget {
  const SuokePage({super.key});

  @override
  Widget build(BuildContext context) {
    return BasePage(
      title: '搜客',
      body: GridView.builder(
        padding: const EdgeInsets.all(16),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          mainAxisSpacing: 16,
          crossAxisSpacing: 16,
          childAspectRatio: 1.5,
        ),
        itemCount: _services.length,
        itemBuilder: (context, index) => _buildServiceCard(_services[index]),
      ),
    );
  }

  Widget _buildServiceCard(ServiceItem service) {
    return Card(
      child: InkWell(
        onTap: () {
          // TODO: 导航到服务详情页
        },
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(service.icon, size: 32),
            const SizedBox(height: 8),
            Text(service.title),
          ],
        ),
      ),
    );
  }

  static const _services = [
    ServiceItem(title: '健康问卷', icon: Icons.assignment),
    ServiceItem(title: 'API服务', icon: Icons.api),
    ServiceItem(title: '农产品预制', icon: Icons.shopping_basket),
    ServiceItem(title: '供应链', icon: Icons.inventory),
  ];
}

class ServiceItem {
  final String title;
  final IconData icon;

  const ServiceItem({
    required this.title,
    required this.icon,
  });
} 