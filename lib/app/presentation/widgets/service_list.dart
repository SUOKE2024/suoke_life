import 'package:flutter/material.dart';
import '../../data/models/service.dart';

class ServiceList extends StatelessWidget {
  final String title;
  final List<Service> services;
  final Function(Service) onServiceTap;

  const ServiceList({
    Key? key,
    required this.title,
    required this.services,
    required this.onServiceTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 16),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            crossAxisSpacing: 16,
            mainAxisSpacing: 16,
            childAspectRatio: 1.2,
          ),
          itemCount: services.length,
          itemBuilder: (context, index) {
            final service = services[index];
            return Card(
              child: InkWell(
                onTap: () => onServiceTap(service),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Image(
                        image: service.imageUrl != null 
                          ? AssetImage(service.imageUrl!)
                          : const AssetImage('assets/images/default_service.png'),
                        height: 48,
                        width: 48,
                        errorBuilder: (context, error, stackTrace) {
                          return const Icon(Icons.image_not_supported);
                        },
                      ),
                      const SizedBox(height: 8),
                      Text(
                        service.title,
                        textAlign: TextAlign.center,
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ],
    );
  }
} 