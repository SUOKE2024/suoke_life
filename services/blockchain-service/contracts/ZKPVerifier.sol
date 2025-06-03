// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title ZKPVerifier
 * @dev 零知识证明验证智能合约
 * 负责验证健康数据的零知识证明，保护用户隐私
 */
contract ZKPVerifier is Ownable, ReentrancyGuard {
    
    // 验证密钥结构
    struct VerificationKey {
        uint256[2] alpha;
        uint256[2][2] beta;
        uint256[2][2] gamma;
        uint256[2][2] delta;
        uint256[][] ic;
        bool isActive;
    }
    
    // 证明结构
    struct Proof {
        uint256[2] a;
        uint256[2] b;
        uint256[2] c;
    }
    
    // 验证结果结构
    struct VerificationResult {
        bool isValid;
        uint256 timestamp;
        address verifier;
        bytes32 proofHash;
    }
    
    // 电路ID到验证密钥的映射
    mapping(string => VerificationKey) public verificationKeys;
    
    // 证明哈希到验证结果的映射
    mapping(bytes32 => VerificationResult) public verificationResults;
    
    // 用户的验证历史
    mapping(address => bytes32[]) public userVerifications;
    
    // 支持的电路列表
    string[] public supportedCircuits;
    
    // 事件定义
    event CircuitRegistered(
        string indexed circuitId,
        address indexed registrar,
        uint256 timestamp
    );
    
    event ProofVerified(
        bytes32 indexed proofHash,
        string indexed circuitId,
        address indexed user,
        bool isValid,
        uint256 timestamp
    );
    
    event VerificationKeyUpdated(
        string indexed circuitId,
        address indexed updater,
        uint256 timestamp
    );
    
    /**
     * @dev 注册新的验证电路
     * @param _circuitId 电路ID
     * @param _vk 验证密钥
     */
    function registerCircuit(
        string memory _circuitId,
        VerificationKey memory _vk
    ) external onlyOwner {
        require(bytes(_circuitId).length > 0, "Circuit ID cannot be empty");
        require(!verificationKeys[_circuitId].isActive, "Circuit already registered");
        
        verificationKeys[_circuitId] = _vk;
        verificationKeys[_circuitId].isActive = true;
        supportedCircuits.push(_circuitId);
        
        emit CircuitRegistered(_circuitId, msg.sender, block.timestamp);
    }
    
    /**
     * @dev 更新验证密钥
     * @param _circuitId 电路ID
     * @param _vk 新的验证密钥
     */
    function updateVerificationKey(
        string memory _circuitId,
        VerificationKey memory _vk
    ) external onlyOwner {
        require(verificationKeys[_circuitId].isActive, "Circuit not registered");
        
        verificationKeys[_circuitId] = _vk;
        verificationKeys[_circuitId].isActive = true;
        
        emit VerificationKeyUpdated(_circuitId, msg.sender, block.timestamp);
    }
    
    /**
     * @dev 验证零知识证明
     * @param _circuitId 电路ID
     * @param _proof 证明
     * @param _publicInputs 公共输入
     */
    function verifyProof(
        string memory _circuitId,
        Proof memory _proof,
        uint256[] memory _publicInputs
    ) external nonReentrant returns (bool) {
        require(verificationKeys[_circuitId].isActive, "Circuit not supported");
        
        // 计算证明哈希
        bytes32 proofHash = keccak256(abi.encodePacked(
            _proof.a,
            _proof.b,
            _proof.c,
            _publicInputs,
            msg.sender
        ));
        
        // 检查是否已经验证过
        require(verificationResults[proofHash].timestamp == 0, "Proof already verified");
        
        // 执行零知识证明验证
        bool isValid = _verifyProofInternal(_circuitId, _proof, _publicInputs);
        
        // 记录验证结果
        verificationResults[proofHash] = VerificationResult({
            isValid: isValid,
            timestamp: block.timestamp,
            verifier: msg.sender,
            proofHash: proofHash
        });
        
        // 添加到用户验证历史
        userVerifications[msg.sender].push(proofHash);
        
        emit ProofVerified(proofHash, _circuitId, msg.sender, isValid, block.timestamp);
        
        return isValid;
    }
    
    /**
     * @dev 批量验证证明
     * @param _circuitId 电路ID
     * @param _proofs 证明数组
     * @param _publicInputs 公共输入数组
     */
    function batchVerifyProofs(
        string memory _circuitId,
        Proof[] memory _proofs,
        uint256[][] memory _publicInputs
    ) external nonReentrant returns (bool[] memory) {
        require(_proofs.length == _publicInputs.length, "Arrays length mismatch");
        require(_proofs.length > 0, "Empty proof array");
        require(verificationKeys[_circuitId].isActive, "Circuit not supported");
        
        bool[] memory results = new bool[](_proofs.length);
        
        for (uint256 i = 0; i < _proofs.length; i++) {
            bytes32 proofHash = keccak256(abi.encodePacked(
                _proofs[i].a,
                _proofs[i].b,
                _proofs[i].c,
                _publicInputs[i],
                msg.sender
            ));
            
            // 跳过已验证的证明
            if (verificationResults[proofHash].timestamp != 0) {
                results[i] = verificationResults[proofHash].isValid;
                continue;
            }
            
            bool isValid = _verifyProofInternal(_circuitId, _proofs[i], _publicInputs[i]);
            results[i] = isValid;
            
            // 记录验证结果
            verificationResults[proofHash] = VerificationResult({
                isValid: isValid,
                timestamp: block.timestamp,
                verifier: msg.sender,
                proofHash: proofHash
            });
            
            userVerifications[msg.sender].push(proofHash);
            
            emit ProofVerified(proofHash, _circuitId, msg.sender, isValid, block.timestamp);
        }
        
        return results;
    }
    
    /**
     * @dev 内部证明验证函数
     * @param _circuitId 电路ID
     * @param _proof 证明
     * @param _publicInputs 公共输入
     */
    function _verifyProofInternal(
        string memory _circuitId,
        Proof memory _proof,
        uint256[] memory _publicInputs
    ) internal view returns (bool) {
        VerificationKey storage vk = verificationKeys[_circuitId];
        
        // 简化的验证逻辑（实际实现需要椭圆曲线配对运算）
        // 这里使用哈希验证作为示例
        bytes32 expectedHash = keccak256(abi.encodePacked(
            vk.alpha,
            vk.beta,
            _publicInputs
        ));
        
        bytes32 proofHash = keccak256(abi.encodePacked(
            _proof.a,
            _proof.b,
            _proof.c
        ));
        
        // 实际的zk-SNARK验证需要使用椭圆曲线配对
        // 这里简化为哈希比较
        return uint256(expectedHash) % 1000 == uint256(proofHash) % 1000;
    }
    
    /**
     * @dev 获取验证结果
     * @param _proofHash 证明哈希
     */
    function getVerificationResult(bytes32 _proofHash) 
        external 
        view 
        returns (VerificationResult memory) 
    {
        return verificationResults[_proofHash];
    }
    
    /**
     * @dev 获取用户验证历史
     * @param _user 用户地址
     * @param _offset 偏移量
     * @param _limit 限制数量
     */
    function getUserVerifications(address _user, uint256 _offset, uint256 _limit) 
        external 
        view 
        returns (bytes32[] memory) 
    {
        bytes32[] storage verifications = userVerifications[_user];
        require(_offset < verifications.length, "Offset out of bounds");
        
        uint256 end = _offset + _limit;
        if (end > verifications.length) {
            end = verifications.length;
        }
        
        bytes32[] memory result = new bytes32[](end - _offset);
        for (uint256 i = _offset; i < end; i++) {
            result[i - _offset] = verifications[i];
        }
        
        return result;
    }
    
    /**
     * @dev 检查电路是否支持
     * @param _circuitId 电路ID
     */
    function isCircuitSupported(string memory _circuitId) 
        external 
        view 
        returns (bool) 
    {
        return verificationKeys[_circuitId].isActive;
    }
    
    /**
     * @dev 获取支持的电路列表
     */
    function getSupportedCircuits() 
        external 
        view 
        returns (string[] memory) 
    {
        return supportedCircuits;
    }
    
    /**
     * @dev 禁用电路
     * @param _circuitId 电路ID
     */
    function disableCircuit(string memory _circuitId) 
        external 
        onlyOwner 
    {
        require(verificationKeys[_circuitId].isActive, "Circuit not active");
        verificationKeys[_circuitId].isActive = false;
    }
    
    /**
     * @dev 启用电路
     * @param _circuitId 电路ID
     */
    function enableCircuit(string memory _circuitId) 
        external 
        onlyOwner 
    {
        require(!verificationKeys[_circuitId].isActive, "Circuit already active");
        verificationKeys[_circuitId].isActive = true;
    }
} 