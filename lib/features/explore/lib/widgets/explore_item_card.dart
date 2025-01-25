import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class ExploreItemCard extends StatelessWidget {
  final String title;
  final String description;
  final String imageUrl;

  const ExploreItemCard({
    Key? key,
    required this.title,
    required this.description,
    required this.imageUrl,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(16.0),
      child: InkWell(
        onTap: () => context.go('/explore_item_detail', extra: {
          'title': title,
          'description': description,
          'imageUrl': imageUrl,
        }),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Image.asset(
              imageUrl,
              height: 150,
              width: double.infinity,
              fit: BoxFit.cover,
            ),
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(description),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
} 