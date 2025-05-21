// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./HealthDataStorage.sol";
import "./ZKPVerifier.sol";
import "./AccessControl.sol";

/**
 * @title SuoKeLifeContractFactory
 * @dev 部署和管理SuoKeLife区块链健康数据相关合约的工厂合约
 */
contract SuoKeLifeContractFactory {
    // 合约地址存储
    address public healthDataStorageAddress;
    address public zkpVerifierAddress;
    address public accessControlAddress;
    
    // 合约实例
    HealthDataStorage private healthDataStorage;
    ZKPVerifier private zkpVerifier;
    AccessControl private accessControl;
    
    // 合约所有者
    address public owner;
    
    // 事件定义
    event ContractsDeployed(
        address healthDataStorageAddress,
        address zkpVerifierAddress,
        address accessControlAddress,
        uint256 deploymentTimestamp
    );
    
    // 合约初始化 - 创建所有所需合约
    constructor() {
        owner = msg.sender;
        
        // 部署所有合约
        deployContracts();
    }
    
    // 只允许合约所有者执行的修饰符
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    // 部署所有合约
    function deployContracts() public onlyOwner {
        // 部署健康数据存储合约
        healthDataStorage = new HealthDataStorage();
        healthDataStorageAddress = address(healthDataStorage);
        
        // 部署零知识证明验证合约
        zkpVerifier = new ZKPVerifier();
        zkpVerifierAddress = address(zkpVerifier);
        
        // 部署访问控制合约
        accessControl = new AccessControl();
        accessControlAddress = address(accessControl);
        
        // 触发事件
        emit ContractsDeployed(
            healthDataStorageAddress,
            zkpVerifierAddress,
            accessControlAddress,
            block.timestamp
        );
    }
    
    // 重新部署特定合约
    function redeployHealthDataStorage() public onlyOwner returns (address) {
        healthDataStorage = new HealthDataStorage();
        healthDataStorageAddress = address(healthDataStorage);
        return healthDataStorageAddress;
    }
    
    function redeployZKPVerifier() public onlyOwner returns (address) {
        zkpVerifier = new ZKPVerifier();
        zkpVerifierAddress = address(zkpVerifier);
        return zkpVerifierAddress;
    }
    
    function redeployAccessControl() public onlyOwner returns (address) {
        accessControl = new AccessControl();
        accessControlAddress = address(accessControl);
        return accessControlAddress;
    }
    
    // 获取当前合约地址
    function getContractAddresses() public view returns (
        address healthDataStorage,
        address zkpVerifier,
        address accessControl
    ) {
        return (
            healthDataStorageAddress,
            zkpVerifierAddress,
            accessControlAddress
        );
    }
    
    // 以下是便捷方法，直接通过工厂调用各个合约的核心功能
    
    // =============== 健康数据存储相关方法 ===============
    
    // 存储健康数据
    function storeHealthData(
        string memory userId,
        string memory dataType,
        bytes32 dataHash,
        string memory metadata
    ) public returns (bytes32) {
        return healthDataStorage.storeHealthData(userId, dataType, dataHash, metadata);
    }
    
    // 验证健康数据
    function verifyHealthData(
        bytes32 transactionId,
        bytes32 dataHash
    ) public view returns (bool, uint256) {
        return healthDataStorage.verifyHealthData(transactionId, dataHash);
    }
    
    // =============== 零知识证明验证相关方法 ===============
    
    // 设置验证器密钥
    function setVerificationKey(
        uint8 verifierType,
        bytes32 verificationKey
    ) public onlyOwner {
        zkpVerifier.setVerificationKey(verifierType, verificationKey);
    }
    
    // 验证零知识证明
    function verifyProof(
        string memory userId,
        string memory verifierId,
        uint8 verifierType,
        bytes calldata proof,
        bytes calldata publicInputs,
        string memory metadata
    ) public returns (bytes32, bool) {
        return zkpVerifier.verifyProof(userId, verifierId, verifierType, proof, publicInputs, metadata);
    }
    
    // =============== 访问控制相关方法 ===============
    
    // 授权访问
    function grantAccess(
        string memory userId,
        string memory authorizedId,
        string[] memory dataTypes,
        uint8 accessLevel,
        uint256 expirationTime,
        string memory policyData
    ) public returns (bytes32) {
        return accessControl.grantAccess(userId, authorizedId, dataTypes, accessLevel, expirationTime, policyData);
    }
    
    // 撤销授权
    function revokeAccess(
        bytes32 authorizationId,
        string memory revokerUserId,
        string memory reason
    ) public returns (bool) {
        return accessControl.revokeAccess(authorizationId, revokerUserId, reason);
    }
    
    // 检查访问权限
    function checkAccess(
        string memory userId,
        string memory accessorId,
        string memory dataType,
        uint8 requiredLevel
    ) public view returns (bool, bytes32) {
        return accessControl.checkAccess(userId, accessorId, dataType, requiredLevel);
    }
    
    // 在合约升级时转移所有权
    function transferOwnership(address newOwner) public onlyOwner {
        require(newOwner != address(0), "New owner cannot be zero address");
        owner = newOwner;
    }
} 