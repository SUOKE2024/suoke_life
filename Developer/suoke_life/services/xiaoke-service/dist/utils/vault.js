"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.setupVault = setupVault;
exports.getSecretFromVault = getSecretFromVault;
exports.hasSecret = hasSecret;
exports.listSecrets = listSecrets;
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const logger_1 = require("./logger");
const logger = (0, logger_1.createLogger)('vault');
// 密钥存储路径
const SECRETS_MOUNT_PATH = '/mnt/secrets-store';
/**
 * 初始化Vault集成
 */
async function setupVault() {
    try {
        if (!process.env.USE_VAULT) {
            logger.info('Vault integration not enabled');
            return;
        }
        // 检查密钥挂载路径是否存在
        if (fs_1.default.existsSync(SECRETS_MOUNT_PATH)) {
            logger.info(`Vault secrets mount path exists at ${SECRETS_MOUNT_PATH}`);
            // 列出可用的密钥
            const files = fs_1.default.readdirSync(SECRETS_MOUNT_PATH);
            logger.info(`Available secrets: ${files.join(', ')}`);
        }
        else {
            logger.warn(`Vault secrets mount path does not exist at ${SECRETS_MOUNT_PATH}`);
            // 如果在开发环境中，不存在挂载路径是正常的
            if (process.env.NODE_ENV !== 'production') {
                logger.info('Not in production, Vault integration will be simulated');
            }
            else {
                throw new Error('Vault secrets mount path not found in production environment');
            }
        }
    }
    catch (error) {
        logger.error('Failed to setup Vault integration', error);
        throw error;
    }
}
/**
 * 从Vault获取密钥
 *
 * @param secretName 密钥名称
 * @returns 密钥值，如果无法获取则返回null
 */
async function getSecretFromVault(secretName) {
    try {
        // 检查是否启用了Vault
        if (!process.env.USE_VAULT) {
            logger.warn(`Vault not enabled, can't get secret: ${secretName}`);
            return process.env[secretName.toUpperCase()] || null;
        }
        // 检查密钥文件路径
        const secretPath = path_1.default.join(SECRETS_MOUNT_PATH, secretName);
        if (fs_1.default.existsSync(secretPath)) {
            // 读取密钥文件
            const secret = fs_1.default.readFileSync(secretPath, 'utf8');
            logger.debug(`Successfully read secret: ${secretName}`);
            return secret.trim();
        }
        else {
            // 如果在开发环境，从环境变量获取
            if (process.env.NODE_ENV !== 'production') {
                logger.warn(`Secret file not found: ${secretName}, falling back to environment variable`);
                return process.env[secretName.toUpperCase()] || null;
            }
            else {
                logger.error(`Secret file not found in production: ${secretName}`);
                return null;
            }
        }
    }
    catch (error) {
        logger.error(`Error getting secret: ${secretName}`, error);
        return null;
    }
}
/**
 * 检查是否有特定的密钥
 *
 * @param secretName 密钥名称
 * @returns 是否存在密钥
 */
function hasSecret(secretName) {
    if (!process.env.USE_VAULT) {
        return !!process.env[secretName.toUpperCase()];
    }
    const secretPath = path_1.default.join(SECRETS_MOUNT_PATH, secretName);
    return fs_1.default.existsSync(secretPath);
}
/**
 * 获取所有可用的密钥名称
 *
 * @returns 密钥名称数组
 */
function listSecrets() {
    try {
        if (!process.env.USE_VAULT || !fs_1.default.existsSync(SECRETS_MOUNT_PATH)) {
            return [];
        }
        return fs_1.default.readdirSync(SECRETS_MOUNT_PATH);
    }
    catch (error) {
        logger.error('Error listing secrets', error);
        return [];
    }
}
