import 'package:flutter/material.dart';
import 'package:get/get.dart';

class QuickActions extends StatelessWidget {
  const QuickActions({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '快捷操作',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildQuickAction(
                icon: Icons.person_add,
                label: '添加朋友',
                onTap: () => Get.toNamed('/contacts/add'),
              ),
              _buildQuickAction(
                icon: Icons.group_add,
                label: '发起群聊',
                onTap: () => Get.toNamed('/chat/group/create'),
              ),
              _buildQuickAction(
                icon: Icons.calendar_today,
                label: '预约咨询',
                onTap: () => Get.toNamed('/consultation/book'),
              ),
              _buildQuickAction(
                icon: Icons.qr_code_scanner,
                label: '扫一扫',
                onTap: () => Get.toNamed('/scan'),
              ),
              _buildQuickAction(
                icon: Icons.payment,
                label: '收付款',
                onTap: () => Get.toNamed('/payment'),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQuickAction({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: 12,
          vertical: 8,
        ),
        child: Column(
          children: [
            Icon(icon, size: 28),
            const SizedBox(height: 4),
            Text(
              label,
              style: const TextStyle(fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }
} 