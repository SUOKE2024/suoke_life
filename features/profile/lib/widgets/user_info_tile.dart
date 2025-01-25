import 'package:flutter/material.dart';

class UserInfoTile extends StatelessWidget {
  final String title;
  final IconData icon;

  const UserInfoTile({
    Key? key,
    required this.title,
    required this.icon,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      onTap: () {
        // TODO: Implement user info tile tap action
      },
    );
  }
} 