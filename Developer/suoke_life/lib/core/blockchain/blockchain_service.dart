import 'dart:async';
import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:web3dart/web3dart.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:web_socket_channel/io.dart';

/// 区块链服务接口
abstract class BlockchainService {
  /// 初始化区块链服务
  Future<void> initialize();
  
  /// 获取当前账户地址
  Future<String?> getCurrentAddress();
  
  /// 设置当前使用的账户
  Future<void> setCurrentAddress(String privateKey);
  
  /// 获取代币余额
  Future<BigInt> getTokenBalance();
  
  /// 创建健康记录
  Future<String> createHealthRecord(String dataHash, String dataType, String metadata);
  
  /// 获取用户健康记录数量
  Future<int> getUserRecordCount();
  
  /// 获取特定索引的健康记录ID
  Future<BigInt> getRecordIdAtIndex(int index);
  
  /// 获取健康记录详情
  Future<Map<String, dynamic>> getHealthRecord(BigInt recordId);
  
  /// 共享健康记录给其他用户
  Future<String> shareHealthRecord(BigInt recordId, String targetAddress);
}

/// Web3区块链服务实现
class Web3BlockchainService implements BlockchainService {
  static const String _privateKeyKey = 'blockchain_private_key';
  static const String _rpcUrlKey = 'blockchain_rpc_url';
  static const String _wsUrlKey = 'blockchain_ws_url';
  static const String _chainIdKey = 'blockchain_chain_id';
  static const String _healthRecordAddressKey = 'health_record_contract_address';
  static const String _tokenAddressKey = 'token_contract_address';
  
  final FlutterSecureStorage _secureStorage;
  final http.Client _httpClient;
  
  late Web3Client _web3client;
  late String _rpcUrl;
  late String _wsUrl;
  late int _chainId;
  late EthereumAddress _healthRecordAddress;
  late EthereumAddress _tokenAddress;
  late Credentials _credentials;
  late DeployedContract _healthRecordContract;
  late DeployedContract _tokenContract;
  
  Web3BlockchainService(this._secureStorage, this._httpClient);
  
  @override
  Future<void> initialize() async {
    // 从安全存储中加载配置
    _rpcUrl = await _secureStorage.read(key: _rpcUrlKey) ?? 'http://127.0.0.1:8545';
    _wsUrl = await _secureStorage.read(key: _wsUrlKey) ?? 'ws://127.0.0.1:8545';
    _chainId = int.parse(await _secureStorage.read(key: _chainIdKey) ?? '1337');
    
    final healthRecordAddressString = await _secureStorage.read(key: _healthRecordAddressKey);
    final tokenAddressString = await _secureStorage.read(key: _tokenAddressKey);
    
    if (healthRecordAddressString == null || tokenAddressString == null) {
      throw Exception('合约地址未配置');
    }
    
    _healthRecordAddress = EthereumAddress.fromHex(healthRecordAddressString);
    _tokenAddress = EthereumAddress.fromHex(tokenAddressString);
    
    // 初始化Web3客户端
    _web3client = Web3Client(
      _rpcUrl,
      _httpClient,
      socketConnector: () => IOWebSocketChannel.connect(_wsUrl).cast<String>(),
    );
    
    // 加载合约ABI
    await _loadContracts();
    
    // 尝试加载凭证
    final privateKey = await _secureStorage.read(key: _privateKeyKey);
    if (privateKey != null) {
      await setCurrentAddress(privateKey);
    }
  }
  
  Future<void> _loadContracts() async {
    // 在实际应用中,应该从assets加载ABI文件
    final healthRecordAbi = await _loadAbiJson('assets/contracts/HealthRecord.json');
    final tokenAbi = await _loadAbiJson('assets/contracts/HealthDataToken.json');
    
    _healthRecordContract = DeployedContract(
      ContractAbi.fromJson(healthRecordAbi, 'HealthRecord'), 
      _healthRecordAddress
    );
    
    _tokenContract = DeployedContract(
      ContractAbi.fromJson(tokenAbi, 'HealthDataToken'), 
      _tokenAddress
    );
  }
  
  // 模拟加载ABI,实际应用中应该从资源文件加载
  Future<String> _loadAbiJson(String assetPath) async {
    // 这里简化处理,实际应用中应该使用rootBundle.loadString()加载
    if (assetPath.contains('HealthRecord')) {
      return '''
      [
        {
          "inputs": [
            {
              "internalType": "string",
              "name": "dataHash",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "dataType",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "encryptedMetadata",
              "type": "string"
            }
          ],
          "name": "createRecord",
          "outputs": [
            {
              "internalType": "uint256",
              "name": "",
              "type": "uint256"
            }
          ],
          "stateMutability": "nonpayable",
          "type": "function"
        },
        {
          "inputs": [
            {
              "internalType": "uint256",
              "name": "recordId",
              "type": "uint256"
            }
          ],
          "name": "getRecord",
          "outputs": [
            {
              "internalType": "string",
              "name": "dataHash",
              "type": "string"
            },
            {
              "internalType": "uint256",
              "name": "timestamp",
              "type": "uint256"
            },
            {
              "internalType": "string",
              "name": "dataType",
              "type": "string"
            },
            {
              "internalType": "bool",
              "name": "isShared",
              "type": "bool"
            }
          ],
          "stateMutability": "view",
          "type": "function"
        },
        {
          "inputs": [],
          "name": "getUserRecordCount",
          "outputs": [
            {
              "internalType": "uint256",
              "name": "",
              "type": "uint256"
            }
          ],
          "stateMutability": "view",
          "type": "function"
        },
        {
          "inputs": [
            {
              "internalType": "uint256",
              "name": "index",
              "type": "uint256"
            }
          ],
          "name": "getUserRecordIdAtIndex",
          "outputs": [
            {
              "internalType": "uint256",
              "name": "",
              "type": "uint256"
            }
          ],
          "stateMutability": "view",
          "type": "function"
        },
        {
          "inputs": [
            {
              "internalType": "uint256",
              "name": "recordId",
              "type": "uint256"
            },
            {
              "internalType": "address",
              "name": "user",
              "type": "address"
            }
          ],
          "name": "shareRecord",
          "outputs": [],
          "stateMutability": "nonpayable",
          "type": "function"
        }
      ]
      ''';
    } else {
      return '''
      [
        {
          "inputs": [
            {
              "internalType": "address",
              "name": "user",
              "type": "address"
            }
          ],
          "name": "balanceOf",
          "outputs": [
            {
              "internalType": "uint256",
              "name": "",
              "type": "uint256"
            }
          ],
          "stateMutability": "view",
          "type": "function"
        },
        {
          "inputs": [
            {
              "internalType": "address",
              "name": "user",
              "type": "address"
            }
          ],
          "name": "getTotalRewards",
          "outputs": [
            {
              "internalType": "uint256",
              "name": "",
              "type": "uint256"
            }
          ],
          "stateMutability": "view",
          "type": "function"
        }
      ]
      ''';
    }
  }
  
  @override
  Future<String?> getCurrentAddress() async {
    final privateKey = await _secureStorage.read(key: _privateKeyKey);
    if (privateKey == null) return null;
    
    final credentials = EthPrivateKey.fromHex(privateKey);
    return credentials.address.hex;
  }
  
  @override
  Future<void> setCurrentAddress(String privateKey) async {
    _credentials = EthPrivateKey.fromHex(privateKey);
    await _secureStorage.write(key: _privateKeyKey, value: privateKey);
  }
  
  @override
  Future<BigInt> getTokenBalance() async {
    final function = _tokenContract.function('balanceOf');
    final currentAddress = await _credentials.extractAddress();
    
    final result = await _web3client.call(
      contract: _tokenContract, 
      function: function, 
      params: [currentAddress]
    );
    
    return result.first as BigInt;
  }
  
  @override
  Future<String> createHealthRecord(String dataHash, String dataType, String metadata) async {
    final function = _healthRecordContract.function('createRecord');
    final currentAddress = await _credentials.extractAddress();
    
    final transaction = Transaction.callContract(
      contract: _healthRecordContract,
      function: function,
      parameters: [dataHash, dataType, metadata],
      from: currentAddress,
    );
    
    return _web3client.sendTransaction(
      _credentials, 
      transaction,
      chainId: _chainId
    );
  }
  
  @override
  Future<int> getUserRecordCount() async {
    final function = _healthRecordContract.function('getUserRecordCount');
    
    final result = await _web3client.call(
      contract: _healthRecordContract, 
      function: function, 
      params: []
    );
    
    return (result.first as BigInt).toInt();
  }
  
  @override
  Future<BigInt> getRecordIdAtIndex(int index) async {
    final function = _healthRecordContract.function('getUserRecordIdAtIndex');
    
    final result = await _web3client.call(
      contract: _healthRecordContract, 
      function: function, 
      params: [BigInt.from(index)]
    );
    
    return result.first as BigInt;
  }
  
  @override
  Future<Map<String, dynamic>> getHealthRecord(BigInt recordId) async {
    final function = _healthRecordContract.function('getRecord');
    
    final result = await _web3client.call(
      contract: _healthRecordContract, 
      function: function, 
      params: [recordId]
    );
    
    return {
      'dataHash': result[0] as String,
      'timestamp': (result[1] as BigInt).toInt(),
      'dataType': result[2] as String,
      'isShared': result[3] as bool,
    };
  }
  
  @override
  Future<String> shareHealthRecord(BigInt recordId, String targetAddress) async {
    final function = _healthRecordContract.function('shareRecord');
    final currentAddress = await _credentials.extractAddress();
    
    final transaction = Transaction.callContract(
      contract: _healthRecordContract,
      function: function,
      parameters: [recordId, EthereumAddress.fromHex(targetAddress)],
      from: currentAddress,
    );
    
    return _web3client.sendTransaction(
      _credentials, 
      transaction,
      chainId: _chainId
    );
  }
}

/// 区块链服务提供者
final blockchainServiceProvider = Provider<BlockchainService>((ref) {
  return Web3BlockchainService(
    const FlutterSecureStorage(),
    http.Client(),
  );
});

/// 初始化区块链服务
final blockchainInitProvider = FutureProvider<void>((ref) async {
  final service = ref.watch(blockchainServiceProvider);
  await service.initialize();
}); 