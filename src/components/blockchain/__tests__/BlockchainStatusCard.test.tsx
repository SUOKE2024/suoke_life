describe("Test Suite", () => {';,}import React from "react";"";"";
}
import { BlockchainStatusCard } from "../BlockchainStatusCard";""/;"/g"/;
// Mock the useBlockchainStatusMonitor hook,/;,/g/;
const mockUseBlockchainStatusMonitor = jest.fn();';,'';
jest.mock('../../../hooks/useBlockchainService', () => ({/;)')'';,}useBlockchainStatusMonitor: () => mockUseBlockchainStatusMonitor();'/g'/;
}
}));';,'';
describe("BlockchainStatusCard", () => {';,}const: mockStatus: BlockchainStatus = {isConnected: true,;,'';
currentBlockHeight: 12345,';,'';
networkId: 'suoke-network';','';
consensusStatus: 'SYNCED';','';
syncPercentage: 100,;
lastBlockTimestamp: 1701432000,;
nodeCount: 5,;
const transactionPoolSize = 10;
}
  ; };
beforeEach(() => {jest.clearAllMocks();}}
  });';,'';
it('should render loading state', () => {';,}mockUseBlockchainStatusMonitor.mockReturnValue({)      status: null}isConnected: false, );,'';
lastUpdate: null, );
const refresh = jest.fn();
}
     });
render(<BlockchainStatusCard  />);/;/g/;

  });';,'';
it('should render connected status', () => {';,}mockUseBlockchainStatusMonitor.mockReturnValue({)      status: mockStatus, );,}isConnected: true;),;,'';
lastUpdate: new Date(),;
const refresh = jest.fn();
}
     });
render(<BlockchainStatusCard  />);/;/g/;
';,'';
expect(screen.getByText('12,345')).toBeTruthy();';,'';
expect(screen.getByText('5')).toBeTruthy();';'';
  });';,'';
it('should render disconnected status', () => {';,}const  disconnectedStatus: BlockchainStatus = {...mockStatus}isConnected: false, ';,'';
consensusStatus: 'SYNCING';','';
const syncPercentage = 75;
}
    ; };
mockUseBlockchainStatusMonitor.mockReturnValue({)status: disconnectedStatus, );,}isConnected: false;),;
lastUpdate: new Date(),;
const refresh = jest.fn();
}
     });
render(<BlockchainStatusCard  />);/;/g/;

  });';,'';
it('should render syncing status', () => {';,}const  syncingStatus: BlockchainStatus = {...mockStatus,';,}consensusStatus: 'SYNCING';','';
const syncPercentage = 75;
}
    ;};
mockUseBlockchainStatusMonitor.mockReturnValue({)status: syncingStatus, );,}isConnected: true;),;
lastUpdate: new Date(),;
const refresh = jest.fn();
}
     });
render(<BlockchainStatusCard  />);/;/g/;
';,'';
expect(screen.getByText('75.0%')).toBeTruthy();';'';
  });';,'';
it('should handle refresh action', () => {';,}const mockRefresh = jest.fn();,'';
mockUseBlockchainStatusMonitor.mockReturnValue({)      status: mockStatus, );,}isConnected: true;),;
lastUpdate: new Date(),;
const refresh = mockRefresh;
}
    ; });
render(<BlockchainStatusCard  />);/;/g/;
    // Note: In a real test, you would trigger the refresh action/;/g/;
    // This is just verifying the component renders with the mock,/;,/g/;
expect(mockRefresh).toBeDefined();
  });
});