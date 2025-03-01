import 'package:flutter/material.dart';
import '../../domain/entities/health_service.dart';

class HealthServiceCard extends StatelessWidget {
  final HealthService service;
  final VoidCallback onTap;
  final bool isHorizontal;
  
  const HealthServiceCard({
    Key? key,
    required this.service,
    required this.onTap,
    this.isHorizontal = false,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return isHorizontal
        ? _buildHorizontalCard(context)
        : _buildVerticalCard(context);
  }
  
  Widget _buildVerticalCard(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 160,
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        clipBehavior: Clip.antiAlias,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildServiceImage(height: 100, width: double.infinity),
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildServiceTitle(context),
                  const SizedBox(height: 4),
                  _buildTagsRow(),
                  const SizedBox(height: 8),
                  _buildPriceRow(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildHorizontalCard(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 120,
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        clipBehavior: Clip.antiAlias,
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildServiceImage(height: 120, width: 120),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildServiceTitle(context),
                    const SizedBox(height: 4),
                    Expanded(
                      child: Text(
                        service.description,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          color: Theme.of(context).textTheme.bodySmall?.color,
                          fontSize: 12,
                        ),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        _buildTagsRow(),
                        const Spacer(),
                        _buildPriceTag(),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildServiceImage({required double height, required double width}) {
    if (service.imageUrl != null) {
      return SizedBox(
        height: height,
        width: width,
        child: Image.asset(
          service.imageUrl!,
          fit: BoxFit.cover,
          errorBuilder: (context, error, stackTrace) {
            return _buildPlaceholderImage(height: height, width: width);
          },
        ),
      );
    } else {
      return _buildPlaceholderImage(height: height, width: width);
    }
  }
  
  Widget _buildPlaceholderImage({required double height, required double width}) {
    return Container(
      height: height,
      width: width,
      color: Colors.grey[200],
      child: Center(
        child: Icon(
          service.icon,
          size: 40,
          color: Colors.grey[400],
        ),
      ),
    );
  }
  
  Widget _buildServiceTitle(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Text(
            service.name,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
        ),
        if (service.isPremium)
          const Icon(
            Icons.star,
            color: Colors.amber,
            size: 16,
          ),
      ],
    );
  }
  
  Widget _buildTagsRow() {
    if (service.tags.isEmpty) return const SizedBox.shrink();
    
    return Row(
      children: [
        for (int i = 0; i < service.tags.length && i < 2; i++)
          Padding(
            padding: EdgeInsets.only(right: i < service.tags.length - 1 ? 4 : 0),
            child: _buildTag(service.tags[i]),
          ),
      ],
    );
  }
  
  Widget _buildTag(String tag) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: Colors.blue.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        tag,
        style: const TextStyle(
          fontSize: 10,
          color: Colors.blue,
        ),
      ),
    );
  }
  
  Widget _buildPriceRow() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        _buildPriceTag(),
        Icon(
          Icons.arrow_forward_ios,
          size: 12,
          color: Colors.grey[400],
        ),
      ],
    );
  }
  
  Widget _buildPriceTag() {
    final bool isFree = service.price == 0;
    
    return Text(
      isFree ? '免费' : '¥${service.price.toStringAsFixed(1)}',
      style: TextStyle(
        fontWeight: FontWeight.bold,
        color: isFree ? Colors.green : Colors.orange,
        fontSize: 14,
      ),
    );
  }
} 