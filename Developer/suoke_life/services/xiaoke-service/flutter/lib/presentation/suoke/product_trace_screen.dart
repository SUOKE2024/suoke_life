import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_colors.dart';
import '../../core/widgets/animated_gradient_card.dart';
import '../../data/models/supply_chain_model.dart';
import '../../di/providers/supply_chain_providers.dart';

class ProductTraceScreen extends ConsumerStatefulWidget {
  final String qrCodeId;
  
  const ProductTraceScreen({Key? key, required this.qrCodeId}) : super(key: key);

  @override
  ConsumerState<ProductTraceScreen> createState() => _ProductTraceScreenState();
}

class _ProductTraceScreenState extends ConsumerState<ProductTraceScreen> {
  late Future<ProductTraceabilityModel> _traceabilityFuture;
  
  @override
  void initState() {
    super.initState();
    _traceabilityFuture = ref.read(traceabilityRepositoryProvider).getProductTraceability(widget.qrCodeId);
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('产品溯源'),
        backgroundColor: AppColors.SUOKE_GREEN,
      ),
      body: FutureBuilder<ProductTraceabilityModel>(
        future: _traceabilityFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          
          if (snapshot.hasError) {
            return Center(
              child: Text('加载失败: ${snapshot.error}', 
                style: const TextStyle(color: Colors.red))
            );
          }
          
          final data = snapshot.data!;
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildProductInfo(data),
                const SizedBox(height: 16),
                _buildJourneyInfo(data),
                const SizedBox(height: 16),
                _buildKeyEvents(data),
                const SizedBox(height: 16),
                _buildCertificationInfo(data),
                const SizedBox(height: 24),
                _buildRiskPredictions(data.product['id']),
              ],
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: AppColors.SUOKE_ORANGE,
        child: const Icon(Icons.share),
        onPressed: () {
          // 分享产品溯源信息
        },
      ),
    );
  }
  
  Widget _buildProductInfo(ProductTraceabilityModel data) {
    return AnimatedGradientCard(
      colors: const [Color(0xFF35BB78), Color(0xFF2E9D66)],
      borderRadius: 16,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              data.product['name'],
              style: const TextStyle(
                color: Colors.white,
                fontSize: 22,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '产品ID: ${data.product['id']}',
              style: const TextStyle(color: Colors.white70),
            ),
            if (data.product['batchId'] != null) ...[
              const SizedBox(height: 4),
              Text(
                '批次: ${data.product['batchId']}',
                style: const TextStyle(color: Colors.white70),
              ),
            ],
            const SizedBox(height: 12),
            Row(
              children: [
                const Icon(Icons.qr_code, color: Colors.white70, size: 16),
                const SizedBox(width: 8),
                Text(
                  '扫描时间: ${_formatDateTime(data.scanInfo['scanTime'])}',
                  style: const TextStyle(color: Colors.white70, fontSize: 12),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildJourneyInfo(ProductTraceabilityModel data) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '供应链旅程',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Text('当前阶段: ${data.journey['currentStage']}'),
            const SizedBox(height: 16),
            ...data.journey['stages'].map<Widget>((stage) {
              final bool isCompleted = stage['status'] == '已完成';
              return Padding(
                padding: const EdgeInsets.only(bottom: 12.0),
                child: Row(
                  children: [
                    Container(
                      width: 24,
                      height: 24,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: isCompleted ? AppColors.SUOKE_GREEN : Colors.grey,
                      ),
                      child: isCompleted 
                        ? const Icon(Icons.check, color: Colors.white, size: 16)
                        : null,
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            stage['name'],
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          Text(
                            '${stage['status']} · ${stage['date']}',
                            style: TextStyle(
                              color: isCompleted ? Colors.black54 : Colors.orange,
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }
  
  Widget _buildKeyEvents(ProductTraceabilityModel data) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '关键事件',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            ...data.keyEvents.map<Widget>((event) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 16.0),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.event_note, color: AppColors.SUOKE_GREEN),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            event['type'],
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 4),
                          Text(event['description'] ?? ''),
                          const SizedBox(height: 4),
                          Text(
                            '${event['date']} · ${event['location']}',
                            style: const TextStyle(
                              color: Colors.black54,
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }
  
  Widget _buildCertificationInfo(ProductTraceabilityModel data) {
    final isVerified = data.certification['verified'] as bool;
    
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '区块链认证',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Icon(
                  isVerified ? Icons.verified : Icons.gpp_maybe,
                  color: isVerified ? AppColors.SUOKE_GREEN : Colors.orange,
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        isVerified ? '已通过区块链验证' : '未验证',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: isVerified ? AppColors.SUOKE_GREEN : Colors.orange,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '上次验证: ${data.certification['lastVerified']}',
                        style: const TextStyle(color: Colors.black54, fontSize: 12),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                primary: Colors.white,
                onPrimary: AppColors.SUOKE_GREEN,
                side: const BorderSide(color: AppColors.SUOKE_GREEN),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
              onPressed: () {
                // 查看详细认证信息
              },
              child: const Text('查看区块链证书'),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildRiskPredictions(String productId) {
    return FutureBuilder<List<SupplyChainRiskModel>>(
      future: ref.read(riskPredictionProvider(productId).future),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }
        
        if (snapshot.hasError) {
          return const SizedBox.shrink();
        }
        
        final risks = snapshot.data!;
        if (risks.isEmpty) {
          return const SizedBox.shrink();
        }
        
        return Card(
          elevation: 2,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'AI风险预测',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                ...risks.map<Widget>((risk) {
                  final riskColor = _getRiskColor(risk.severity);
                  
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.warning_amber_rounded, color: riskColor),
                            const SizedBox(width: 8),
                            Text(
                              _getRiskChineseName(risk.type),
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: riskColor,
                              ),
                            ),
                            const Spacer(),
                            Text(
                              '风险指数: ${(risk.probability * 10).toStringAsFixed(1)}',
                              style: TextStyle(color: riskColor),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(risk.description),
                        const SizedBox(height: 8),
                        Wrap(
                          spacing: 8,
                          children: risk.suggestedActions.map((action) {
                            return Chip(
                              label: Text(action, style: const TextStyle(fontSize: 12)),
                              backgroundColor: Colors.grey.withAlpha(30),
                            );
                          }).toList(),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '预计时间窗口: ${risk.expectedTimeframe}',
                          style: const TextStyle(color: Colors.black54, fontSize: 12),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ],
            ),
          ),
        );
      },
    );
  }
  
  Color _getRiskColor(int severity) {
    if (severity >= 8) return Colors.red;
    if (severity >= 5) return Colors.orange;
    return Colors.yellow.shade700;
  }
  
  String _getRiskChineseName(String riskType) {
    final riskNames = {
      'quality_degradation': '质量下降风险',
      'delivery_delay': '配送延迟风险',
      'spoilage_risk': '变质风险',
      'systematic_quality_issue': '系统性质量风险',
      'weather_disruption': '天气影响风险',
    };
    
    return riskNames[riskType] ?? riskType;
  }
  
  String _formatDateTime(String isoString) {
    final date = DateTime.parse(isoString);
    return '${date.year}年${date.month}月${date.day}日 ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
  }
}