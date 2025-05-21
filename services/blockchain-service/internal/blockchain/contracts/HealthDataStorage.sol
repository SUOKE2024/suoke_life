// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title HealthDataStorage
 * @dev 健康数据存储合约，负责存储和验证健康数据的哈希值
 */
contract HealthDataStorage {
    // 健康数据记录结构
    struct HealthDataRecord {
        string userId;          // 用户ID
        string dataType;        // 数据类型
        bytes32 dataHash;       // 数据哈希
        uint256 timestamp;      // 时间戳
        bytes32 blockHash;      // 区块哈希
        string metadata;        // 元数据 (JSON格式)
        bool isDeleted;         // 是否已删除
    }
    
    // 存储健康数据记录 (交易ID => 数据记录)
    mapping(bytes32 => HealthDataRecord) private healthRecords;
    
    // 用户数据交易索引 (用户ID => 交易ID数组)
    mapping(string => bytes32[]) private userTransactions;
    
    // 用户数据类型索引 (用户ID_数据类型 => 交易ID数组)
    mapping(string => bytes32[]) private userDataTypeTransactions;
    
    // 事件定义
    event HealthDataStored(
        bytes32 indexed transactionId,
        string indexed userId,
        string dataType,
        bytes32 dataHash,
        uint256 timestamp
    );
    
    event HealthDataDeleted(
        bytes32 indexed transactionId,
        string indexed userId,
        uint256 timestamp,
        string reason
    );
    
    // 合约所有者
    address public owner;
    
    // 构造函数
    constructor() {
        owner = msg.sender;
    }
    
    // 仅限所有者修饰器
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    /**
     * 存储健康数据
     * 
     * @param userId 用户ID
     * @param dataType 数据类型
     * @param dataHash 数据哈希
     * @param metadata 元数据
     * @return 交易ID
     */
    function storeHealthData(
        string memory userId,
        string memory dataType,
        bytes32 dataHash,
        string memory metadata
    ) public returns (bytes32) {
        // 验证参数
        require(bytes(userId).length > 0, "User ID cannot be empty");
        require(bytes(dataType).length > 0, "Data type cannot be empty");
        require(dataHash != bytes32(0), "Data hash cannot be empty");
        
        // 生成交易ID
        bytes32 transactionId = keccak256(
            abi.encodePacked(userId, dataType, dataHash, block.timestamp, msg.sender)
        );
        
        // 确保交易ID不重复
        require(healthRecords[transactionId].timestamp == 0, "Transaction ID already exists");
        
        // 创建健康数据记录
        HealthDataRecord memory record = HealthDataRecord({
            userId: userId,
            dataType: dataType,
            dataHash: dataHash,
            timestamp: block.timestamp,
            blockHash: blockhash(block.number - 1),  // 获取上一个区块的哈希
            metadata: metadata,
            isDeleted: false
        });
        
        // 存储记录
        healthRecords[transactionId] = record;
        
        // 更新索引
        userTransactions[userId].push(transactionId);
        
        // 更新数据类型索引
        string memory userDataTypeKey = string(abi.encodePacked(userId, "_", dataType));
        userDataTypeTransactions[userDataTypeKey].push(transactionId);
        
        // 触发事件
        emit HealthDataStored(
            transactionId,
            userId,
            dataType,
            dataHash,
            block.timestamp
        );
        
        return transactionId;
    }
    
    /**
     * 验证健康数据
     * 
     * @param transactionId 交易ID
     * @param dataHash 要验证的数据哈希
     * @return valid 验证是否通过
     * @return timestamp 数据时间戳
     */
    function verifyHealthData(
        bytes32 transactionId,
        bytes32 dataHash
    ) public view returns (bool, uint256) {
        // 检查交易是否存在
        if (healthRecords[transactionId].timestamp == 0) {
            return (false, 0);
        }
        
        // 获取记录
        HealthDataRecord memory record = healthRecords[transactionId];
        
        // 检查是否已删除
        if (record.isDeleted) {
            return (false, record.timestamp);
        }
        
        // 验证数据哈希
        bool valid = record.dataHash == dataHash;
        
        return (valid, record.timestamp);
    }
    
    /**
     * 获取健康数据记录
     * 
     * @param transactionId 交易ID
     * @return 数据记录字段(用户ID, 数据类型, 数据哈希, 时间戳, 区块哈希, 元数据)
     */
    function getHealthDataRecord(
        bytes32 transactionId
    ) public view returns (
        string memory userId,
        string memory dataType,
        bytes32 dataHash,
        uint256 timestamp,
        bytes32 blockHash,
        string memory metadata,
        bool isDeleted
    ) {
        // 检查交易是否存在
        require(healthRecords[transactionId].timestamp > 0, "Transaction does not exist");
        
        // 获取记录
        HealthDataRecord memory record = healthRecords[transactionId];
        
        return (
            record.userId,
            record.dataType,
            record.dataHash,
            record.timestamp,
            record.blockHash,
            record.metadata,
            record.isDeleted
        );
    }
    
    /**
     * 获取用户的所有交易ID
     * 
     * @param userId 用户ID
     * @return 交易ID数组
     */
    function getUserDataTransactionIds(
        string memory userId
    ) public view returns (bytes32[] memory) {
        return userTransactions[userId];
    }
    
    /**
     * 获取用户特定数据类型的交易ID
     * 
     * @param userId 用户ID
     * @param dataType 数据类型
     * @return 交易ID数组
     */
    function getUserDataTypeTransactionIds(
        string memory userId,
        string memory dataType
    ) public view returns (bytes32[] memory) {
        string memory userDataTypeKey = string(abi.encodePacked(userId, "_", dataType));
        return userDataTypeTransactions[userDataTypeKey];
    }
    
    /**
     * 标记删除健康数据
     * 注意：区块链上数据无法真正删除，这只是标记为已删除
     * 
     * @param transactionId 交易ID
     * @param reason 删除原因
     * @return 操作是否成功
     */
    function markHealthDataDeleted(
        bytes32 transactionId,
        string memory reason
    ) public returns (bool) {
        // 检查交易是否存在
        require(healthRecords[transactionId].timestamp > 0, "Transaction does not exist");
        
        // 获取记录
        HealthDataRecord storage record = healthRecords[transactionId];
        
        // 验证调用者是否为合约所有者
        require(
            msg.sender == owner,
            "Only owner can delete health data"
        );
        
        // 检查是否已删除
        require(!record.isDeleted, "Data already deleted");
        
        // 标记为已删除
        record.isDeleted = true;
        
        // 触发事件
        emit HealthDataDeleted(
            transactionId,
            record.userId,
            block.timestamp,
            reason
        );
        
        return true;
    }
    
    /**
     * 批量获取健康数据状态
     * 
     * @param transactionIds 交易ID数组
     * @return 数据存在状态数组
     */
    function batchGetHealthDataStatus(
        bytes32[] memory transactionIds
    ) public view returns (bool[] memory) {
        bool[] memory statuses = new bool[](transactionIds.length);
        
        for (uint i = 0; i < transactionIds.length; i++) {
            bytes32 txId = transactionIds[i];
            if (healthRecords[txId].timestamp == 0 || healthRecords[txId].isDeleted) {
                statuses[i] = false;
            } else {
                statuses[i] = true;
            }
        }
        
        return statuses;
    }
    
    /**
     * 获取用户最近的健康数据记录数量
     * 
     * @param userId 用户ID
     * @return 记录数量
     */
    function getUserDataCount(
        string memory userId
    ) public view returns (uint256) {
        return userTransactions[userId].length;
    }
    
    /**
     * 转移合约所有权
     * 
     * @param newOwner 新所有者地址
     */
    function transferOwnership(address newOwner) public onlyOwner {
        require(newOwner != address(0), "New owner cannot be zero address");
        owner = newOwner;
    }
} 