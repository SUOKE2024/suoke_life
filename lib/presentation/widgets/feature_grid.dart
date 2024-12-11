import 'package:flutter/material.dart';

class FeatureItem {
  final String title;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;

  const FeatureItem({
    required this.title,
    required this.icon,
    required this.color,
    required this.onTap,
  });
}

class FeatureGrid extends StatelessWidget {
  final List<FeatureItem> features;

  const FeatureGrid({
    super.key,
    required this.features,
  });

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
        childAspectRatio: 1,
      ),
      itemCount: features.length,
      itemBuilder: (context, index) {
        final feature = features[index];
        return Card(
          elevation: 1,
          child: InkWell(
            onTap: feature.onTap,
            borderRadius: BorderRadius.circular(8),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  feature.icon,
                  size: 32,
                  color: feature.color,
                ),
                const SizedBox(height: 8),
                Text(
                  feature.title,
                  style: Theme.of(context).textTheme.bodyMedium,
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        );
      },
    );
  }
} 