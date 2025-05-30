import AsyncStorage from "@react-native-async-storage/async-storage";
import CryptoJS from "crypto-js";
import { securityManager } from "./securityManager";


// 区块链配置
const BLOCKCHAIN_CONFIG = {
  NETWORK_ID: "suoke_health_network",
  BLOCK_SIZE_LIMIT: 1024 * 1024, // 1MB
  MINING_DIFFICULTY: 4,
  BLOCK_TIME: 30000, // 30秒
  CONSENSUS_THRESHOLD: 0.67, // 67%共识
  DATA_RETENTION_DAYS: 365 * 7, // 7年
};

// 健康数据类型
export interface HealthDataRecord {
  id: string;
  userId: string;
  dataType:
    | "vital_signs"
    | "diagnosis"
    | "treatment"
    | "lifestyle"
    | "genetic"
    | "environmental";
  data: any;
  timestamp: number;
  source: string;
  privacy_level: "public" | "private" | "confidential" | "restricted";
  consent: ConsentRecord;
  hash: string;
}

export interface ConsentRecord {
  granted: boolean;
  scope: string[];
  expiry: number;
  grantor: string;
  witness?: string;
  signature: string;
}

// 区块结构
export interface Block {
  index: number;
  timestamp: number;
  data: HealthDataRecord[];
  previousHash: string;
  hash: string;
  nonce: number;
  merkleRoot: string;
  validator: string;
}

// 交易记录
export interface Transaction {
  id: string;
  type:
    | "data_write"
    | "data_read"
    | "consent_update"
    | "access_grant"
    | "data_share";
  from: string;
  to?: string;
  data: any;
  timestamp: number;
  signature: string;
  fee: number;
}

// 访问控制记录
export interface AccessControl {
  dataId: string;
  userId: string;
  permissions: string[];
  grantedBy: string;
  grantedAt: number;
  expiresAt?: number;
  conditions?: string[];
}

// 零知识证明
export interface ZKProof {
  statement: string;
  proof: string;
  publicInputs: any[];
  verificationKey: string;
  timestamp: number;
}

// Merkle树节点
interface MerkleNode {
  hash: string;
  left?: MerkleNode;
  right?: MerkleNode;
  data?: any;
}

// Merkle树实现
class MerkleTree {
  private root: MerkleNode | null = null;
  private leaves: MerkleNode[] = [];

  constructor(data: any[]) {
    this.buildTree(data);
  }

  private buildTree(data: any[]): void {
    // 创建叶子节点
    this.leaves = data.map((item) => ({
      hash: this.hash(JSON.stringify(item)),
      data: item,
    }));

    if (this.leaves.length === 0) {
      this.root = null;
      return;
    }

    // 构建树
    let currentLevel = [...this.leaves];

    while (currentLevel.length > 1) {
      const nextLevel: MerkleNode[] = [];

      for (let i = 0; i < currentLevel.length; i += 2) {
        const left = currentLevel[i];
        const right = currentLevel[i + 1] || left; // 如果是奇数个节点，复制最后一个

        const parent: MerkleNode = {
          hash: this.hash(left.hash + right.hash),
          left,
          right,
        };

        nextLevel.push(parent);
      }

      currentLevel = nextLevel;
    }

    this.root = currentLevel[0];
  }

  private hash(data: string): string {
    return CryptoJS.SHA256(data).toString();
  }

  getRootHash(): string {
    return this.root?.hash || "";
  }

  // 生成Merkle证明
  generateProof(dataIndex: number): string[] {
    if (!this.root || dataIndex >= this.leaves.length) {
      return [];
    }

    const proof: string[] = [];
    let currentIndex = dataIndex;
    let currentLevel = [...this.leaves];

    while (currentLevel.length > 1) {
      const nextLevel: MerkleNode[] = [];

      for (let i = 0; i < currentLevel.length; i += 2) {
        const left = currentLevel[i];
        const right = currentLevel[i + 1] || left;

        // 如果当前索引在这一对中
        if (i === currentIndex || i + 1 === currentIndex) {
          // 添加兄弟节点的哈希到证明中
          if (i === currentIndex) {
            proof.push(right.hash);
          } else {
            proof.push(left.hash);
          }
          currentIndex = Math.floor(i / 2);
        }

        nextLevel.push({
          hash: this.hash(left.hash + right.hash),
          left,
          right,
        });
      }

      currentLevel = nextLevel;
    }

    return proof;
  }

  // 验证Merkle证明
  static verifyProof(
    leafHash: string,
    proof: string[],
    rootHash: string,
    leafIndex: number
  ): boolean {
    let computedHash = leafHash;
    let index = leafIndex;

    for (const proofElement of proof) {
      if (index % 2 === 0) {
        computedHash = CryptoJS.SHA256(computedHash + proofElement).toString();
      } else {
        computedHash = CryptoJS.SHA256(proofElement + computedHash).toString();
      }
      index = Math.floor(index / 2);
    }

    return computedHash === rootHash;
  }
}

// 零知识证明生成器
class ZKProofGenerator {
  private static instance: ZKProofGenerator;

  static getInstance(): ZKProofGenerator {
    if (!ZKProofGenerator.instance) {
      ZKProofGenerator.instance = new ZKProofGenerator();
    }
    return ZKProofGenerator.instance;
  }

  // 生成年龄范围证明（不暴露具体年龄）
  generateAgeRangeProof(
    actualAge: number,
    minAge: number,
    maxAge: number,
    secret: string
  ): ZKProof {
    const statement = `Age is between ${minAge} and ${maxAge}`;
    const isValid = actualAge >= minAge && actualAge <= maxAge;

    // 简化的零知识证明（实际应用中需要使用专业的ZK库）
    const commitment = CryptoJS.SHA256(actualAge + secret).toString();
    const challenge = CryptoJS.SHA256(statement + commitment).toString();
    const response = CryptoJS.SHA256(secret + challenge).toString();

    return {
      statement,
      proof: JSON.stringify({
        commitment,
        challenge,
        response,
        valid: isValid,
      }),
      publicInputs: [minAge, maxAge],
      verificationKey: CryptoJS.SHA256(statement).toString(),
      timestamp: Date.now(),
    };
  }

  // 生成健康状态证明（不暴露具体健康数据）
  generateHealthStatusProof(
    healthData: any,
    threshold: any,
    secret: string
  ): ZKProof {
    const statement = "Health metrics meet required standards";

    // 简化的健康状态验证
    const meetsStandards = this.evaluateHealthStandards(healthData, threshold);

    const commitment = CryptoJS.SHA256(
      JSON.stringify(healthData) + secret
    ).toString();
    const challenge = CryptoJS.SHA256(statement + commitment).toString();
    const response = CryptoJS.SHA256(secret + challenge).toString();

    return {
      statement,
      proof: JSON.stringify({
        commitment,
        challenge,
        response,
        valid: meetsStandards,
      }),
      publicInputs: [threshold],
      verificationKey: CryptoJS.SHA256(statement).toString(),
      timestamp: Date.now(),
    };
  }

  // 验证零知识证明
  verifyProof(proof: ZKProof): boolean {
    try {
      const proofData = JSON.parse(proof.proof);

      // 重新计算挑战
      const expectedChallenge = CryptoJS.SHA256(
        proof.statement + proofData.commitment
      ).toString();

      return proofData.challenge === expectedChallenge && proofData.valid;
    } catch (error) {
      console.error("证明验证失败:", error);
      return false;
    }
  }

  private evaluateHealthStandards(healthData: any, threshold: any): boolean {
    // 简化的健康标准评估
    if (healthData.bloodPressure && threshold.bloodPressure) {
      const systolic = healthData.bloodPressure.systolic;
      const diastolic = healthData.bloodPressure.diastolic;

      if (
        systolic > threshold.bloodPressure.maxSystolic ||
        diastolic > threshold.bloodPressure.maxDiastolic
      ) {
        return false;
      }
    }

    return true;
  }
}

// 区块链健康数据管理器
export class BlockchainHealthDataManager {
  private static instance: BlockchainHealthDataManager;
  private blockchain: Block[] = [];
  private pendingTransactions: Transaction[] = [];
  private accessControls: Map<string, AccessControl[]> = new Map();
  private zkProofGenerator: ZKProofGenerator;
  private miningReward = 10;

  private constructor() {
    this.zkProofGenerator = ZKProofGenerator.getInstance();
    this.initializeBlockchain();
  }

  static getInstance(): BlockchainHealthDataManager {
    if (!BlockchainHealthDataManager.instance) {
      BlockchainHealthDataManager.instance = new BlockchainHealthDataManager();
    }
    return BlockchainHealthDataManager.instance;
  }

  // 初始化区块链
  private async initializeBlockchain(): Promise<void> {
    try {
      // 尝试从存储加载现有区块链
      const stored = await AsyncStorage.getItem("health_blockchain");
      if (stored) {
        const decrypted = securityManager.decryptData(stored);
        this.blockchain = decrypted.blocks || [];
        this.accessControls = new Map(decrypted.accessControls || []);
      }

      // 如果没有区块链，创建创世区块
      if (this.blockchain.length === 0) {
        this.createGenesisBlock();
      }
    } catch (error) {
      console.error("区块链初始化失败:", error);
      this.createGenesisBlock();
    }
  }

  // 创建创世区块
  private createGenesisBlock(): void {
    const genesisBlock: Block = {
      index: 0,
      timestamp: Date.now(),
      data: [],
      previousHash: "0",
      hash: "",
      nonce: 0,
      merkleRoot: "",
      validator: "system",
    };

    genesisBlock.hash = this.calculateHash(genesisBlock);
    this.blockchain.push(genesisBlock);

    console.log("创世区块已创建");
  }

  // 添加健康数据
  async addHealthData(
    userId: string,
    dataType: HealthDataRecord["dataType"],
    data: any,
    source: string,
    privacyLevel: HealthDataRecord["privacy_level"] = "private",
    consent: ConsentRecord
  ): Promise<string> {
    const dataId = this.generateDataId();

    const healthRecord: HealthDataRecord = {
      id: dataId,
      userId,
      dataType,
      data: securityManager.encryptData(data), // 加密敏感数据
      timestamp: Date.now(),
      source,
      privacy_level: privacyLevel,
      consent,
      hash: "",
    };

    // 计算数据哈希
    healthRecord.hash = this.calculateDataHash(healthRecord);

    // 创建交易
    const transaction: Transaction = {
      id: this.generateTransactionId(),
      type: "data_write",
      from: userId,
      data: healthRecord,
      timestamp: Date.now(),
      signature: this.signTransaction(healthRecord, userId),
      fee: 1,
    };

    this.pendingTransactions.push(transaction);

    // 记录安全事件
    securityManager.logSecurityEvent({
      type: "data_access",
      userId,
      details: {
        action: "health_data_added",
        dataId,
        dataType,
        privacyLevel,
      },
      severity: "low",
    });

    // 如果有足够的待处理交易，挖掘新区块
    if (this.pendingTransactions.length >= 5) {
      await this.mineBlock();
    }

    return dataId;
  }

  // 获取健康数据（带权限检查）
  async getHealthData(
    dataId: string,
    requesterId: string,
    purpose: string
  ): Promise<HealthDataRecord | null> {
    // 检查访问权限
    if (!this.checkAccess(dataId, requesterId, "read")) {
      securityManager.logSecurityEvent({
        type: "access_denied",
        userId: requesterId,
        details: {
          action: "unauthorized_data_access",
          dataId,
          purpose,
        },
        severity: "high",
      });
      throw new Error("访问被拒绝：权限不足");
    }

    // 在区块链中查找数据
    for (const block of this.blockchain) {
      for (const record of block.data) {
        if (record.id === dataId) {
          // 记录访问事件
          const transaction: Transaction = {
            id: this.generateTransactionId(),
            type: "data_read",
            from: requesterId,
            data: { dataId, purpose },
            timestamp: Date.now(),
            signature: this.signTransaction({ dataId, purpose }, requesterId),
            fee: 0.1,
          };

          this.pendingTransactions.push(transaction);

          // 解密数据（如果有权限）
          const decryptedRecord = { ...record };
          if (this.checkAccess(dataId, requesterId, "decrypt")) {
            decryptedRecord.data = securityManager.decryptData(record.data);
          }

          return decryptedRecord;
        }
      }
    }

    return null;
  }

  // 生成零知识证明
  generateZKProof(
    userId: string,
    proofType: "age_range" | "health_status",
    parameters: any,
    secret: string
  ): ZKProof {
    switch (proofType) {
      case "age_range":
        return this.zkProofGenerator.generateAgeRangeProof(
          parameters.actualAge,
          parameters.minAge,
          parameters.maxAge,
          secret
        );
      case "health_status":
        return this.zkProofGenerator.generateHealthStatusProof(
          parameters.healthData,
          parameters.threshold,
          secret
        );
      default:
        throw new Error("不支持的证明类型");
    }
  }

  // 验证零知识证明
  verifyZKProof(proof: ZKProof): boolean {
    return this.zkProofGenerator.verifyProof(proof);
  }

  // 授予数据访问权限
  grantAccess(
    dataId: string,
    userId: string,
    permissions: string[],
    grantedBy: string,
    expiresAt?: number
  ): void {
    const accessControl: AccessControl = {
      dataId,
      userId,
      permissions,
      grantedBy,
      grantedAt: Date.now(),
      expiresAt,
    };

    const existing = this.accessControls.get(dataId) || [];
    existing.push(accessControl);
    this.accessControls.set(dataId, existing);

    // 创建访问授权交易
    const transaction: Transaction = {
      id: this.generateTransactionId(),
      type: "access_grant",
      from: grantedBy,
      to: userId,
      data: accessControl,
      timestamp: Date.now(),
      signature: this.signTransaction(accessControl, grantedBy),
      fee: 0.5,
    };

    this.pendingTransactions.push(transaction);
  }

  // 检查访问权限
  private checkAccess(
    dataId: string,
    userId: string,
    permission: string
  ): boolean {
    const controls = this.accessControls.get(dataId) || [];

    for (const control of controls) {
      if (
        control.userId === userId &&
        control.permissions.includes(permission)
      ) {
        // 检查是否过期
        if (control.expiresAt && Date.now() > control.expiresAt) {
          continue;
        }

        return true;
      }
    }

    return false;
  }

  // 挖掘新区块
  private async mineBlock(): Promise<void> {
    const previousBlock = this.blockchain[this.blockchain.length - 1];
    const newBlock: Block = {
      index: previousBlock.index + 1,
      timestamp: Date.now(),
      data: this.extractHealthRecords(this.pendingTransactions),
      previousHash: previousBlock.hash,
      hash: "",
      nonce: 0,
      merkleRoot: "",
      validator: "system",
    };

    // 计算Merkle根
    const merkleTree = new MerkleTree(newBlock.data);
    newBlock.merkleRoot = merkleTree.getRootHash();

    // 工作量证明
    newBlock.hash = this.mineBlockWithProofOfWork(newBlock);

    // 添加到区块链
    this.blockchain.push(newBlock);

    // 清空待处理交易
    this.pendingTransactions = [];

    // 持久化区块链
    await this.persistBlockchain();

    console.log(`新区块已挖掘: ${newBlock.hash}`);
  }

  // 工作量证明挖矿
  private mineBlockWithProofOfWork(block: Block): string {
    const target = "0".repeat(BLOCKCHAIN_CONFIG.MINING_DIFFICULTY);

    while (true) {
      const hash = this.calculateHash(block);
      if (hash.substring(0, BLOCKCHAIN_CONFIG.MINING_DIFFICULTY) === target) {
        return hash;
      }
      block.nonce++;
    }
  }

  // 验证区块链完整性
  validateBlockchain(): boolean {
    for (let i = 1; i < this.blockchain.length; i++) {
      const currentBlock = this.blockchain[i];
      const previousBlock = this.blockchain[i - 1];

      // 验证当前区块哈希
      if (currentBlock.hash !== this.calculateHash(currentBlock)) {
        console.error(`区块 ${i} 哈希无效`);
        return false;
      }

      // 验证前一个区块的连接
      if (currentBlock.previousHash !== previousBlock.hash) {
        console.error(`区块 ${i} 与前一个区块连接无效`);
        return false;
      }

      // 验证Merkle根
      const merkleTree = new MerkleTree(currentBlock.data);
      if (currentBlock.merkleRoot !== merkleTree.getRootHash()) {
        console.error(`区块 ${i} Merkle根无效`);
        return false;
      }
    }

    return true;
  }

  // 获取用户健康数据摘要
  getUserHealthSummary(userId: string): {
    totalRecords: number;
    dataTypes: string[];
    latestRecord: number;
    privacyDistribution: Record<string, number>;
  } {
    let totalRecords = 0;
    const dataTypes = new Set<string>();
    let latestRecord = 0;
    const privacyDistribution: Record<string, number> = {};

    for (const block of this.blockchain) {
      for (const record of block.data) {
        if (record.userId === userId) {
          totalRecords++;
          dataTypes.add(record.dataType);
          latestRecord = Math.max(latestRecord, record.timestamp);

          privacyDistribution[record.privacy_level] =
            (privacyDistribution[record.privacy_level] || 0) + 1;
        }
      }
    }

    return {
      totalRecords,
      dataTypes: Array.from(dataTypes),
      latestRecord,
      privacyDistribution,
    };
  }

  // 计算区块哈希
  private calculateHash(block: Block): string {
    return CryptoJS.SHA256(
      block.index +
        block.timestamp +
        JSON.stringify(block.data) +
        block.previousHash +
        block.nonce +
        block.merkleRoot
    ).toString();
  }

  // 计算数据哈希
  private calculateDataHash(record: HealthDataRecord): string {
    return CryptoJS.SHA256(
      record.id +
        record.userId +
        record.dataType +
        JSON.stringify(record.data) +
        record.timestamp +
        record.source
    ).toString();
  }

  // 签名交易
  private signTransaction(data: any, userId: string): string {
    return CryptoJS.SHA256(JSON.stringify(data) + userId).toString();
  }

  // 从交易中提取健康记录
  private extractHealthRecords(
    transactions: Transaction[]
  ): HealthDataRecord[] {
    return transactions
      .filter((tx) => tx.type === "data_write")
      .map((tx) => tx.data as HealthDataRecord);
  }

  // 持久化区块链
  private async persistBlockchain(): Promise<void> {
    try {
      const data = {
        blocks: this.blockchain,
        accessControls: Array.from(this.accessControls.entries()),
      };

      const encrypted = securityManager.encryptData(data);
      await AsyncStorage.setItem("health_blockchain", encrypted);
    } catch (error) {
      console.error("区块链持久化失败:", error);
    }
  }

  // 生成数据ID
  private generateDataId(): string {
    return `data_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // 生成交易ID
  private generateTransactionId(): string {
    return `tx_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // 获取区块链统计
  getBlockchainStats(): {
    totalBlocks: number;
    totalTransactions: number;
    totalDataRecords: number;
    chainSize: number;
    isValid: boolean;
  } {
    const totalBlocks = this.blockchain.length;
    let totalTransactions = this.pendingTransactions.length;
    let totalDataRecords = 0;

    for (const block of this.blockchain) {
      totalDataRecords += block.data.length;
    }

    const chainSize = JSON.stringify(this.blockchain).length;
    const isValid = this.validateBlockchain();

    return {
      totalBlocks,
      totalTransactions,
      totalDataRecords,
      chainSize,
      isValid,
    };
  }
}

// 导出单例实例
export const blockchainHealthDataManager =
  BlockchainHealthDataManager.getInstance();
