import 'package:flutter/material.dart';

class ChatAppBar extends StatelessWidget implements PreferredSizeWidget {
  final Widget title;
  final VoidCallback onAvatarTap;
  final VoidCallback onMoreTap;
  final List<Widget>? actions;

  const ChatAppBar({
    Key? key,
    required this.title,
    required this.onAvatarTap,
    required this.onMoreTap,
    this.actions,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return AppBar(
      leading: IconButton(
        icon: const Icon(Icons.arrow_back),
        onPressed: () => Navigator.pop(context),
      ),
      title: Row(
        children: [
          GestureDetector(
            onTap: onAvatarTap,
            child: const CircleAvatar(
              radius: 16,
              backgroundImage: AssetImage('assets/images/default_avatar.png'),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(child: title),
        ],
      ),
      actions: [
        ...?actions,
        IconButton(
          icon: const Icon(Icons.more_vert),
          onPressed: onMoreTap,
        ),
      ],
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
} 