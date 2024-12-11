import 'package:flutter/material.dart';
import 'package:timeline_tile/timeline_tile.dart';
import '../../../services/order_service.dart';

class OrderTimeline extends StatelessWidget {
  final List<OrderStatusChange> statusChanges;

  const OrderTimeline({Key? key, required this.statusChanges}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: statusChanges.length,
      itemBuilder: (context, index) {
        final statusChange = statusChanges[index];
        final isFirst = index == 0;
        final isLast = index == statusChanges.length - 1;

        return TimelineTile(
          isFirst: isFirst,
          isLast: isLast,
          beforeLineStyle: LineStyle(
            color: Theme.of(context).primaryColor,
          ),
          indicatorStyle: IndicatorStyle(
            width: 20,
            color: Theme.of(context).primaryColor,
            iconStyle: IconStyle(
              color: Colors.white,
              iconData: _getStatusIcon(statusChange.status),
            ),
          ),
          endChild: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _getStatusText(statusChange.status),
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  statusChange.timestamp.toString(),
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 14,
                  ),
                ),
                if (statusChange.description != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    statusChange.description!,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 14,
                    ),
                  ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  IconData _getStatusIcon(OrderStatus status) {
    switch (status) {
      case OrderStatus.pending:
        return Icons.pending;
      case OrderStatus.paid:
        return Icons.payment;
      case OrderStatus.shipped:
        return Icons.local_shipping;
      case OrderStatus.delivered:
        return Icons.check_circle;
      case OrderStatus.cancelled:
        return Icons.cancel;
      case OrderStatus.refunded:
        return Icons.replay;
    }
  }

  String _getStatusText(OrderStatus status) {
    switch (status) {
      case OrderStatus.pending:
        return '待付款';
      case OrderStatus.paid:
        return '已付款';
      case OrderStatus.shipped:
        return '配送中';
      case OrderStatus.delivered:
        return '已送达';
      case OrderStatus.cancelled:
        return '已取消';
      case OrderStatus.refunded:
        return '已退款';
    }
  }
} 