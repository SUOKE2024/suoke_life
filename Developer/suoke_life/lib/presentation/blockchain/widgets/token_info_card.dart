import 'package:flutter/material.dart';
import 'package:suoke_life/domain/entities/health_data_token.dart';

class TokenInfoCard extends StatelessWidget {
  final HealthDataToken token;

  const TokenInfoCard({Key? key, required this.token}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // 将BigInt转换为可读格式（假设代币有18位小数）
    final decimalFactor = BigInt.from(10).pow(18);
    final balanceDecimal = token.balance / decimalFactor;
    final totalSupplyDecimal = token.totalSupply / decimalFactor;

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  backgroundColor: const Color(0xFF35BB78).withAlpha(40),
                  child: Text(
                    token.symbol[0],
                    style: const TextStyle(
                      color: Color(0xFF35BB78),
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      token.name,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      token.symbol,
                      style: TextStyle(
                        color: Colors.grey.shade600,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const Divider(height: 32),
            _buildInfoRow('合约地址', token.address, isAddress: true),
            const SizedBox(height: 8),
            _buildInfoRow('代币余额', '${balanceDecimal.toStringAsFixed(4)} ${token.symbol}'),
            const SizedBox(height: 8),
            _buildInfoRow('总供应量', '${totalSupplyDecimal.toStringAsFixed(0)} ${token.symbol}'),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value, {bool isAddress = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontWeight: FontWeight.w500,
          ),
        ),
        Expanded(
          child: Text(
            isAddress ? '${value.substring(0, 6)}...${value.substring(value.length - 4)}' : value,
            style: const TextStyle(
              fontWeight: FontWeight.bold,
            ),
            textAlign: TextAlign.end,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }
} 