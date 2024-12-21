import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';

class ProfileHeader extends StatelessWidget {
  final String? avatar;
  final String name;
  final String role;
  final VoidCallback onAvatarTap;
  final VoidCallback onNameTap;

  const ProfileHeader({
    Key? key,
    this.avatar,
    required this.name,
    required this.role,
    required this.onAvatarTap,
    required this.onNameTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            GestureDetector(
              onTap: onAvatarTap,
              child: CircleAvatar(
                radius: 40,
                backgroundImage: avatar != null
                  ? CachedNetworkImageProvider(avatar!)
                  : null,
                child: avatar == null
                  ? Text(name[0], style: const TextStyle(fontSize: 24))
                  : null,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: GestureDetector(
                onTap: onNameTap,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      name,
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      role,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.grey,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const Icon(Icons.chevron_right),
          ],
        ),
      ),
    );
  }
} 