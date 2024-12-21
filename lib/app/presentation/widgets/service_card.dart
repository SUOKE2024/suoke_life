import 'package:flutter/material.dart';

class ServiceCard extends StatelessWidget {
  final String title;
  final String description;
  final String icon;
  final VoidCallback onTap;
  final bool isNew;
  final bool isPremium;

  const ServiceCard({
    Key? key,
    required this.title,
    required this.description,
    required this.icon,
    required this.onTap,
    this.isNew = false,
    this.isPremium = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Stack(
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Image.asset(
                    icon,
                    width: 48,
                    height: 48,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    description,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.grey[600],
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            if (isNew)
              Positioned(
                right: 12,
                top: 12,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: Theme.of(context).primaryColor,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Text(
                    'NEW',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                    ),
                  ),
                ),
              ),
            if (isPremium)
              Positioned(
                right: 12,
                bottom: 12,
                child: Icon(
                  Icons.workspace_premium,
                  color: Colors.amber[700],
                  size: 20,
                ),
              ),
          ],
        ),
      ),
    );
  }
} 