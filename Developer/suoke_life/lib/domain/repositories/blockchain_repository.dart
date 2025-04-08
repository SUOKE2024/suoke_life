import 'package:suoke_life/domain/entities/health_data_token.dart';
import 'package:suoke_life/domain/entities/health_record.dart';

/// 区块链存储库接口，定义与区块链交互的方法
abstract class BlockchainRepository {
  /// 获取当前账户地址
  Future<String> getCurrentAccountAddress();
  
  /// 获取账户以太坊余额
  Future<double> getAccountEthBalance(String address);
  
  /// 获取账户健康数据代币余额
  Future<BigInt> getTokenBalance(String address);
  
  /// 获取代币信息
  Future<HealthDataToken> getTokenInfo();
  
  /// 创建健康记录
  Future<String> createHealthRecord(String dataHash, String dataUrl);
  
  /// 共享健康记录给其他用户
  Future<String> shareHealthRecord(BigInt recordId, String toAddress);
  
  /// 获取健康记录
  Future<HealthRecord> getHealthRecord(BigInt recordId);
  
  /// 获取用户的所有健康记录
  Future<List<HealthRecord>> getUserHealthRecords(String userAddress);
} 