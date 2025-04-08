// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title HealthDataToken
 * @dev 索克生活健康数据通证 (HDT)
 * 用于奖励健康数据贡献和支付健康服务
 */
contract HealthDataToken is ERC20, ERC20Burnable, Ownable {
    // 奖励类型
    enum RewardType { 
        DATA_CONTRIBUTION,  // 数据贡献
        HEALTH_ACHIEVEMENT, // 健康成就
        COMMUNITY_ACTIVITY  // 社区活动
    }
    
    // 奖励事件
    event Rewarded(address indexed user, uint256 amount, RewardType rewardType);
    
    // 白名单合约列表 (允许调用奖励函数的合约地址)
    mapping(address => bool) private rewardContracts;
    
    // 累计奖励记录
    mapping(address => uint256) private totalRewards;
    
    /**
     * @dev 构造函数
     * @param initialSupply 初始供应量
     */
    constructor(uint256 initialSupply) ERC20("Health Data Token", "HDT") Ownable(msg.sender) {
        _mint(msg.sender, initialSupply * 10 ** decimals());
    }
    
    /**
     * @dev 添加奖励合约白名单
     * @param contractAddress 奖励合约地址
     */
    function addRewardContract(address contractAddress) external onlyOwner {
        rewardContracts[contractAddress] = true;
    }
    
    /**
     * @dev 移除奖励合约白名单
     * @param contractAddress 奖励合约地址
     */
    function removeRewardContract(address contractAddress) external onlyOwner {
        rewardContracts[contractAddress] = false;
    }
    
    /**
     * @dev 检查合约是否在奖励白名单中
     * @param contractAddress 合约地址
     */
    function isRewardContract(address contractAddress) external view returns (bool) {
        return rewardContracts[contractAddress];
    }
    
    /**
     * @dev 奖励用户代币 (只能由白名单合约调用)
     * @param user 用户地址
     * @param amount 奖励数量
     * @param rewardType 奖励类型
     */
    function reward(address user, uint256 amount, RewardType rewardType) external {
        require(rewardContracts[msg.sender], "Caller is not authorized to reward");
        require(user != address(0), "Cannot reward to zero address");
        
        _mint(user, amount);
        totalRewards[user] += amount;
        
        emit Rewarded(user, amount, rewardType);
    }
    
    /**
     * @dev 获取用户累计奖励
     * @param user 用户地址
     */
    function getTotalRewards(address user) external view returns (uint256) {
        return totalRewards[user];
    }
    
    /**
     * @dev 铸造代币 (只有管理员可调用)
     * @param to 接收代币的地址
     * @param amount 铸造数量
     */
    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
}
