import 'package:flutter/material.dart';

class UserProfileCard extends StatelessWidget {
  final Map<String, dynamic> profile;
  final VoidCallback onTap;

  const UserProfileCard({
    Key? key,
    required this.profile,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              CircleAvatar(
                radius: 30,
                backgroundImage: profile['avatar']?.startsWith('assets/') ?? false
                    ? AssetImage(profile['avatar']!) as ImageProvider
                    : NetworkImage(profile['avatar'] ?? ''),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      profile['name'] ?? '',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      profile['description'] ?? '',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
} 