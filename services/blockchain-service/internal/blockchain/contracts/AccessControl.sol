// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title AccessControl
 * @dev 健康数据访问控制合约，管理数据授权和访问权限
 */
contract AccessControl {
    // 访问级别枚举
    enum AccessLevel {
        NONE,   // 无权限
        READ,   // 只读权限
        WRITE,  // 读写权限
        FULL    // 完全权限(包括删除)
    }
    
    // 授权记录结构
    struct Authorization {
        string userId;              // 数据所有者
        string authorizedId;        // 被授权方ID
        string[] dataTypes;         // 授权的数据类型
        AccessLevel accessLevel;    // 访问级别
        uint256 issuedAt;           // 授权时间
        uint256 expirationTime;     // 过期时间 (0 表示永不过期)
        bool isActive;              // 是否有效
        string policyData;          // 额外的策略数据 (JSON格式)
    }
    
    // 存储授权记录
    mapping(bytes32 => Authorization) private authorizations;
    
    // 用户授权的索引 (userId => authorizationIds[])
    mapping(string => bytes32[]) private userAuthorizations;
    
    // 授权给用户的索引 (authorizedId => authorizationIds[])
    mapping(string => bytes32[]) private userAuthorizedAccess;
    
    // 事件定义
    event AccessGranted(
        bytes32 indexed authorizationId,
        string indexed userId,
        string authorizedId,
        uint8 accessLevel,
        uint256 expirationTime
    );
    
    event AccessRevoked(
        bytes32 indexed authorizationId,
        string indexed userId,
        string authorizedId,
        uint256 revocationTime,
        string reason
    );
    
    // 合约所有者
    address public owner;
    
    // 合约初始化
    constructor() {
        owner = msg.sender;
    }
    
    // 只允许合约所有者执行的修饰符
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    // 授权访问
    function grantAccess(
        string memory userId,
        string memory authorizedId,
        string[] memory dataTypes,
        uint8 accessLevel,
        uint256 expirationTime,
        string memory policyData
    ) public returns (bytes32) {
        // 验证参数
        require(bytes(userId).length > 0, "User ID cannot be empty");
        require(bytes(authorizedId).length > 0, "Authorized ID cannot be empty");
        require(dataTypes.length > 0, "Data types cannot be empty");
        require(accessLevel > uint8(AccessLevel.NONE) && accessLevel <= uint8(AccessLevel.FULL), "Invalid access level");
        
        // 生成授权ID
        bytes32 authorizationId = keccak256(
            abi.encodePacked(userId, authorizedId, block.timestamp, msg.sender)
        );
        
        // 创建授权记录
        Authorization memory auth = Authorization({
            userId: userId,
            authorizedId: authorizedId,
            dataTypes: dataTypes,
            accessLevel: AccessLevel(accessLevel),
            issuedAt: block.timestamp,
            expirationTime: expirationTime,
            isActive: true,
            policyData: policyData
        });
        
        // 存储授权记录
        authorizations[authorizationId] = auth;
        
        // 更新索引
        userAuthorizations[userId].push(authorizationId);
        userAuthorizedAccess[authorizedId].push(authorizationId);
        
        // 触发事件
        emit AccessGranted(
            authorizationId,
            userId,
            authorizedId,
            accessLevel,
            expirationTime
        );
        
        return authorizationId;
    }
    
    // 撤销授权
    function revokeAccess(
        bytes32 authorizationId,
        string memory revokerUserId,
        string memory reason
    ) public returns (bool) {
        // 检查授权是否存在
        require(authorizations[authorizationId].issuedAt > 0, "Authorization does not exist");
        
        // 获取授权记录
        Authorization storage auth = authorizations[authorizationId];
        
        // 验证撤销者是否是数据所有者或合约所有者
        require(
            keccak256(abi.encodePacked(auth.userId)) == keccak256(abi.encodePacked(revokerUserId)) || 
            msg.sender == owner,
            "Only data owner or contract owner can revoke access"
        );
        
        // 检查授权是否已经撤销
        require(auth.isActive, "Authorization already revoked");
        
        // 撤销授权
        auth.isActive = false;
        
        // 触发事件
        emit AccessRevoked(
            authorizationId,
            auth.userId,
            auth.authorizedId,
            block.timestamp,
            reason
        );
        
        return true;
    }
    
    // 检查访问权限
    function checkAccess(
        string memory userId,
        string memory accessorId,
        string memory dataType,
        uint8 requiredLevel
    ) public view returns (bool, bytes32) {
        // 获取被授权用户的所有授权
        bytes32[] memory userAccesses = userAuthorizedAccess[accessorId];
        
        // 遍历所有授权
        for (uint i = 0; i < userAccesses.length; i++) {
            bytes32 authId = userAccesses[i];
            Authorization memory auth = authorizations[authId];
            
            // 检查授权是否有效、未过期、数据所有者匹配
            if (auth.isActive && 
                (auth.expirationTime == 0 || auth.expirationTime > block.timestamp) &&
                keccak256(abi.encodePacked(auth.userId)) == keccak256(abi.encodePacked(userId))) {
                
                // 检查数据类型是否包含在授权中
                bool dataTypeFound = false;
                for (uint j = 0; j < auth.dataTypes.length; j++) {
                    if (keccak256(abi.encodePacked(auth.dataTypes[j])) == keccak256(abi.encodePacked(dataType)) ||
                        keccak256(abi.encodePacked(auth.dataTypes[j])) == keccak256(abi.encodePacked("all"))) {
                        dataTypeFound = true;
                        break;
                    }
                }
                
                // 如果数据类型匹配且访问级别足够
                if (dataTypeFound && uint8(auth.accessLevel) >= requiredLevel) {
                    return (true, authId);
                }
            }
        }
        
        // 没有找到有效的授权
        return (false, bytes32(0));
    }
    
    // 获取授权详情
    function getAuthorization(
        bytes32 authorizationId
    ) public view returns (
        string memory userId,
        string memory authorizedId,
        uint8 accessLevel,
        uint256 issuedAt,
        uint256 expirationTime,
        bool isActive,
        string memory policyData
    ) {
        // 检查授权是否存在
        require(authorizations[authorizationId].issuedAt > 0, "Authorization does not exist");
        
        // 获取授权记录
        Authorization memory auth = authorizations[authorizationId];
        
        return (
            auth.userId,
            auth.authorizedId,
            uint8(auth.accessLevel),
            auth.issuedAt,
            auth.expirationTime,
            auth.isActive,
            auth.policyData
        );
    }
    
    // 获取授权的数据类型
    function getAuthorizationDataTypes(
        bytes32 authorizationId
    ) public view returns (string[] memory) {
        // 检查授权是否存在
        require(authorizations[authorizationId].issuedAt > 0, "Authorization does not exist");
        
        // 返回数据类型数组
        return authorizations[authorizationId].dataTypes;
    }
    
    // 获取用户的所有授权ID
    function getUserAuthorizations(
        string memory userId
    ) public view returns (bytes32[] memory) {
        return userAuthorizations[userId];
    }
    
    // 获取授权给用户的所有授权ID
    function getUserAuthorizedAccess(
        string memory authorizedId
    ) public view returns (bytes32[] memory) {
        return userAuthorizedAccess[authorizedId];
    }
    
    // 批量检查授权是否已过期
    function batchCheckExpiredAuthorizations(
        bytes32[] memory authIds
    ) public view returns (bool[] memory) {
        bool[] memory results = new bool[](authIds.length);
        
        for (uint i = 0; i < authIds.length; i++) {
            if (authorizations[authIds[i]].issuedAt == 0) {
                // 授权不存在
                results[i] = false;
            } else {
                Authorization memory auth = authorizations[authIds[i]];
                // 检查授权是否已过期
                results[i] = auth.isActive && 
                            (auth.expirationTime == 0 || auth.expirationTime > block.timestamp);
            }
        }
        
        return results;
    }
    
    // 更新授权的过期时间
    function updateExpirationTime(
        bytes32 authorizationId,
        uint256 newExpirationTime
    ) public returns (bool) {
        // 检查授权是否存在
        require(authorizations[authorizationId].issuedAt > 0, "Authorization does not exist");
        
        // 获取授权记录
        Authorization storage auth = authorizations[authorizationId];
        
        // 验证调用者是否是数据所有者或合约所有者
        require(
            keccak256(abi.encodePacked(auth.userId)) == keccak256(abi.encodePacked(msg.sender)) || 
            msg.sender == owner,
            "Only data owner or contract owner can update expiration time"
        );
        
        // 检查授权是否已经撤销
        require(auth.isActive, "Authorization already revoked");
        
        // 更新过期时间
        auth.expirationTime = newExpirationTime;
        
        return true;
    }
} 