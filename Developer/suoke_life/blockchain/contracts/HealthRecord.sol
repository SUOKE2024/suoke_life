// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title HealthRecord
 * @dev 储存和管理用户健康数据
 */
contract HealthRecord {
    struct Record {
        string dataHash; // IPFS哈希或加密哈希
        uint256 timestamp;
        string dataType; // 例如: "体质检测", "舌诊", "面诊" 等
        string encryptedMetadata; // 加密的元数据
        bool isShared; // 是否已共享
        address[] authorizedUsers; // 授权访问的用户
    }
    
    // 用户地址 => 记录ID数组
    mapping(address => uint256[]) private userRecords;
    
    // 记录ID => 记录数据
    mapping(uint256 => Record) private records;
    
    // 记录ID计数器
    uint256 private recordIdCounter;
    
    // 记录创建事件
    event RecordCreated(address indexed user, uint256 recordId, string dataType);
    
    // 记录共享事件
    event RecordShared(address indexed owner, address indexed authorized, uint256 recordId);
    
    /**
     * @dev 创建新的健康记录
     * @param dataHash 数据哈希
     * @param dataType 数据类型
     * @param encryptedMetadata 加密的元数据
     */
    function createRecord(
        string memory dataHash,
        string memory dataType,
        string memory encryptedMetadata
    ) public returns (uint256) {
        uint256 recordId = recordIdCounter++;
        
        records[recordId] = Record({
            dataHash: dataHash,
            timestamp: block.timestamp,
            dataType: dataType,
            encryptedMetadata: encryptedMetadata,
            isShared: false,
            authorizedUsers: new address[](0)
        });
        
        userRecords[msg.sender].push(recordId);
        
        emit RecordCreated(msg.sender, recordId, dataType);
        
        return recordId;
    }
    
    /**
     * @dev 获取用户的记录数量
     */
    function getUserRecordCount() public view returns (uint256) {
        return userRecords[msg.sender].length;
    }
    
    /**
     * @dev 获取用户特定索引的记录ID
     * @param index 索引
     */
    function getUserRecordIdAtIndex(uint256 index) public view returns (uint256) {
        require(index < userRecords[msg.sender].length, "Index out of bounds");
        return userRecords[msg.sender][index];
    }
    
    /**
     * @dev 获取记录信息
     * @param recordId 记录ID
     */
    function getRecord(uint256 recordId) public view 
        returns (
            string memory dataHash,
            uint256 timestamp,
            string memory dataType,
            bool isShared
        ) 
    {
        Record storage record = records[recordId];
        
        // 验证访问权限 (记录所有者或已授权用户)
        bool isAuthorized = false;
        for (uint i = 0; i < userRecords[msg.sender].length; i++) {
            if (userRecords[msg.sender][i] == recordId) {
                isAuthorized = true;
                break;
            }
        }
        
        if (!isAuthorized) {
            for (uint i = 0; i < record.authorizedUsers.length; i++) {
                if (record.authorizedUsers[i] == msg.sender) {
                    isAuthorized = true;
                    break;
                }
            }
        }
        
        require(isAuthorized, "Not authorized to access this record");
        
        return (
            record.dataHash,
            record.timestamp,
            record.dataType,
            record.isShared
        );
    }
    
    /**
     * @dev 共享记录给其他用户
     * @param recordId 记录ID
     * @param user 被授权的用户地址
     */
    function shareRecord(uint256 recordId, address user) public {
        // 验证是记录所有者
        bool isOwner = false;
        for (uint i = 0; i < userRecords[msg.sender].length; i++) {
            if (userRecords[msg.sender][i] == recordId) {
                isOwner = true;
                break;
            }
        }
        
        require(isOwner, "Not the owner of this record");
        require(user != address(0), "Invalid user address");
        
        Record storage record = records[recordId];
        
        // 检查用户是否已授权
        for (uint i = 0; i < record.authorizedUsers.length; i++) {
            require(record.authorizedUsers[i] != user, "User already authorized");
        }
        
        record.authorizedUsers.push(user);
        record.isShared = true;
        
        emit RecordShared(msg.sender, user, recordId);
    }
}
