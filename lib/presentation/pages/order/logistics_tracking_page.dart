import 'package:flutter/material.dart';
import 'package:timeline_tile/timeline_tile.dart';
import '../../../services/order_service.dart';

class LogisticsTrackingPage extends StatefulWidget {
  final String orderId;
  final String trackingNumber;
  final String trackingCompany;

  const LogisticsTrackingPage({
    Key? key,
    required this.orderId,
    required this.trackingNumber,
    required this.trackingCompany,
  }) : super(key: key);

  @override
  State<LogisticsTrackingPage> createState() => _LogisticsTrackingPageState();
}

class _LogisticsTrackingPageState extends State<LogisticsTrackingPage> {
  late Future<List<LogisticsInfo>> _logisticsFuture;
  Timer? _refreshTimer;

  @override
  void initState() {
    super.initState();
    _logisticsFuture = _fetchLogisticsInfo();
    // 每3分钟自动刷新一次物流信息
    _refreshTimer = Timer.periodic(const Duration(minutes: 3), (_) {
      if (mounted) {
        _refreshLogistics();
      }
    });
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  Future<List<LogisticsInfo>> _fetchLogisticsInfo() {
    return OrderService().getLogisticsInfo(
      trackingNumber: widget.trackingNumber,
      trackingCompany: widget.trackingCompany,
    );
  }

  Future<void> _refreshLogistics() async {
    setState(() {
      _logisticsFuture = _fetchLogisticsInfo();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('物流跟踪'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _refreshLogistics,
          ),
        ],
      ),
      body: Column(
        children: [
          _buildTrackingHeader(),
          Expanded(
            child: FutureBuilder<List<LogisticsInfo>>(
              future: _logisticsFuture,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(child: CircularProgressIndicator());
                }

                if (snapshot.hasError) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text('加载失败: ${snapshot.error}'),
                        ElevatedButton(
                          onPressed: _refreshLogistics,
                          child: const Text('重试'),
                        ),
                      ],
                    ),
                  );
                }

                final logistics = snapshot.data!;
                return _buildLogisticsTimeline(logistics);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTrackingHeader() {
    return Container(
      padding: const EdgeInsets.all(16),
      color: Colors.white,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Image.asset(
                'assets/images/logistics/${widget.trackingCompany.toLowerCase()}.png',
                width: 40,
                height: 40,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.trackingCompany,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '运单号：${widget.trackingNumber}',
                      style: TextStyle(
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
              IconButton(
                icon: const Icon(Icons.copy),
                onPressed: () {
                  Clipboard.setData(
                    ClipboardData(text: widget.trackingNumber),
                  );
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('运单号已复制')),
                  );
                },
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildLogisticsTimeline(List<LogisticsInfo> logistics) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: logistics.length,
      itemBuilder: (context, index) {
        final info = logistics[index];
        final isFirst = index == 0;
        final isLast = index == logistics.length - 1;

        return TimelineTile(
          isFirst: isFirst,
          isLast: isLast,
          beforeLineStyle: LineStyle(
            color: isFirst ? Theme.of(context).primaryColor : Colors.grey[300]!,
          ),
          indicatorStyle: IndicatorStyle(
            width: 20,
            color: isFirst ? Theme.of(context).primaryColor : Colors.grey[300]!,
            iconStyle: IconStyle(
              color: Colors.white,
              iconData: _getLogisticsIcon(info.status),
            ),
          ),
          endChild: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  info.description,
                  style: TextStyle(
                    fontSize: 14,
                    color: isFirst ? Colors.black : Colors.grey[600],
                    fontWeight: isFirst ? FontWeight.bold : FontWeight.normal,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  info.time.toString(),
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
                if (info.location != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    info.location!,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
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

  IconData _getLogisticsIcon(LogisticsStatus status) {
    switch (status) {
      case LogisticsStatus.collected:
        return Icons.inventory;
      case LogisticsStatus.inTransit:
        return Icons.local_shipping;
      case LogisticsStatus.delivering:
        return Icons.delivery_dining;
      case LogisticsStatus.delivered:
        return Icons.check_circle;
      case LogisticsStatus.exception:
        return Icons.error;
      case LogisticsStatus.returning:
        return Icons.assignment_return;
      default:
        return Icons.local_shipping;
    }
  }
} 