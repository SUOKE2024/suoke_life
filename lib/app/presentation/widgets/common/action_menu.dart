import 'package:flutter/material.dart';

class ActionMenuItem {
  final IconData icon;
  final String title;
  final VoidCallback onTap;

  const ActionMenuItem({
    required this.icon,
    required this.title,
    required this.onTap,
  });
}

class ActionMenu extends StatelessWidget {
  final List<ActionMenuItem> items;

  const ActionMenu({
    Key? key,
    required this.items,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ...items.map((item) => ListTile(
            leading: Icon(item.icon),
            title: Text(item.title),
            onTap: () {
              Navigator.pop(context);
              item.onTap();
            },
          )),
          const SizedBox(height: 8),
          // 取消按钮
          ListTile(
            title: const Text(
              '取消',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey),
            ),
            onTap: () => Navigator.pop(context),
          ),
        ],
      ),
    );
  }
} 