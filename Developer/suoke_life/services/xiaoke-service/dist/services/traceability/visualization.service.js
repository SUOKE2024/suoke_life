"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TraceabilityVisualizationService = void 0;
const logger_1 = require("../../utils/logger");
const cache_1 = require("../../core/cache");
const traceability_model_1 = require("../../models/traceability.model");
// 缓存配置
const VISUALIZATION_CACHE_TTL = 3600; // 1小时
/**
 * 溯源可视化服务
 * 负责提供产品溯源数据可视化和分析功能
 */
class TraceabilityVisualizationService {
    /**
     * 获取完整溯源链数据（用于产品生命周期可视化）
     * @param traceabilityId 溯源ID
     */
    async getTraceabilityChain(traceabilityId) {
        try {
            // 尝试从缓存获取
            const cacheKey = `traceability_chain:${traceabilityId}`;
            const cachedData = await (0, cache_1.getCache)(cacheKey);
            if (cachedData) {
                logger_1.logger.debug(`从缓存获取溯源链数据: ${traceabilityId}`);
                return cachedData;
            }
            // 从数据库获取完整溯源信息
            const traceability = await traceability_model_1.TraceabilityModel.findOne({
                traceabilityId
            }).lean();
            if (!traceability) {
                return null;
            }
            // 构建溯源链数据结构（优化用于前端可视化）
            const chainData = {
                id: traceability._id.toString(),
                traceabilityId: traceability.traceabilityId,
                productName: traceability.productName,
                nodes: [
                    {
                        id: 'origin',
                        type: 'origin',
                        label: '产品来源',
                        data: {
                            farmName: traceability.origin.farmName,
                            farmerName: traceability.origin.farmerName,
                            location: traceability.origin.location,
                            farmingType: traceability.origin.farmingType,
                            certifications: traceability.origin.certifications
                        },
                        date: traceability.harvestDate.toISOString(),
                        coordinates: traceability.origin.coordinates
                    }
                ],
                links: []
            };
            // 添加生产阶段节点
            let previousNode = 'origin';
            traceability.productionStages.forEach((stage, index) => {
                const nodeId = `stage_${index}`;
                // 添加节点
                chainData.nodes.push({
                    id: nodeId,
                    type: 'production',
                    label: stage.stageName,
                    data: {
                        location: stage.location,
                        operators: stage.operators,
                        processes: stage.processes,
                        qualityTests: stage.qualityTests || [],
                        notes: stage.notes
                    },
                    date: stage.startDate.toISOString(),
                    endDate: stage.endDate ? stage.endDate.toISOString() : null
                });
                // 添加链接
                chainData.links.push({
                    source: previousNode,
                    target: nodeId,
                    label: '流转到'
                });
                previousNode = nodeId;
            });
            // 添加物流节点
            if (traceability.logisticRecords && traceability.logisticRecords.length > 0) {
                traceability.logisticRecords.forEach((record, index) => {
                    const nodeId = `logistics_${index}`;
                    // 添加节点
                    chainData.nodes.push({
                        id: nodeId,
                        type: 'logistics',
                        label: `${record.transportType}运输`,
                        data: {
                            from: record.departureLocation,
                            to: record.arrivalLocation,
                            carrier: record.carrier,
                            temperature: record.temperature,
                            humidity: record.humidity,
                            trackingNumber: record.trackingNumber,
                            status: record.status
                        },
                        date: record.departureTime.toISOString(),
                        endDate: record.arrivalTime ? record.arrivalTime.toISOString() : null
                    });
                    // 添加链接
                    chainData.links.push({
                        source: previousNode,
                        target: nodeId,
                        label: '运输到'
                    });
                    previousNode = nodeId;
                });
            }
            // 添加区块链节点（如果存在）
            if (traceability.blockchainRecord) {
                const nodeId = 'blockchain';
                // 添加节点
                chainData.nodes.push({
                    id: nodeId,
                    type: 'blockchain',
                    label: '区块链记录',
                    data: {
                        blockchainType: traceability.blockchainRecord.blockchainType,
                        transactionId: traceability.blockchainRecord.transactionId,
                        blockNumber: traceability.blockchainRecord.blockNumber,
                        dataHash: traceability.blockchainRecord.dataHash,
                        verificationUrl: traceability.blockchainRecord.verificationUrl
                    },
                    date: traceability.blockchainRecord.timestamp.toISOString()
                });
                // 添加链接
                chainData.links.push({
                    source: previousNode,
                    target: nodeId,
                    label: '数据记录'
                });
            }
            // 更新缓存
            await (0, cache_1.setCache)(cacheKey, chainData, VISUALIZATION_CACHE_TTL);
            return chainData;
        }
        catch (error) {
            logger_1.logger.error('获取溯源链数据失败:', error);
            throw error;
        }
    }
    /**
     * 获取供应链地理分布数据（用于地图可视化）
     * @param productCategory 产品类别（可选）
     */
    async getSupplyChainGeoDistribution(productCategory) {
        try {
            // 尝试从缓存获取
            const cacheKey = `supply_chain_geo:${productCategory || 'all'}`;
            const cachedData = await (0, cache_1.getCache)(cacheKey);
            if (cachedData) {
                logger_1.logger.debug(`从缓存获取供应链地理分布数据: ${productCategory || 'all'}`);
                return cachedData;
            }
            // 构建查询条件
            const query = {};
            if (productCategory) {
                query.productCategory = productCategory;
            }
            // 从数据库聚合数据
            const originData = await traceability_model_1.TraceabilityModel.aggregate([
                { $match: query },
                {
                    $group: {
                        _id: {
                            location: '$origin.location',
                            farmingType: '$origin.farmingType'
                        },
                        count: { $sum: 1 },
                        products: { $push: '$productName' },
                        coordinates: { $first: '$origin.coordinates' }
                    }
                },
                {
                    $project: {
                        _id: 0,
                        location: '$_id.location',
                        farmingType: '$_id.farmingType',
                        count: 1,
                        products: { $slice: ['$products', 10] }, // 最多显示10个产品
                        coordinates: 1
                    }
                }
            ]);
            // 获取生产阶段位置数据
            const productionStageData = await traceability_model_1.TraceabilityModel.aggregate([
                { $match: query },
                { $unwind: '$productionStages' },
                {
                    $group: {
                        _id: {
                            location: '$productionStages.location',
                            stageName: '$productionStages.stageName'
                        },
                        count: { $sum: 1 },
                        products: { $push: '$productName' }
                    }
                },
                {
                    $project: {
                        _id: 0,
                        location: '$_id.location',
                        stageName: '$_id.stageName',
                        count: 1,
                        products: { $slice: ['$products', 10] }
                    }
                }
            ]);
            // 构建完整的地理分布数据
            const geoData = {
                origins: originData,
                productionStages: productionStageData,
                connections: [] // 前端可用于绘制供应链流向线
            };
            // 如果有坐标信息，生成连接数据
            if (originData.some(item => item.coordinates)) {
                const connectionsData = await traceability_model_1.TraceabilityModel.aggregate([
                    { $match: query },
                    { $unwind: '$productionStages' },
                    {
                        $project: {
                            originLocation: '$origin.location',
                            originCoordinates: '$origin.coordinates',
                            stageLocation: '$productionStages.location',
                            productName: 1
                        }
                    },
                    {
                        $group: {
                            _id: {
                                from: '$originLocation',
                                to: '$stageLocation'
                            },
                            count: { $sum: 1 },
                            details: { $push: { product: '$productName' } }
                        }
                    },
                    {
                        $project: {
                            _id: 0,
                            from: '$_id.from',
                            to: '$_id.to',
                            count: 1,
                            details: { $slice: ['$details', 5] }
                        }
                    }
                ]);
                geoData.connections = connectionsData;
            }
            // 更新缓存
            await (0, cache_1.setCache)(cacheKey, geoData, VISUALIZATION_CACHE_TTL);
            return geoData;
        }
        catch (error) {
            logger_1.logger.error('获取供应链地理分布数据失败:', error);
            throw error;
        }
    }
    /**
     * 获取溯源数据统计和趋势（用于数据分析）
     * @param startDate 开始日期（可选）
     * @param endDate 结束日期（可选）
     */
    async getTraceabilityAnalytics(startDate, endDate) {
        try {
            // 构建查询条件
            const query = {};
            if (startDate || endDate) {
                query.createdAt = {};
                if (startDate) {
                    query.createdAt.$gte = new Date(startDate);
                }
                if (endDate) {
                    query.createdAt.$lte = new Date(endDate);
                }
            }
            // 尝试从缓存获取
            const dateRange = startDate && endDate ? `${startDate}_${endDate}` : 'all';
            const cacheKey = `traceability_analytics:${dateRange}`;
            const cachedData = await (0, cache_1.getCache)(cacheKey);
            if (cachedData) {
                logger_1.logger.debug(`从缓存获取溯源数据分析: ${dateRange}`);
                return cachedData;
            }
            // 分类统计
            const categoryCounts = await traceability_model_1.TraceabilityModel.aggregate([
                { $match: query },
                {
                    $group: {
                        _id: '$productCategory',
                        count: { $sum: 1 }
                    }
                },
                {
                    $project: {
                        _id: 0,
                        category: '$_id',
                        count: 1
                    }
                },
                { $sort: { count: -1 } }
            ]);
            // 验证状态统计
            const verificationStatusCounts = await traceability_model_1.TraceabilityModel.aggregate([
                { $match: query },
                {
                    $group: {
                        _id: '$verificationStatus',
                        count: { $sum: 1 }
                    }
                },
                {
                    $project: {
                        _id: 0,
                        status: '$_id',
                        count: 1
                    }
                }
            ]);
            // 扫描量趋势（按天）
            const scanTrends = await traceability_model_1.TraceabilityModel.aggregate([
                { $match: query },
                {
                    $group: {
                        _id: {
                            year: { $year: '$updatedAt' },
                            month: { $month: '$updatedAt' },
                            day: { $dayOfMonth: '$updatedAt' }
                        },
                        totalScans: { $sum: '$scanCount' },
                        count: { $sum: 1 }
                    }
                },
                {
                    $project: {
                        _id: 0,
                        date: {
                            $dateToString: {
                                format: '%Y-%m-%d',
                                date: {
                                    $dateFromParts: {
                                        year: '$_id.year',
                                        month: '$_id.month',
                                        day: '$_id.day'
                                    }
                                }
                            }
                        },
                        scans: '$totalScans',
                        count: 1
                    }
                },
                { $sort: { date: 1 } }
            ]);
            // 农场类型分布
            const farmingTypeCounts = await traceability_model_1.TraceabilityModel.aggregate([
                { $match: query },
                {
                    $group: {
                        _id: '$origin.farmingType',
                        count: { $sum: 1 }
                    }
                },
                {
                    $project: {
                        _id: 0,
                        farmingType: '$_id',
                        count: 1
                    }
                },
                { $sort: { count: -1 } }
            ]);
            // 产品生产周期分析
            const productionDurationAnalysis = await traceability_model_1.TraceabilityModel.aggregate([
                { $match: query },
                { $unwind: '$productionStages' },
                {
                    $group: {
                        _id: '$traceabilityId',
                        productName: { $first: '$productName' },
                        category: { $first: '$productCategory' },
                        firstStage: { $min: '$productionStages.startDate' },
                        lastStage: { $max: '$productionStages.endDate' }
                    }
                },
                {
                    $project: {
                        _id: 0,
                        traceabilityId: '$_id',
                        productName: 1,
                        category: 1,
                        duration: {
                            $divide: [
                                { $subtract: ['$lastStage', '$firstStage'] },
                                86400000 // 毫秒转天
                            ]
                        }
                    }
                },
                {
                    $match: {
                        duration: { $gt: 0 } // 过滤无效数据
                    }
                },
                {
                    $group: {
                        _id: '$category',
                        averageDuration: { $avg: '$duration' },
                        minDuration: { $min: '$duration' },
                        maxDuration: { $max: '$duration' },
                        count: { $sum: 1 }
                    }
                },
                {
                    $project: {
                        _id: 0,
                        category: '$_id',
                        averageDuration: { $round: ['$averageDuration', 1] },
                        minDuration: { $round: ['$minDuration', 1] },
                        maxDuration: { $round: ['$maxDuration', 1] },
                        count: 1
                    }
                },
                { $sort: { averageDuration: 1 } }
            ]);
            // 构建完整分析数据
            const analyticsData = {
                summary: {
                    total: await traceability_model_1.TraceabilityModel.countDocuments(query),
                    verified: verificationStatusCounts.find(i => i.status === 'verified')?.count || 0,
                    pending: verificationStatusCounts.find(i => i.status === 'pending')?.count || 0,
                    failed: verificationStatusCounts.find(i => i.status === 'failed')?.count || 0
                },
                categoryCounts,
                verificationStatusCounts,
                scanTrends,
                farmingTypeCounts,
                productionDurationAnalysis,
                period: {
                    startDate: startDate || 'all',
                    endDate: endDate || 'current'
                }
            };
            // 更新缓存
            await (0, cache_1.setCache)(cacheKey, analyticsData, VISUALIZATION_CACHE_TTL);
            return analyticsData;
        }
        catch (error) {
            logger_1.logger.error('获取溯源数据分析失败:', error);
            throw error;
        }
    }
    /**
     * 获取质量监控数据
     * @param productId 产品ID（可选）
     */
    async getQualityMonitoringData(productId) {
        try {
            // 构建查询条件
            const query = {};
            if (productId) {
                query.productId = productId;
            }
            // 从数据库获取质量测试数据
            const qualityData = await traceability_model_1.TraceabilityModel.aggregate([
                { $match: query },
                { $unwind: '$productionStages' },
                { $unwind: { path: '$productionStages.qualityTests', preserveNullAndEmptyArrays: false } },
                {
                    $project: {
                        productName: 1,
                        productCategory: 1,
                        stageName: '$productionStages.stageName',
                        qualityTest: '$productionStages.qualityTests',
                        testDate: '$productionStages.startDate'
                    }
                },
                {
                    $group: {
                        _id: {
                            category: '$productCategory',
                            testType: '$qualityTest.testType'
                        },
                        tests: {
                            $push: {
                                productName: '$productName',
                                stageName: '$stageName',
                                result: '$qualityTest.result',
                                standard: '$qualityTest.standard',
                                date: '$testDate'
                            }
                        },
                        passCount: {
                            $sum: {
                                $cond: [
                                    { $eq: ['$qualityTest.passed', true] },
                                    1,
                                    0
                                ]
                            }
                        },
                        failCount: {
                            $sum: {
                                $cond: [
                                    { $eq: ['$qualityTest.passed', false] },
                                    1,
                                    0
                                ]
                            }
                        },
                        totalCount: { $sum: 1 }
                    }
                },
                {
                    $project: {
                        _id: 0,
                        category: '$_id.category',
                        testType: '$_id.testType',
                        passRate: {
                            $multiply: [
                                { $divide: ['$passCount', '$totalCount'] },
                                100
                            ]
                        },
                        passCount: 1,
                        failCount: 1,
                        totalCount: 1,
                        sampleTests: { $slice: ['$tests', 5] } // 提供一些样例测试结果
                    }
                },
                { $sort: { passRate: -1 } }
            ]);
            return {
                qualityTests: qualityData,
                summary: {
                    testTypes: qualityData.length,
                    totalTests: qualityData.reduce((sum, item) => sum + item.totalCount, 0),
                    averagePassRate: qualityData.length
                        ? qualityData.reduce((sum, item) => sum + item.passRate, 0) / qualityData.length
                        : 0
                }
            };
        }
        catch (error) {
            logger_1.logger.error('获取质量监控数据失败:', error);
            throw error;
        }
    }
}
exports.TraceabilityVisualizationService = TraceabilityVisualizationService;
exports.default = new TraceabilityVisualizationService();
