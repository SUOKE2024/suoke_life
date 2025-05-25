// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./HealthDataStorage.sol";

/**
 * @title BatchHealthDataStorage
 * @dev 批量健康数据存储合约，提供批量操作功能以提高性能
 */
contract BatchHealthDataStorage is HealthDataStorage {
    
    // 批量操作事件
    event BatchHealthDataStored(
        bytes32[] indexed transactionIds,
        string[] userIds,
        uint256 batchSize,
        uint256 timestamp
    );
    
    event BatchHealthDataVerified(
        bytes32[] indexed transactionIds,
        bool[] results,
        uint256 batchSize,
        uint256 timestamp
    );
    
    /**
     * 批量存储健康数据
     * 
     * @param userIds 用户ID数组
     * @param dataTypes 数据类型数组
     * @param dataHashes 数据哈希数组
     * @param metadataArray 元数据数组
     * @return transactionIds 交易ID数组
     */
    function batchStoreHealthData(
        string[] memory userIds,
        string[] memory dataTypes,
        bytes32[] memory dataHashes,
        string[] memory metadataArray
    ) public returns (bytes32[] memory) {
        // 验证输入参数长度一致
        require(
            userIds.length == dataTypes.length && 
            dataTypes.length == dataHashes.length && 
            dataHashes.length == metadataArray.length,
            "Input arrays length mismatch"
        );
        
        require(userIds.length > 0, "Empty input arrays");
        require(userIds.length <= 100, "Batch size too large"); // 限制批量大小
        
        bytes32[] memory transactionIds = new bytes32[](userIds.length);
        
        // 批量存储数据
        for (uint256 i = 0; i < userIds.length; i++) {
            transactionIds[i] = storeHealthData(
                userIds[i],
                dataTypes[i],
                dataHashes[i],
                metadataArray[i]
            );
        }
        
        // 触发批量存储事件
        emit BatchHealthDataStored(
            transactionIds,
            userIds,
            userIds.length,
            block.timestamp
        );
        
        return transactionIds;
    }
    
    /**
     * 批量验证健康数据
     * 
     * @param transactionIds 交易ID数组
     * @param dataHashes 要验证的数据哈希数组
     * @return results 验证结果数组
     * @return timestamps 时间戳数组
     */
    function batchVerifyHealthData(
        bytes32[] memory transactionIds,
        bytes32[] memory dataHashes
    ) public view returns (bool[] memory results, uint256[] memory timestamps) {
        // 验证输入参数
        require(transactionIds.length == dataHashes.length, "Input arrays length mismatch");
        require(transactionIds.length > 0, "Empty input arrays");
        require(transactionIds.length <= 100, "Batch size too large");
        
        results = new bool[](transactionIds.length);
        timestamps = new uint256[](transactionIds.length);
        
        // 批量验证数据
        for (uint256 i = 0; i < transactionIds.length; i++) {
            (results[i], timestamps[i]) = verifyHealthData(transactionIds[i], dataHashes[i]);
        }
        
        return (results, timestamps);
    }
    
    /**
     * 批量获取健康数据记录
     * 
     * @param transactionIds 交易ID数组
     * @return userIds 用户ID数组
     * @return dataTypes 数据类型数组
     * @return dataHashes 数据哈希数组
     * @return timestamps 时间戳数组
     * @return isDeletedArray 删除状态数组
     */
    function batchGetHealthDataRecords(
        bytes32[] memory transactionIds
    ) public view returns (
        string[] memory userIds,
        string[] memory dataTypes,
        bytes32[] memory dataHashes,
        uint256[] memory timestamps,
        bool[] memory isDeletedArray
    ) {
        require(transactionIds.length > 0, "Empty input array");
        require(transactionIds.length <= 100, "Batch size too large");
        
        userIds = new string[](transactionIds.length);
        dataTypes = new string[](transactionIds.length);
        dataHashes = new bytes32[](transactionIds.length);
        timestamps = new uint256[](transactionIds.length);
        isDeletedArray = new bool[](transactionIds.length);
        
        for (uint256 i = 0; i < transactionIds.length; i++) {
            (
                userIds[i],
                dataTypes[i],
                dataHashes[i],
                timestamps[i],
                , // blockHash - 不需要在批量操作中返回
                , // metadata - 不需要在批量操作中返回
                isDeletedArray[i]
            ) = getHealthDataRecord(transactionIds[i]);
        }
        
        return (userIds, dataTypes, dataHashes, timestamps, isDeletedArray);
    }
    
    /**
     * 批量删除健康数据（软删除）
     * 
     * @param transactionIds 要删除的交易ID数组
     * @param reasons 删除原因数组
     * @return success 操作成功标志
     */
    function batchDeleteHealthData(
        bytes32[] memory transactionIds,
        string[] memory reasons
    ) public onlyOwner returns (bool) {
        require(transactionIds.length == reasons.length, "Input arrays length mismatch");
        require(transactionIds.length > 0, "Empty input arrays");
        require(transactionIds.length <= 100, "Batch size too large");
        
        for (uint256 i = 0; i < transactionIds.length; i++) {
            // 调用父合约的删除方法（需要在父合约中实现）
            _markAsDeleted(transactionIds[i], reasons[i]);
        }
        
        return true;
    }
    
    /**
     * 内部方法：标记数据为已删除
     * 
     * @param transactionId 交易ID
     * @param reason 删除原因
     */
    function _markAsDeleted(bytes32 transactionId, string memory reason) internal {
        // 检查交易是否存在
        require(healthRecords[transactionId].timestamp > 0, "Transaction does not exist");
        
        // 标记为已删除
        healthRecords[transactionId].isDeleted = true;
        
        // 触发删除事件
        emit HealthDataDeleted(
            transactionId,
            healthRecords[transactionId].userId,
            block.timestamp,
            reason
        );
    }
    
    /**
     * 获取批量操作的燃料估算
     * 
     * @param batchSize 批量大小
     * @param operationType 操作类型 (0: store, 1: verify, 2: get)
     * @return estimatedGas 估算的燃料消耗
     */
    function estimateBatchGas(
        uint256 batchSize,
        uint8 operationType
    ) public pure returns (uint256 estimatedGas) {
        require(batchSize > 0 && batchSize <= 100, "Invalid batch size");
        
        uint256 baseGas = 21000; // 基础交易燃料
        uint256 perItemGas;
        
        if (operationType == 0) { // store
            perItemGas = 150000; // 每个存储操作的燃料
        } else if (operationType == 1) { // verify
            perItemGas = 50000; // 每个验证操作的燃料
        } else if (operationType == 2) { // get
            perItemGas = 30000; // 每个获取操作的燃料
        } else {
            revert("Invalid operation type");
        }
        
        estimatedGas = baseGas + (batchSize * perItemGas);
        
        // 添加10%的缓冲
        estimatedGas = estimatedGas * 110 / 100;
        
        return estimatedGas;
    }
} 