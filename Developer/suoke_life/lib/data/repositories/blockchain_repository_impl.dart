import 'package:suoke_life/core/blockchain/web3_client.dart';
import 'package:suoke_life/domain/entities/health_data_token.dart';
import 'package:suoke_life/domain/entities/health_record.dart';
import 'package:suoke_life/domain/repositories/blockchain_repository.dart';
import 'package:web3dart/web3dart.dart';

/// 区块链存储库实现
class BlockchainRepositoryImpl implements BlockchainRepository {
  final Web3Client _web3Client;
  
  BlockchainRepositoryImpl(this._web3Client);
  
  @override
  Future<String> getCurrentAccountAddress() async {
    return await _web3Client.getDefaultAccountAddress();
  }
  
  @override
  Future<double> getAccountEthBalance(String address) async {
    final balance = await _web3Client.getAccountBalance(address);
    // 将Wei转换为ETH（1 ETH = 10^18 Wei）
    return balance.getValueInUnit(EtherUnit.ether);
  }
  
  @override
  Future<BigInt> getTokenBalance(String address) async {
    return await _web3Client.getTokenBalance(address);
  }
  
  @override
  Future<HealthDataToken> getTokenInfo() async {
    // 获取当前账户地址
    final address = await getCurrentAccountAddress();
    
    // 获取代币余额
    final balance = await getTokenBalance(address);
    
    // 获取合约实例后，可以从合约获取名称、符号和总供应量
    // 这里暂时使用硬编码，实际应该从合约读取
    return HealthDataToken(
      address: '0x4a58DE0Ec653a049ebc37dE6b063841d58D50Aee',
      name: 'Health Data Token',
      symbol: 'HDT',
      totalSupply: BigInt.from(1000000) * BigInt.from(10).pow(18),
      balance: balance,
    );
  }
  
  @override
  Future<String> createHealthRecord(String dataHash, String dataUrl) async {
    return await _web3Client.createHealthRecord(dataHash, dataUrl);
  }
  
  @override
  Future<String> shareHealthRecord(BigInt recordId, String toAddress) async {
    return await _web3Client.shareHealthRecord(recordId, toAddress);
  }
  
  @override
  Future<HealthRecord> getHealthRecord(BigInt recordId) async {
    final result = await _web3Client.getHealthRecord(recordId);
    
    // 解析合约返回的结果
    final owner = result[0] as String;
    final dataHash = result[1] as String;
    final dataUrl = result[2] as String;
    final timestamp = result[3] as BigInt;
    final isShared = result[4] as bool;
    final authorizedUsers = (result[5] as List<dynamic>).cast<String>();
    
    return HealthRecord(
      id: recordId,
      owner: owner,
      dataHash: dataHash,
      dataUrl: dataUrl,
      timestamp: timestamp,
      isShared: isShared,
      authorizedUsers: authorizedUsers,
    );
  }
  
  @override
  Future<List<HealthRecord>> getUserHealthRecords(String userAddress) async {
    // 创建一个空列表，用于存储健康记录
    final records = <HealthRecord>[];
    
    try {
      // 首先从合约获取当前账户地址
      final currentAddress = await getCurrentAccountAddress();
      
      // 为演示目的，我们创建几条模拟数据（实际应用中应该从合约获取）
      if (userAddress == currentAddress) {
        // 添加一些测试数据，仅当用户查看自己的记录时
        records.add(
          HealthRecord(
            id: BigInt.from(1),
            owner: userAddress,
            dataHash: "0x7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9",
            dataUrl: "https://ipfs.io/ipfs/QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D",
            timestamp: BigInt.from(DateTime.now().millisecondsSinceEpoch ~/ 1000 - 86400 * 3),
            isShared: true,
            authorizedUsers: ["0x1234567890123456789012345678901234567890", "0x0987654321098765432109876543210987654321"],
          ),
        );
        
        records.add(
          HealthRecord(
            id: BigInt.from(2),
            owner: userAddress,
            dataHash: "0x1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b",
            dataUrl: "https://ipfs.io/ipfs/QmW2WQi7j6c7UgJTarActp7tDNikE4B2qXtFCfLPdsgaTQ",
            timestamp: BigInt.from(DateTime.now().millisecondsSinceEpoch ~/ 1000 - 86400),
            isShared: false,
            authorizedUsers: [],
          ),
        );
        
        records.add(
          HealthRecord(
            id: BigInt.from(3),
            owner: userAddress,
            dataHash: "0x3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d",
            dataUrl: "https://ipfs.io/ipfs/QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco",
            timestamp: BigInt.from(DateTime.now().millisecondsSinceEpoch ~/ 1000 - 3600),
            isShared: true,
            authorizedUsers: ["0x5678901234567890123456789012345678901234"],
          ),
        );
      }
      
      // 实际实现中，应该使用以下逻辑：
      // 1. 从合约获取用户记录的数量
      // 2. 循环获取每条记录的ID
      // 3. 根据ID获取记录详情
      // 4. 将记录添加到列表中
      
      return records;
    } catch (e) {
      // 发生错误时返回空列表
      print('获取健康记录失败: $e');
      return [];
    }
  }
}