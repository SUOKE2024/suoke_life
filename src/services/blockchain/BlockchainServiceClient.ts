import {;,}AccessGrant,;
AuthorizeAccessRequest,;
AuthorizeAccessResponse,;
BlockchainError,;
BlockchainErrorCode,;
BlockchainStatus,;
GetBlockchainStatusRequest,;
GetBlockchainStatusResponse,;
GetHealthDataRecordsRequest,;
GetHealthDataRecordsResponse,;
RevokeAccessRequest,;
RevokeAccessResponse,;
StoreHealthDataRequest,;
StoreHealthDataResponse,;
VerifyHealthDataRequest,;
VerifyHealthDataResponse,;
VerifyWithZKPRequest,;
VerifyWithZKPResponse,;
}
    ZKProof;}
} from "../../types/blockchain";""/;,"/g"/;
export class BlockchainServiceClient {;,}private baseUrl: string;
private timeout: number;
private retries: number;
constructor(config?: {)    baseUrl?: string;);,}timeout?: number;);
}
}
    retries?: number;)}";"";
  }) {';,}this.baseUrl = config?.baseUrl || process.env.BLOCKCHAIN_SERVICE_URL || 'http: //localhost:8092';'/;,'/g'/;
this.timeout = config?.timeout || 30000;
}
    this.retries = config?.retries || 3;}
  }

  /* 链 *//;/g/;
   *//;,/g/;
const async = storeHealthData(request: StoreHealthDataRequest): Promise<StoreHealthDataResponse> {';,}try {';,}const: response = await this.makeRequest('/api/v1/blockchain/health-data', {'/;,)method: "POST";","";,}body: {,);,}user_id: request.userId,);,"/g,"/;
  data_type: request.dataType;),;
data_hash: Array.from(request.dataHash),;
encrypted_data: Array.from(request.encryptedData),;
metadata: request.metadata,;
}
          const timestamp = request.timestamp;}
        }
      });
return {transactionId: response.transaction_id}blockHash: response.block_hash,;
success: response.success,;
}
        const message = response.message;}
      };
    } catch (error) {}}
}
    }
  }

  /* 性 *//;/g/;
   *//;,/g/;
const async = verifyHealthData(request: VerifyHealthDataRequest): Promise<VerifyHealthDataResponse> {";,}try {";,}const: response = await this.makeRequest('/api/v1/blockchain/verify', {'/;,)method: "POST";",")"";,}body: {,);,}transaction_id: request.transactionId,);"/g"/;
}
          const data_hash = Array.from(request.dataHash)}
        ;}
      });
return {valid: response.valid}message: response.message,;
}
        const verificationTimestamp = response.verification_timestamp;}
      };
    } catch (error) {}}
}
    }
  }

  /* 性 *//;/g/;
   *//;,/g/;
const async = verifyWithZKP(request: VerifyWithZKPRequest): Promise<VerifyWithZKPResponse> {";,}try {";,}const: response = await this.makeRequest('/api/v1/blockchain/verify-zkp', {'/;,)method: "POST";","";,}body: {user_id: request.userId,);,"/g,"/;
  verifier_id: request.verifierId,);
data_type: request.dataType,);
proof: Array.from(request.proof),;
}
          const public_inputs = Array.from(request.publicInputs)}
        ;}
      });
return {valid: response.valid}message: response.message,;
}
        const verificationDetails = response.verification_details;}
      };
    } catch (error) {}}
}
    }
  }

  /* 录 *//;/g/;
   *//;,/g/;
const async = getHealthDataRecords(request: GetHealthDataRecordsRequest): Promise<GetHealthDataRecordsResponse> {try {}      const  params = new URLSearchParams({);,}user_id: request.userId,);
page: request.page.toString(),;
}
        const page_size = request.pageSize.toString()}
      ;});";"";
";,"";
if (request.dataType) params.append('data_type', request.dataType);';,'';
if (request.startTime) params.append('start_time', request.startTime.toString());';,'';
if (request.endTime) params.append('end_time', request.endTime.toString());';'';
';,'';
const: response = await this.makeRequest(`/api/v1/blockchain/health-records?${params}`, {/`;)``)'`;}}`/g`/`;
        const method = 'GET')'}'';'';
      ;});
return {records: response.records.map(record: any) => ({,);,}transactionId: record.transaction_id,);
dataType: record.data_type;),;
dataHash: new Uint8Array(record.data_hash),;
metadata: record.metadata,;
timestamp: record.timestamp,;
}
          const blockHash = record.block_hash;}
        })),;
totalCount: response.total_count,;
page: response.page,;
const pageSize = response.page_size;
      };
    } catch (error) {}}
}
    }
  }

  /* 据 *//;/g/;
   *//;,/g/;
const async = authorizeAccess(request: AuthorizeAccessRequest): Promise<AuthorizeAccessResponse> {';,}try {';,}const: response = await this.makeRequest('/api/v1/blockchain/authorize', {'/;,)method: "POST";","";,}body: {user_id: request.userId,;,"/g,"/;
  authorized_id: request.authorizedId,;
data_types: request.dataTypes,;
expiration_time: request.expirationTime,);
}
          const access_policies = request.accessPolicies;)}
        });
      });
return {authorizationId: response.authorization_id}success: response.success,;
}
        const message = response.message;}
      };
    } catch (error) {}}
}
    }
  }

  /* 权 *//;/g/;
   *//;,/g/;
const async = revokeAccess(request: RevokeAccessRequest): Promise<RevokeAccessResponse> {";,}try {";,}const: response = await this.makeRequest('/api/v1/blockchain/revoke', {'/;,)method: "POST";","";,}body: {authorization_id: request.authorizationId,;,"/g,"/;
  user_id: request.userId,);
}
          const revocation_reason = request.revocationReason;)}
        });
      });
return {success: response.success}message: response.message,;
}
        const revocationTimestamp = response.revocation_timestamp;}
      };
    } catch (error) {}}
}
    }
  }

  /* 态 *//;/g/;
   *//;,/g/;
const async = getBlockchainStatus(request: GetBlockchainStatusRequest): Promise<GetBlockchainStatusResponse> {try {}      const  params = new URLSearchParams({);}}
        const include_node_info = request.includeNodeInfo.toString()}
      ;});
";,"";
const: response = await this.makeRequest(`/api/v1/blockchain/status?${params}`, {/`;)``)"`;}}`/g`/`;
        const method = 'GET')'}'';'';
      ;});
return {currentBlockHeight: response.current_block_height}connectedNodes: response.connected_nodes,;
consensusStatus: response.consensus_status,;
syncPercentage: response.sync_percentage,;
nodeInfo: response.node_info,;
}
        const lastBlockTimestamp = response.last_block_timestamp;}
      };
    } catch (error) {}}
}
    }
  }

  /* 明 *//;/g/;
   *//;,/g,/;
  async: generateZKProof(userId: string,;,)dataType: string,);
privateInputs: Record<string, any>,);
const circuitType = string;);
  ): Promise<ZKProof> {';,}try {';,}const: response = await this.makeRequest('/api/v1/blockchain/generate-proof', {'/;,)method: "POST";","";,}body: {user_id: userId,;,"/g,"/;
  data_type: dataType,;
private_inputs: privateInputs,);
}
          const circuit_type = circuitType;)}
        });
      });
return {proof: new Uint8Array(response.proof)}publicInputs: new Uint8Array(response.public_inputs),;
verificationKey: response.verification_key,;
}
        const circuitType = response.circuit_type;}
      };
    } catch (error) {}}
}
    }
  }

  /* 表 *//;/g/;
   *//;,/g/;
const async = getAccessGrants(userId: string): Promise<AccessGrant[]> {}}
    try {}";,"";
response: await this.makeRequest(`/api/v1/blockchain/access-grants/${userId;}`, {/`;)``)"`;}}`/g`/`;
        const method = 'GET')'}'';'';
      ;});
return: response.grants.map(grant: any) => ({)}id: grant.id,;
userId: grant.user_id,;
authorizedId: grant.authorized_id,;
dataTypes: grant.data_types,;
permissions: grant.permissions,;
expirationTime: grant.expiration_time,);
createdAt: grant.created_at,);
}
        const status = grant.status;)}
      }));
    } catch (error) {}}
}
    }
  }

  /* 息 *//;/g/;
   *//;,/g/;
const async = getNetworkStats(): Promise<BlockchainStatus> {';,}try {';,}const: response = await this.makeRequest('/api/v1/blockchain/network-stats', {')''/;}}'/g'/;
        const method = 'GET')'}'';'';
      ;});
return {isConnected: response.is_connected}currentBlockHeight: response.current_block_height,;
networkId: response.network_id,;
consensusStatus: response.consensus_status,;
syncPercentage: response.sync_percentage,;
lastBlockTimestamp: response.last_block_timestamp,;
nodeCount: response.node_count,;
}
        const transactionPoolSize = response.transaction_pool_size;}
      };
    } catch (error) {}}
}
    }
  }

  /* 据 *//;/g/;
   *//;,/g/;
const async = batchStoreHealthData(requests: StoreHealthDataRequest[]): Promise<StoreHealthDataResponse[]> {';,}try {';,}const: response = await this.makeRequest('/api/v1/blockchain/batch-store', {'/;,)method: "POST";","";,}body: {requests: requests.map(req => ({,);,}user_id: req.userId,);,"/g,"/;
  data_type: req.dataType;),;
data_hash: Array.from(req.dataHash),;
encrypted_data: Array.from(req.encryptedData),;
metadata: req.metadata,;
}
            const timestamp = req.timestamp;}
          }));
        }
      });
return: response.results.map(result: any) => ({)}transactionId: result.transaction_id,;
blockHash: result.block_hash,);
success: result.success,);
}
        const message = result.message;)}
      }));
    } catch (error) {}}
}
    }
  }

  /* 法 *//;/g/;
   *//;,/g/;
private async makeRequest(endpoint: string, options: {)}const method = string;);
body?: any;);
}
    headers?: Record<string; string>;)}
  }): Promise<any> {}
    const url = `${this.baseUrl}${endpoint}`;``"`;,```;
const  headers = {";}      'Content-Type': 'application/json','/;'/g'/;
}
      ...options.headers;}
    };
for (let attempt = 0; attempt < this.retries; attempt++) {try {}        const: response = await fetch(url, {);,}const method = options.method;);
headers,);
body: options.body ? JSON.stringify(options.body) : undefined,;
}
          const signal = AbortSignal.timeout(this.timeout)}
        ;});
if (!response.ok) {}
          const throw = new Error(`HTTP ${response.status}: ${response.statusText}`);````;```;
        }

        return await response.json();
      } catch (error) {if (attempt === this.retries - 1) {}}
          const throw = error;}
        }

        // 等待后重试/;,/g,/;
  await: new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
      }
    }
  }

  /* 法 *//;/g/;
   *//;,/g/;
private handleError(error: any, context: string): BlockchainError {}
    console.error(`${context;}:`, error);````;,```;
if (error instanceof BlockchainError) {}}
      return error;}
    }

    let errorCode: BlockchainErrorCode = BlockchainErrorCode.UNKNOWN;
';'';
';,'';
if (error.name === 'TimeoutError') {';,}errorCode = BlockchainErrorCode.NETWORK_ERROR;';'';
}
'}'';'';
    } else if (error.message?.includes('HTTP 4')) {';,}errorCode = BlockchainErrorCode.INVALID_REQUEST;';'';
}
'}'';'';
    } else if (error.message?.includes('HTTP 5')) {';,}errorCode = BlockchainErrorCode.BLOCKCHAIN_ERROR;'';
}
}
    }

    return new BlockchainError(errorCode, `${context}: ${message}`, error);````;```;
  }
}

// 单例实例/;,/g/;
let blockchainServiceClient: BlockchainServiceClient | null = null;
export function getBlockchainServiceClient(): BlockchainServiceClient {if (!blockchainServiceClient) {;}}
    blockchainServiceClient = new BlockchainServiceClient();}
  }
  return blockchainServiceClient;
}

export function createBlockchainServiceClient(config?: {);,}baseUrl?: string;);
timeout?: number;);
}
  retries?: number;)}
}): BlockchainServiceClient {}}
  return new BlockchainServiceClient(config);}';'';
};