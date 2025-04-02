import nodeVault from 'node-vault';
import logger from './logger';

let vault: any = null;

/**
 * 设置Vault客户端
 */
export const setupVault = async () => {
  try {
    // 创建Vault客户端
    vault = nodeVault({
      apiVersion: 'v1',
      endpoint: process.env.VAULT_ADDR || 'http://localhost:8200',
      token: process.env.VAULT_TOKEN
    });
    
    // 验证连接
    await vault.status();
    logger.info('Vault连接成功');
    
    // 加载密钥
    await loadSecrets();
    
    return vault;
  } catch (error) {
    logger.error('Vault连接失败:', error);
    throw error;
  }
};

/**
 * 从Vault加载密钥并设置环境变量
 */
export const loadSecrets = async () => {
  try {
    if (!vault) {
      throw new Error('Vault未初始化');
    }
    
    const secretPath = process.env.VAULT_PATH || 'secret/data/laoke-service';
    
    // 读取密钥
    const { data } = await vault.read(secretPath);
    
    if (!data || !data.data) {
      logger.warn(`Vault路径 ${secretPath} 未找到数据`);
      return;
    }
    
    // 设置环境变量
    const secrets = data.data;
    for (const [key, value] of Object.entries(secrets)) {
      if (typeof value === 'string') {
        process.env[key] = value;
      }
    }
    
    logger.info(`从Vault加载了 ${Object.keys(secrets).length} 个密钥`);
  } catch (error) {
    logger.error('从Vault加载密钥失败:', error);
    throw error;
  }
};

/**
 * 获取Vault客户端实例
 */
export const getVaultClient = () => {
  if (!vault) {
    throw new Error('Vault未初始化');
  }
  return vault;
};

/**
 * 获取特定密钥
 */
export const getSecret = async (path: string, key: string) => {
  try {
    if (!vault) {
      throw new Error('Vault未初始化');
    }
    
    const { data } = await vault.read(`secret/data/${path}`);
    
    if (!data || !data.data || !data.data[key]) {
      throw new Error(`密钥 ${path}/${key} 未找到`);
    }
    
    return data.data[key];
  } catch (error) {
    logger.error(`获取密钥 ${path}/${key} 失败:`, error);
    throw error;
  }
}; 