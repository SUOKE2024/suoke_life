import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../core/routes/route_paths.dart';
import 'service_controller.dart';
import 'service_model.dart';

class ServicePage extends GetView<ServiceController> {
  const ServicePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        actions: [
          IconButton(
            icon: const Icon(Icons.shopping_cart_outlined),
            onPressed: () => Get.toNamed(RoutePaths.cart),
          ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.add_circle_outline),
            offset: const Offset(0, 45),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            itemBuilder: (context) => [
              _buildPopupMenuItem(
                icon: Icons.api,
                title: '第三方API服务',
                value: RoutePaths.apiService,
                description: '审核通过后显示在本页面',
              ),
              _buildPopupMenuItem(
                icon: Icons.design_services,
                title: '索克定制',
                value: RoutePaths.customService,
                description: '审核通过后显示在本页面',
              ),
              _buildPopupMenuItem(
                icon: Icons.inventory,
                title: '供应链入口',
                value: RoutePaths.supplyChain,
                description: '审核通过后显示在本页面',
              ),
            ],
            onSelected: (value) => Get.toNamed(value),
          ),
        ],
      ),
      body: Stack(
        children: [
          Obx(() => controller.services.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.add_business,
                        size: 64,
                        color: Colors.grey[400],
                      ),
                      const SizedBox(height: 16),
                      Text(
                        '点击右上角"+"号添加服务项目',
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.grey[600],
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '审核通过后将显示在本页面',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[500],
                        ),
                      ),
                    ],
                  ),
                )
              : GridView.builder(
                  padding: const EdgeInsets.all(16),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    mainAxisSpacing: 16,
                    crossAxisSpacing: 16,
                    childAspectRatio: 0.8,
                  ),
                  itemCount: controller.services.length,
                  itemBuilder: (context, index) {
                    final service = controller.services[index];
                    return _buildServiceCard(service);
                  },
                )),
          Positioned(
            right: 16,
            bottom: 16,
            child: _buildAssistantBubble(),
          ),
        ],
      ),
    );
  }

  PopupMenuItem<String> _buildPopupMenuItem({
    required IconData icon,
    required String title,
    required String value,
    required String description,
  }) {
    return PopupMenuItem<String>(
      value: value,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 20),
              const SizedBox(width: 12),
              Text(title),
            ],
          ),
          Padding(
            padding: const EdgeInsets.only(left: 32),
            child: Text(
              description,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildServiceCard(ServiceModel service) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: InkWell(
        onTap: () => Get.toNamed(service.route),
        borderRadius: BorderRadius.circular(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ClipRRect(
              borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
              child: AspectRatio(
                aspectRatio: 16/9,
                child: Image.network(
                  service.coverImage,
                  fit: BoxFit.cover,
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    service.title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    service.description,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      _buildMetric(
                        icon: Icons.favorite,
                        value: '${service.popularity}%',
                        color: Colors.red,
                      ),
                      _buildMetric(
                        icon: Icons.remove_red_eye,
                        value: service.visits,
                        color: Colors.blue,
                      ),
                      _buildMetric(
                        icon: Icons.star,
                        value: service.rating.toString(),
                        color: Colors.amber,
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

  Widget _buildMetric({
    required IconData icon,
    required String value,
    required Color color,
  }) {
    return Row(
      children: [
        Icon(
          icon,
          size: 14,
          color: color,
        ),
        const SizedBox(width: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  Widget _buildAssistantBubble() {
    return FloatingActionButton(
      onPressed: () => Get.toNamed(RoutePaths.xiaokeChat),
      backgroundColor: Colors.white,
      elevation: 4,
      child: Stack(
        children: [
          const CircleAvatar(
            radius: 28,
            backgroundColor: Colors.green,
            child: Icon(
              Icons.child_care,
              color: Colors.white,
              size: 32,
            ),
          ),
          Positioned(
            right: 0,
            bottom: 0,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.blue,
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Text(
                'AI',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 8,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
} 