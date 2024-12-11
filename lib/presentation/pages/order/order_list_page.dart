import 'package:flutter/material.dart';
import '../../../services/order_service.dart';
import '../../../core/di/service_locator.dart';
import 'order_detail_page.dart';

class OrderListPage extends StatefulWidget {
  const OrderListPage({super.key});

  @override
  State<OrderListPage> createState() => _OrderListPageState();
}

class _OrderListPageState extends State<OrderListPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _orderService = serviceLocator<OrderService>();
  final List<Order> _orders = [];
  bool _isLoading = false;
  bool _hasMore = true;
  int _currentPage = 1;
  OrderStatus? _currentStatus;

  final List<Tab> _tabs = const [
    Tab(text: '全部'),
    Tab(text: '待付款'),
    Tab(text: '待发货'),
    Tab(text: '待收货'),
    Tab(text: '已完成'),
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: _tabs.length, vsync: this);
    _tabController.addListener(_handleTabChange);
    _loadOrders();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _handleTabChange() {
    if (!_tabController.indexIsChanging) {
      setState(() {
        switch (_tabController.index) {
          case 0:
            _currentStatus = null;
            break;
          case 1:
            _currentStatus = OrderStatus.pending;
            break;
          case 2:
            _currentStatus = OrderStatus.paid;
            break;
          case 3:
            _currentStatus = OrderStatus.shipping;
            break;
          case 4:
            _currentStatus = OrderStatus.completed;
            break;
        }
        _orders.clear();
        _currentPage = 1;
        _hasMore = true;
        _loadOrders();
      });
    }
  }

  Future<void> _loadOrders() async {
    if (_isLoading || !_hasMore) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final orders = await _orderService.getOrders(
        status: _currentStatus,
        page: _currentPage,
      );

      setState(() {
        if (orders.isEmpty) {
          _hasMore = false;
        } else {
          _orders.addAll(orders);
          _currentPage++;
        }
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('加载订单失败：$e')),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _refreshOrders() async {
    setState(() {
      _orders.clear();
      _currentPage = 1;
      _hasMore = true;
    });
    await _loadOrders();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('我的订单'),
        centerTitle: true,
        bottom: TabBar(
          controller: _tabController,
          tabs: _tabs,
          isScrollable: true,
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: List.generate(
          _tabs.length,
          (index) => OrderListView(
            orders: _orders,
            isLoading: _isLoading,
            hasMore: _hasMore,
            onRefresh: _refreshOrders,
            onLoadMore: _loadOrders,
          ),
        ),
      ),
    );
  }
}

class OrderListView extends StatelessWidget {
  final List<Order> orders;
  final bool isLoading;
  final bool hasMore;
  final VoidCallback onLoadMore;
  final Future<void> Function() onRefresh;

  const OrderListView({
    super.key,
    required this.orders,
    required this.isLoading,
    required this.hasMore,
    required this.onLoadMore,
    required this.onRefresh,
  });

  @override
  Widget build(BuildContext context) {
    if (orders.isEmpty && !isLoading) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.receipt_long,
              size: 64,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            Text(
              '暂无订单',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: onRefresh,
      child: NotificationListener<ScrollNotification>(
        onNotification: (notification) {
          if (notification is ScrollEndNotification) {
            if (notification.metrics.extentAfter == 0 && !isLoading && hasMore) {
              onLoadMore();
            }
          }
          return false;
        },
        child: ListView.separated(
          padding: const EdgeInsets.all(16),
          itemCount: orders.length + (hasMore ? 1 : 0),
          separatorBuilder: (context, index) => const SizedBox(height: 16),
          itemBuilder: (context, index) {
            if (index == orders.length) {
              return Center(
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  child: hasMore
                      ? const CircularProgressIndicator()
                      : Text(
                          '没有更多订单了',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[600],
                          ),
                        ),
                ),
              );
            }

            final order = orders[index];
            return OrderCard(order: order);
          },
        ),
      ),
    );
  }
}

class OrderCard extends StatelessWidget {
  final Order order;

  const OrderCard({
    super.key,
    required this.order,
  });

  String _getStatusText(OrderStatus status) {
    switch (status) {
      case OrderStatus.pending:
        return '待付款';
      case OrderStatus.paid:
        return '待发货';
      case OrderStatus.processing:
        return '处理中';
      case OrderStatus.shipping:
        return '配送中';
      case OrderStatus.delivered:
        return '待收货';
      case OrderStatus.completed:
        return '已完成';
      case OrderStatus.cancelled:
        return '已取消';
      case OrderStatus.refunding:
        return '退款中';
      case OrderStatus.refunded:
        return '已退款';
    }
  }

  Color _getStatusColor(OrderStatus status) {
    switch (status) {
      case OrderStatus.pending:
        return Colors.orange;
      case OrderStatus.paid:
        return Colors.blue;
      case OrderStatus.processing:
        return Colors.blue;
      case OrderStatus.shipping:
        return Colors.purple;
      case OrderStatus.delivered:
        return Colors.green;
      case OrderStatus.completed:
        return Colors.grey;
      case OrderStatus.cancelled:
        return Colors.red;
      case OrderStatus.refunding:
        return Colors.orange;
      case OrderStatus.refunded:
        return Colors.red;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => OrderDetailPage(orderId: order.id),
            ),
          );
        },
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 订单头部
              Row(
                children: [
                  Text(
                    '订单号：${order.id}',
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const Spacer(),
                  Text(
                    _getStatusText(order.status),
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                      color: _getStatusColor(order.status),
                    ),
                  ),
                ],
              ),
              const Divider(height: 16),

              // 商品列表
              ...List.generate(
                order.items.length > 3 ? 3 : order.items.length,
                (index) {
                  final item = order.items[index];
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Row(
                      children: [
                        ClipRRect(
                          borderRadius: BorderRadius.circular(4),
                          child: Image.network(
                            item.imageUrl,
                            width: 60,
                            height: 60,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) {
                              return Container(
                                width: 60,
                                height: 60,
                                color: Colors.grey[200],
                                child: const Icon(
                                  Icons.image,
                                  color: Colors.grey,
                                ),
                              );
                            },
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                item.name,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                              Text(
                                item.specification,
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey[600],
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 8),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text(
                              '¥${item.price.toStringAsFixed(2)}',
                              style: const TextStyle(
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                            Text(
                              'x${item.quantity}',
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey[600],
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  );
                },
              ),
              if (order.items.length > 3)
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Text(
                    '共${order.items.length}件商品',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                ),

              const Divider(height: 16),

              // 订单底部
              Row(
                children: [
                  Text(
                    '${order.createTime.year}-${order.createTime.month}-${order.createTime.day} ${order.createTime.hour}:${order.createTime.minute}',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                  const Spacer(),
                  Text(
                    '实付：',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                  Text(
                    '¥${order.totalAmount.toStringAsFixed(2)}',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),

              // 订单操作按钮
              if (order.status == OrderStatus.pending ||
                  order.status == OrderStatus.delivered)
                Padding(
                  padding: const EdgeInsets.only(top: 16),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      if (order.status == OrderStatus.pending) ...[
                        OutlinedButton(
                          onPressed: () {
                            // TODO: 实现取消订单功能
                          },
                          child: const Text('取消订单'),
                        ),
                        const SizedBox(width: 16),
                        FilledButton(
                          onPressed: () {
                            // TODO: 实现去支付功能
                          },
                          child: const Text('去支付'),
                        ),
                      ],
                      if (order.status == OrderStatus.delivered)
                        FilledButton(
                          onPressed: () {
                            // TODO: 实现确认收货功能
                          },
                          child: const Text('确认收货'),
                        ),
                    ],
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
} 