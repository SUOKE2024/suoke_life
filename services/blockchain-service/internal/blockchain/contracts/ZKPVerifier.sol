// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title ZKPVerifier
 * @dev 零知识证明验证合约，支持多种验证器类型，用于验证健康数据的特定属性而不暴露原始数据
 */
contract ZKPVerifier {
    // 验证器类型枚举（对应于不同类型的零知识证明）
    enum VerifierType {
        GENERIC,      // 0: 通用验证器
        INQUIRY,      // 1: 问诊数据验证器
        LISTEN,       // 2: 闻诊数据验证器
        LOOK,         // 3: 望诊数据验证器
        PALPATION,    // 4: 切诊数据验证器
        VITAL_SIGNS,  // 5: 生命体征验证器
        LABORATORY,   // 6: 实验室检查验证器
        MEDICATION,   // 7: 用药记录验证器
        NUTRITION,    // 8: 营养记录验证器
        ACTIVITY,     // 9: 活动记录验证器
        SLEEP,        // 10: 睡眠记录验证器
        SYNDROME,     // 11: 证型记录验证器
        PRESCRIPTION, // 12: 处方记录验证器
        HEALTH_PLAN   // 13: 健康计划验证器
    }
    
    // 验证记录
    struct VerificationRecord {
        bytes32 verificationId;  // 验证ID
        string userId;           // 用户ID
        string verifierId;       // 验证者ID
        uint8 verifierType;      // 验证器类型
        bytes32 proofHash;       // 证明哈希
        bytes32 publicInputsHash; // 公共输入哈希
        bool valid;              // 验证结果
        uint256 timestamp;       // 验证时间戳
        string metadata;         // 元数据 (JSON格式)
    }
    
    // 验证密钥映射 (验证器类型 => 验证密钥)
    mapping(uint8 => bytes32) private verificationKeys;
    
    // 验证记录映射 (验证ID => 验证记录)
    mapping(bytes32 => VerificationRecord) private verifications;
    
    // 用户验证索引 (用户ID => 验证ID数组)
    mapping(string => bytes32[]) private userVerifications;
    
    // 事件定义
    event ProofVerified(
        bytes32 indexed verificationId,
        string indexed userId,
        string verifierId,
        uint8 verifierType,
        bool valid,
        uint256 timestamp
    );
    
    event VerificationKeySet(
        uint8 indexed verifierType,
        bytes32 verificationKey,
        uint256 timestamp
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
     * 设置验证器密钥
     * 
     * @param verifierType 验证器类型
     * @param verificationKey 验证密钥
     */
    function setVerificationKey(
        uint8 verifierType,
        bytes32 verificationKey
    ) public onlyOwner {
        require(verifierType <= uint8(VerifierType.HEALTH_PLAN), "Invalid verifier type");
        require(verificationKey != bytes32(0), "Invalid verification key");
        
        verificationKeys[verifierType] = verificationKey;
        
        emit VerificationKeySet(
            verifierType,
            verificationKey,
            block.timestamp
        );
    }
    
    /**
     * 验证零知识证明
     * 
     * @param userId 用户ID
     * @param verifierId 验证者ID
     * @param verifierType 验证器类型
     * @param proof 零知识证明数据
     * @param publicInputs 公共输入数据
     * @param metadata 元数据
     * @return verificationId 验证ID
     * @return valid 验证结果
     */
    function verifyProof(
        string memory userId,
        string memory verifierId,
        uint8 verifierType,
        bytes calldata proof,
        bytes calldata publicInputs,
        string memory metadata
    ) public returns (bytes32, bool) {
        // 验证参数
        require(bytes(userId).length > 0, "User ID cannot be empty");
        require(bytes(verifierId).length > 0, "Verifier ID cannot be empty");
        require(verifierType <= uint8(VerifierType.HEALTH_PLAN), "Invalid verifier type");
        require(proof.length > 0, "Proof cannot be empty");
        require(publicInputs.length > 0, "Public inputs cannot be empty");
        
        // 计算哈希
        bytes32 proofHash = keccak256(proof);
        bytes32 publicInputsHash = keccak256(publicInputs);
        
        // 执行验证
        bool isValid = verifyZKProof(verifierType, proof, publicInputs);
        
        // 生成验证ID
        bytes32 verificationId = keccak256(
            abi.encodePacked(userId, verifierId, verifierType, proofHash, block.timestamp)
        );
        
        // 创建验证记录
        VerificationRecord memory record = VerificationRecord({
            verificationId: verificationId,
            userId: userId,
            verifierId: verifierId,
            verifierType: verifierType,
            proofHash: proofHash,
            publicInputsHash: publicInputsHash,
            valid: isValid,
            timestamp: block.timestamp,
            metadata: metadata
        });
        
        // 存储验证记录
        verifications[verificationId] = record;
        userVerifications[userId].push(verificationId);
        
        // 触发事件
        emit ProofVerified(
            verificationId,
            userId,
            verifierId,
            verifierType,
            isValid,
            block.timestamp
        );
        
        return (verificationId, isValid);
    }
    
    /**
     * 内部验证逻辑
     * 实际的零知识证明验证在这里进行
     * 
     * @param verifierType 验证器类型
     * @param proof 零知识证明数据
     * @param publicInputs 公共输入数据
     * @return 验证结果
     */
    function verifyZKProof(
        uint8 verifierType,
        bytes calldata proof,
        bytes calldata publicInputs
    ) internal view returns (bool) {
        // 检查是否存在对应的验证密钥
        bytes32 verificationKey = verificationKeys[verifierType];
        
        // 如果没有设置验证密钥，则返回失败
        if (verificationKey == bytes32(0)) {
            return false;
        }
        
        // 在实际实现中，这里应该调用特定的零知识证明验证算法
        // 出于演示目的，这里使用简化的验证逻辑
        
        // 注意：实际项目中应替换为真实的零知识证明验证逻辑
        // 例如使用zkSNARKs或zkSTARKs库
        
        // 模拟验证逻辑：将会在生产环境中替换为实际验证
        bytes32 combinedHash = keccak256(abi.encodePacked(proof, publicInputs, verificationKey));
        
        // 用于演示：确保验证不总是返回true或false
        // 实际验证将基于密码学操作
        return uint256(combinedHash) % 100 > 10; 
    }
    
    /**
     * 获取验证记录详情
     * 
     * @param verificationId 验证ID
     * @return 验证记录字段(用户ID, 验证者ID, 验证器类型, 验证结果, 时间戳, 元数据)
     */
    function getVerificationRecord(
        bytes32 verificationId
    ) public view returns (
        string memory userId,
        string memory verifierId,
        uint8 verifierType,
        bool valid,
        uint256 timestamp,
        string memory metadata
    ) {
        // 检查验证记录是否存在
        require(verifications[verificationId].timestamp > 0, "Verification record does not exist");
        
        // 获取验证记录
        VerificationRecord memory record = verifications[verificationId];
        
        return (
            record.userId,
            record.verifierId,
            record.verifierType,
            record.valid,
            record.timestamp,
            record.metadata
        );
    }
    
    /**
     * 获取用户的所有验证记录ID
     * 
     * @param userId 用户ID
     * @return 验证ID数组
     */
    function getUserVerifications(
        string memory userId
    ) public view returns (bytes32[] memory) {
        return userVerifications[userId];
    }
    
    /**
     * 批量验证是否有效
     * 
     * @param verificationIds 验证ID数组
     * @return 验证结果数组
     */
    function batchCheckValidVerifications(
        bytes32[] memory verificationIds
    ) public view returns (bool[] memory) {
        bool[] memory results = new bool[](verificationIds.length);
        
        for (uint i = 0; i < verificationIds.length; i++) {
            if (verifications[verificationIds[i]].timestamp == 0) {
                results[i] = false;
            } else {
                results[i] = verifications[verificationIds[i]].valid;
            }
        }
        
        return results;
    }
    
    /**
     * 获取验证器支持的类型数量
     * 
     * @return 支持的验证器类型数量
     */
    function getSupportedVerifierTypesCount() public pure returns (uint8) {
        return uint8(VerifierType.HEALTH_PLAN) + 1;
    }
    
    /**
     * 检查验证器密钥是否已设置
     * 
     * @param verifierType 验证器类型
     * @return 是否已设置
     */
    function isVerificationKeySet(
        uint8 verifierType
    ) public view returns (bool) {
        return verificationKeys[verifierType] != bytes32(0);
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