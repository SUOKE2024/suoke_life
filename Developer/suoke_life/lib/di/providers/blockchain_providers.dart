import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:suoke_life/core/blockchain/blockchain_service.dart';
import 'package:suoke_life/core/blockchain/web3_client.dart';
import 'package:suoke_life/data/repositories/blockchain_repository_impl.dart';
import 'package:suoke_life/domain/entities/health_data_token.dart';
import 'package:suoke_life/domain/entities/health_record.dart';
import 'package:suoke_life/domain/repositories/blockchain_repository.dart';

/// 区块链客户端提供者
final httpClientProvider = Provider<http.Client>((ref) {
  return http.Client();
});

/// 安全存储提供者
final secureStorageProvider = Provider<FlutterSecureStorage>((ref) {
  return const FlutterSecureStorage();
});

/// 区块链服务提供者
final blockchainServiceProvider = Provider<BlockchainService>((ref) {
  final httpClient = ref.watch(httpClientProvider);
  final secureStorage = ref.watch(secureStorageProvider);
  
  return Web3BlockchainService(secureStorage, httpClient);
});

/// 区块链初始化提供者
final blockchainInitProvider = FutureProvider<void>((ref) async {
  final service = ref.watch(blockchainServiceProvider);
  await service.initialize();
});

/// 当前钱包地址提供者
final currentWalletAddressProvider = FutureProvider<String?>((ref) async {
  final service = ref.watch(blockchainServiceProvider);
  return service.getCurrentAddress();
});

/// 代币余额提供者
final tokenBalanceProvider = FutureProvider<BigInt>((ref) async {
  final service = ref.watch(blockchainServiceProvider);
  
  // 确保有钱包地址
  final address = await service.getCurrentAddress();
  if (address == null) {
    throw Exception('未设置钱包地址');
  }
  
  return service.getTokenBalance();
});

/// 健康记录数量提供者
final healthRecordCountProvider = FutureProvider<int>((ref) async {
  final service = ref.watch(blockchainServiceProvider);
  
  // 确保有钱包地址
  final address = await service.getCurrentAddress();
  if (address == null) {
    throw Exception('未设置钱包地址');
  }
  
  return service.getUserRecordCount();
});

/// Web3客户端Provider
final web3ClientProvider = Provider<Web3Client>((ref) {
  final client = Web3Client();
  ref.onDispose(() {
    client.dispose();
  });
  return client;
});

/// 区块链存储库Provider
final blockchainRepositoryProvider = Provider<BlockchainRepository>((ref) {
  final web3Client = ref.watch(web3ClientProvider);
  return BlockchainRepositoryImpl(web3Client);
});

/// 当前账户地址Provider
final currentAccountAddressProvider = FutureProvider<String>((ref) async {
  final repository = ref.watch(blockchainRepositoryProvider);
  return await repository.getCurrentAccountAddress();
});

/// 账户ETH余额Provider
final accountEthBalanceProvider = FutureProvider.family<double, String>((ref, address) async {
  final repository = ref.watch(blockchainRepositoryProvider);
  return await repository.getAccountEthBalance(address);
});

/// 账户代币余额Provider
final accountTokenBalanceProvider = FutureProvider.family<BigInt, String>((ref, address) async {
  final repository = ref.watch(blockchainRepositoryProvider);
  return await repository.getTokenBalance(address);
});

/// 代币信息Provider
final tokenInfoProvider = FutureProvider<HealthDataToken>((ref) async {
  final repository = ref.watch(blockchainRepositoryProvider);
  return await repository.getTokenInfo();
});

/// 健康记录Provider
final healthRecordProvider = FutureProvider.family<HealthRecord, BigInt>((ref, recordId) async {
  final repository = ref.watch(blockchainRepositoryProvider);
  return await repository.getHealthRecord(recordId);
});

/// 用户健康记录列表Provider
final userHealthRecordsProvider = FutureProvider.family<List<HealthRecord>, String>((ref, userAddress) async {
  final repository = ref.watch(blockchainRepositoryProvider);
  return await repository.getUserHealthRecords(userAddress);
}); 