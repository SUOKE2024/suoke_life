import neo4j, { Driver, Session } from 'neo4j-driver';
import config from '../../config';
import logger from '../logger';

class Neo4jConnection {
  private static instance: Neo4jConnection;
  private driver: Driver | null = null;

  private constructor() {}

  public static getInstance(): Neo4jConnection {
    if (!Neo4jConnection.instance) {
      Neo4jConnection.instance = new Neo4jConnection();
    }
    return Neo4jConnection.instance;
  }

  public async connect(): Promise<void> {
    try {
      const { host, port, username, password, database } = config.graphDB;
      const uri = `neo4j://${host}:${port}`;

      this.driver = neo4j.driver(
        uri,
        neo4j.auth.basic(username, password),
        {
          maxConnectionPoolSize: config.graphDB.poolMax,
          connectionAcquisitionTimeout: 60000,
        }
      );

      // 验证连接
      await this.driver.verifyConnectivity();
      logger.info('Successfully connected to Neo4j database');
    } catch (error) {
      logger.error('Failed to connect to Neo4j:', error);
      throw error;
    }
  }

  public getSession(): Session {
    if (!this.driver) {
      throw new Error('Database connection not initialized');
    }
    return this.driver.session({
      database: config.graphDB.database,
      defaultAccessMode: neo4j.session.READ
    });
  }

  public async close(): Promise<void> {
    if (this.driver) {
      await this.driver.close();
      this.driver = null;
      logger.info('Neo4j connection closed');
    }
  }
}

export default Neo4jConnection;