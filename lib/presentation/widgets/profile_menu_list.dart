import 'package:flutter/material.dart';

class ProfileMenuList extends StatelessWidget {
  const ProfileMenuList({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _buildSection(
          context,
          '健康管理',
          [
            _MenuItem(
              icon: Icons.favorite,
              color: Colors.red,
              title: '健康档案',
              onTap: () {
                // TODO: 打开健康档案页面
              },
            ),
            _MenuItem(
              icon: Icons.directions_run,
              color: Colors.green,
              title: '运动记录',
              onTap: () {
                // TODO: 打开运动记录页面
              },
            ),
            _MenuItem(
              icon: Icons.restaurant,
              color: Colors.orange,
              title: '饮食记录',
              onTap: () {
                // TODO: 打开饮食记录页面
              },
            ),
          ],
        ),
        _buildSection(
          context,
          '订单中心',
          [
            _MenuItem(
              icon: Icons.local_drink,
              color: Colors.blue,
              title: '饮品订单',
              onTap: () {
                // TODO: 打开饮品订单页面
              },
            ),
            _MenuItem(
              icon: Icons.shopping_bag,
              color: Colors.purple,
              title: '商城订单',
              onTap: () {
                // TODO: 打开商城订单页面
              },
            ),
            _MenuItem(
              icon: Icons.receipt_long,
              color: Colors.teal,
              title: '服务订单',
              onTap: () {
                // TODO: 打开服务订单页面
              },
            ),
          ],
        ),
        _buildSection(
          context,
          '其他服务',
          [
            _MenuItem(
              icon: Icons.help_outline,
              color: Colors.grey,
              title: '帮助中心',
              onTap: () {
                // TODO: 打开帮助中心页面
              },
            ),
            _MenuItem(
              icon: Icons.support_agent,
              color: Colors.indigo,
              title: '联系客服',
              onTap: () {
                // TODO: 打开联系客服页面
              },
            ),
            _MenuItem(
              icon: Icons.info_outline,
              color: Colors.brown,
              title: '关于我们',
              onTap: () {
                // TODO: 打开关于我们页面
              },
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildSection(
    BuildContext context,
    String title,
    List<_MenuItem> items,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Text(
            title,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        Container(
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surface,
            border: Border(
              top: BorderSide(color: Colors.grey[200]!),
              bottom: BorderSide(color: Colors.grey[200]!),
            ),
          ),
          child: Column(
            children: items.map((item) {
              return _buildMenuItem(context, item);
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildMenuItem(BuildContext context, _MenuItem item) {
    return InkWell(
      onTap: item.onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 12,
        ),
        decoration: BoxDecoration(
          border: Border(
            bottom: BorderSide(
              color: Colors.grey[200]!,
            ),
          ),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: item.color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                item.icon,
                color: item.color,
                size: 20,
              ),
            ),
            const SizedBox(width: 12),
            Text(
              item.title,
              style: const TextStyle(fontSize: 16),
            ),
            const Spacer(),
            Icon(
              Icons.arrow_forward_ios,
              size: 16,
              color: Colors.grey[400],
            ),
          ],
        ),
      ),
    );
  }
}

class _MenuItem {
  final IconData icon;
  final Color color;
  final String title;
  final VoidCallback onTap;

  const _MenuItem({
    required this.icon,
    required this.color,
    required this.title,
    required this.onTap,
  });
} 