import 'package:flutter/material.dart';
import 'package:get/get.dart';

class ServiceItem extends StatelessWidget {
  final String title;
  final IconData icon;
  final Widget page;
  final String? description;

  const ServiceItem({
    Key? key,
    required this.title,
    required this.icon,
    required this.page,
    this.description,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(8),
      child: InkWell(
        onTap: () => Get.to(() => page),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 32),
              const SizedBox(height: 8),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              if (description != null)
                Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text(
                    description!,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
} 