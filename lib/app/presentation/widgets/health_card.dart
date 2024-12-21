import 'package:flutter/material.dart';
import '../../data/models/health_advice.dart';

class HealthCard extends StatelessWidget {
  final HealthAdvice advice;
  final VoidCallback onTap;

  const HealthCard({
    Key? key,
    required this.advice,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (advice.imageUrl.isNotEmpty)
              AspectRatio(
                aspectRatio: 16 / 9,
                child: Container(
                  decoration: BoxDecoration(
                    image: DecorationImage(
                      image: NetworkImage(advice.imageUrl),
                      fit: BoxFit.cover,
                    ),
                  ),
                ),
              ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          advice.title,
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                      ),
                      if (advice.isPremium)
                        const Icon(
                          Icons.workspace_premium,
                          color: Colors.amber,
                        ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    advice.description,
                    style: Theme.of(context).textTheme.bodyMedium,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
} 