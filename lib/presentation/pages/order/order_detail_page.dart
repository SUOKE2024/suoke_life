import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
import 'package:timeago/timeago.dart' as timeago;
import '../../../services/order_service.dart';
import '../../../components/order_timeline.dart';
import 'order_review_page.dart';
import 'logistics_tracking_page.dart';
import 'after_sale_page.dart';

class OrderDetailPage extends StatefulWidget {
  final String orderId;

  const OrderDetailPage({Key? key, required this.orderId}) : super(key: key);

  @override
  State<OrderDetailPage> createState() => _OrderDetailPageState();
}

class _OrderDetailPageState extends State<OrderDetailPage> {
  final OrderService _orderService = GetIt.instance<OrderService>();
  late Future<Order> _orderFuture;

  @override
  void initState() {
    super.initState();
    _orderFuture = _orderService.getOrderById(widget.orderId);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('订单详情'),
      ),
      body: FutureBuilder<Order>(
        future: _orderFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          
          if (snapshot.hasError) {
            return Center(child: Text('加载失败: ${snapshot.error}'));
          }

          final order = snapshot.data!;
          return SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildOrderStatus(order),
                _buildOrderInfo(order),
                _buildProductList(order),
                _buildAddressInfo(order),
                _buildPaymentInfo(order),
                _buildOrderTimeline(order),
                _buildActionButtons(order),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildOrderStatus(Order order) {
    return Container(
      padding: const EdgeInsets.all(16),
      color: Theme.of(context).primaryColor,
      child: Row(
        children: [
          Icon(
            _getStatusIcon(order.status),
            color: Colors.white,
            size: 32,
          ),
          const SizedBox(width: 16),
          Text(
            _getStatusText(order.status),
            style: const TextStyle(
              color: Colors.white,
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOrderInfo(Order order) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('订单编号: ${order.id}'),
          const SizedBox(height: 8),
          Text('创建时间: ${timeago.format(order.createdAt, locale: 'zh')}'),
        ],
      ),
    );
  }

  Widget _buildProductList(Order order) {
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: order.items.length,
      itemBuilder: (context, index) {
        final item = order.items[index];
        return ListTile(
          leading: Image.network(
            item.product.imageUrl,
            width: 60,
            height: 60,
            fit: BoxFit.cover,
          ),
          title: Text(item.product.name),
          subtitle: Text('数量: ${item.quantity}'),
          trailing: Text('¥${item.price.toStringAsFixed(2)}'),
        );
      },
    );
  }

  Widget _buildAddressInfo(Order order) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '收货信息',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text('${order.address.name} ${order.address.phone}'),
          Text(order.address.fullAddress),
        ],
      ),
    );
  }

  Widget _buildPaymentInfo(Order order) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '支付信息',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('支付方式'),
              Text(_getPaymentMethod(order.paymentMethod)),
            ],
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('商品总额'),
              Text('¥${order.totalAmount.toStringAsFixed(2)}'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildOrderTimeline(Order order) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '订单进度',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          OrderTimeline(statusChanges: order.statusChanges),
        ],
      ),
    );
  }

  Widget _buildActionButtons(Order order) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          if (order.trackingNumber != null && order.trackingCompany != null)
            OutlinedButton.icon(
              icon: const Icon(Icons.local_shipping),
              label: const Text('查看物流'),
              onPressed: () => _navigateToLogistics(order),
            ),
          const SizedBox(width: 8),
          if (order.status == OrderStatus.pending)
            ElevatedButton(
              onPressed: () => _cancelOrder(order),
              child: const Text('取消订单'),
            ),
          if (order.status == OrderStatus.shipped)
            ElevatedButton(
              onPressed: () => _confirmReceipt(order),
              child: const Text('确认收货'),
            ),
          if (order.status == OrderStatus.delivered && !order.isReviewed)
            ElevatedButton(
              onPressed: () => _navigateToReview(order),
              child: const Text('评价'),
            ),
          if (order.status == OrderStatus.delivered && !order.hasAfterSale)
            ElevatedButton(
              onPressed: () => _navigateToAfterSale(order),
              child: const Text('申请售后'),
            ),
        ],
      ),
    );
  }

  void _navigateToLogistics(Order order) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => LogisticsTrackingPage(
          orderId: order.id,
          trackingNumber: order.trackingNumber!,
          trackingCompany: order.trackingCompany!,
        ),
      ),
    );
  }

  void _navigateToAfterSale(Order order) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => AfterSalePage(
          orderId: order.id,
          items: order.items,
          totalAmount: order.totalAmount,
        ),
      ),
    ).then((value) {
      if (value == true) {
        setState(() {
          _orderFuture = _orderService.getOrderById(widget.orderId);
        });
      }
    });
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

  String _getPaymentMethod(String method) {
    switch (method) {
      case 'alipay':
        return '支付宝';
      case 'wechat':
        return '微信支付';
      default:
        return method;
    }
  }

  Future<void> _cancelOrder(Order order) async {
    try {
      await _orderService.cancelOrder(order.id);
      setState(() {
        _orderFuture = _orderService.getOrderById(widget.orderId);
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('订单已取消')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('取消订单失败: $e')),
        );
      }
    }
  }

  Future<void> _confirmReceipt(Order order) async {
    try {
      await _orderService.confirmReceipt(order.id);
      setState(() {
        _orderFuture = _orderService.getOrderById(widget.orderId);
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('已确认收货')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('确认收货失败: $e')),
        );
      }
    }
  }

  Future<void> _navigateToReview(Order order) async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => OrderReviewPage(
          orderId: order.id,
          items: order.items,
        ),
      ),
    );

    if (result == true) {
      setState(() {
        _orderFuture = _orderService.getOrderById(widget.orderId);
      });
    }
  }
} 