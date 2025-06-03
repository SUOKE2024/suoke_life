// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title HealthDataStorage
 * @dev 健康数据存储智能合约
 * 负责存储健康数据的哈希值和元数据，确保数据完整性和可追溯性
 */
contract HealthDataStorage is Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;
    
    // 数据记录计数器
    Counters.Counter private _recordIds;
    
    // 健康数据记录结构
    struct HealthRecord {
        uint256 id;
        address owner;
        bytes32 dataHash;
        string dataType;
        uint256 timestamp;
        string ipfsHash;
        bytes32 encryptionKeyHash;
        bool isActive;
        mapping(address => bool) authorizedUsers;
    }
    
    // 存储所有健康数据记录
    mapping(uint256 => HealthRecord) public healthRecords;
    
    // 用户的健康记录ID列表
    mapping(address => uint256[]) public userRecords;
    
    // 数据哈希到记录ID的映射
    mapping(bytes32 => uint256) public hashToRecordId;
    
    // 授权访问映射
    mapping(uint256 => mapping(address => bool)) public accessAuthorizations;
    
    // 事件定义
    event HealthDataStored(
        uint256 indexed recordId,
        address indexed owner,
        bytes32 indexed dataHash,
        string dataType,
        uint256 timestamp
    );
    
    event AccessGranted(
        uint256 indexed recordId,
        address indexed owner,
        address indexed grantee,
        uint256 timestamp
    );
    
    event AccessRevoked(
        uint256 indexed recordId,
        address indexed owner,
        address indexed grantee,
        uint256 timestamp
    );
    
    event HealthDataUpdated(
        uint256 indexed recordId,
        bytes32 indexed newDataHash,
        uint256 timestamp
    );
    
    /**
     * @dev 存储健康数据
     * @param _dataHash 数据哈希值
     * @param _dataType 数据类型
     * @param _ipfsHash IPFS哈希值
     * @param _encryptionKeyHash 加密密钥哈希
     */
    function storeHealthData(
        bytes32 _dataHash,
        string memory _dataType,
        string memory _ipfsHash,
        bytes32 _encryptionKeyHash
    ) external nonReentrant returns (uint256) {
        require(_dataHash != bytes32(0), "Data hash cannot be empty");
        require(bytes(_dataType).length > 0, "Data type cannot be empty");
        require(hashToRecordId[_dataHash] == 0, "Data hash already exists");
        
        _recordIds.increment();
        uint256 recordId = _recordIds.current();
        
        HealthRecord storage record = healthRecords[recordId];
        record.id = recordId;
        record.owner = msg.sender;
        record.dataHash = _dataHash;
        record.dataType = _dataType;
        record.timestamp = block.timestamp;
        record.ipfsHash = _ipfsHash;
        record.encryptionKeyHash = _encryptionKeyHash;
        record.isActive = true;
        
        // 添加到用户记录列表
        userRecords[msg.sender].push(recordId);
        
        // 建立哈希到ID的映射
        hashToRecordId[_dataHash] = recordId;
        
        emit HealthDataStored(recordId, msg.sender, _dataHash, _dataType, block.timestamp);
        
        return recordId;
    }
    
    /**
     * @dev 验证健康数据完整性
     * @param _recordId 记录ID
     * @param _dataHash 要验证的数据哈希
     */
    function verifyHealthData(uint256 _recordId, bytes32 _dataHash) 
        external 
        view 
        returns (bool) 
    {
        require(_recordId > 0 && _recordId <= _recordIds.current(), "Invalid record ID");
        
        HealthRecord storage record = healthRecords[_recordId];
        return record.isActive && record.dataHash == _dataHash;
    }
    
    /**
     * @dev 授权访问健康数据
     * @param _recordId 记录ID
     * @param _grantee 被授权者地址
     */
    function grantAccess(uint256 _recordId, address _grantee) 
        external 
        nonReentrant 
    {
        require(_recordId > 0 && _recordId <= _recordIds.current(), "Invalid record ID");
        require(_grantee != address(0), "Invalid grantee address");
        
        HealthRecord storage record = healthRecords[_recordId];
        require(record.owner == msg.sender, "Only owner can grant access");
        require(record.isActive, "Record is not active");
        
        accessAuthorizations[_recordId][_grantee] = true;
        
        emit AccessGranted(_recordId, msg.sender, _grantee, block.timestamp);
    }
    
    /**
     * @dev 撤销访问授权
     * @param _recordId 记录ID
     * @param _grantee 被撤销者地址
     */
    function revokeAccess(uint256 _recordId, address _grantee) 
        external 
        nonReentrant 
    {
        require(_recordId > 0 && _recordId <= _recordIds.current(), "Invalid record ID");
        require(_grantee != address(0), "Invalid grantee address");
        
        HealthRecord storage record = healthRecords[_recordId];
        require(record.owner == msg.sender, "Only owner can revoke access");
        
        accessAuthorizations[_recordId][_grantee] = false;
        
        emit AccessRevoked(_recordId, msg.sender, _grantee, block.timestamp);
    }
    
    /**
     * @dev 检查访问权限
     * @param _recordId 记录ID
     * @param _user 用户地址
     */
    function hasAccess(uint256 _recordId, address _user) 
        external 
        view 
        returns (bool) 
    {
        require(_recordId > 0 && _recordId <= _recordIds.current(), "Invalid record ID");
        
        HealthRecord storage record = healthRecords[_recordId];
        
        // 所有者总是有访问权限
        if (record.owner == _user) {
            return true;
        }
        
        // 检查授权访问
        return accessAuthorizations[_recordId][_user];
    }
    
    /**
     * @dev 获取用户的健康记录数量
     * @param _user 用户地址
     */
    function getUserRecordCount(address _user) 
        external 
        view 
        returns (uint256) 
    {
        return userRecords[_user].length;
    }
    
    /**
     * @dev 获取用户的健康记录ID列表
     * @param _user 用户地址
     * @param _offset 偏移量
     * @param _limit 限制数量
     */
    function getUserRecords(address _user, uint256 _offset, uint256 _limit) 
        external 
        view 
        returns (uint256[] memory) 
    {
        uint256[] storage records = userRecords[_user];
        require(_offset < records.length, "Offset out of bounds");
        
        uint256 end = _offset + _limit;
        if (end > records.length) {
            end = records.length;
        }
        
        uint256[] memory result = new uint256[](end - _offset);
        for (uint256 i = _offset; i < end; i++) {
            result[i - _offset] = records[i];
        }
        
        return result;
    }
    
    /**
     * @dev 获取健康记录详情
     * @param _recordId 记录ID
     */
    function getHealthRecord(uint256 _recordId) 
        external 
        view 
        returns (
            uint256 id,
            address owner,
            bytes32 dataHash,
            string memory dataType,
            uint256 timestamp,
            string memory ipfsHash,
            bool isActive
        ) 
    {
        require(_recordId > 0 && _recordId <= _recordIds.current(), "Invalid record ID");
        
        HealthRecord storage record = healthRecords[_recordId];
        
        return (
            record.id,
            record.owner,
            record.dataHash,
            record.dataType,
            record.timestamp,
            record.ipfsHash,
            record.isActive
        );
    }
    
    /**
     * @dev 更新健康数据（仅限所有者）
     * @param _recordId 记录ID
     * @param _newDataHash 新的数据哈希
     * @param _newIpfsHash 新的IPFS哈希
     */
    function updateHealthData(
        uint256 _recordId, 
        bytes32 _newDataHash, 
        string memory _newIpfsHash
    ) external nonReentrant {
        require(_recordId > 0 && _recordId <= _recordIds.current(), "Invalid record ID");
        require(_newDataHash != bytes32(0), "Data hash cannot be empty");
        
        HealthRecord storage record = healthRecords[_recordId];
        require(record.owner == msg.sender, "Only owner can update data");
        require(record.isActive, "Record is not active");
        
        // 更新哈希映射
        delete hashToRecordId[record.dataHash];
        hashToRecordId[_newDataHash] = _recordId;
        
        record.dataHash = _newDataHash;
        record.ipfsHash = _newIpfsHash;
        
        emit HealthDataUpdated(_recordId, _newDataHash, block.timestamp);
    }
    
    /**
     * @dev 获取总记录数
     */
    function getTotalRecords() external view returns (uint256) {
        return _recordIds.current();
    }
} 