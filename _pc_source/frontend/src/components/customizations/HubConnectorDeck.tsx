import React, { useState } from 'react';
import type { ConnectorCard } from '../../types/domain';
import type { ConnectJob } from '../../api/client';
import { HubConnectorCard } from './HubConnectorCard';

interface HubConnectorDeckProps {
  connectors: ConnectorCard[];
  jobs?: Record<string, ConnectJob>;
  onConnect: (connectorId: string) => Promise<unknown> | void;
  onRunTest: (connectorId: string) => Promise<unknown> | void;
  testingId: string | null;
}

export const HubConnectorDeck: React.FC<HubConnectorDeckProps> = ({
  connectors,
  jobs = {},
  onConnect,
  onRunTest,
  testingId,
}) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (connectors.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-white/[0.09] px-6 py-12 text-center">
        <p className="text-[13px] text-zinc-400">Todavía no hay conectores registrados.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 items-start gap-4 md:grid-cols-2">
      {connectors.map((connector) => (
        <HubConnectorCard
          key={connector.connector_id}
          connector={connector}
          job={jobs[connector.connector_id]}
          expanded={expandedId === connector.connector_id}
          onToggle={() =>
            setExpandedId((current) => (current === connector.connector_id ? null : connector.connector_id))
          }
          onConnect={onConnect}
          onRunTest={onRunTest}
          testing={testingId === connector.connector_id}
        />
      ))}
    </div>
  );
};
