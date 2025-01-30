import 'package:flutter/material.dart';
import 'package:suoke_life/lib/core/widgets/common_scaffold.dart';

class ExploreItemDetailPage extends StatelessWidget {
  final String title;
  final String description;
  final String imageUrl;

  const ExploreItemDetailPage({
    Key? key,
    required this.title,
    required this.description,
    required this.imageUrl,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return CommonScaffold(
      title: title,
      body: Column(
        children: [
          Image.asset(imageUrl),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(description),
          ),
        ],
      ),
    );
  }
} 