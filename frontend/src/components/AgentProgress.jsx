import React from 'react';

export default function AgentProgress({ agents = {} }) {
  const agentNames = [
    'content_analyzer',
    'rag_agent',
    'research_agent',
    'bias_detector',
    'bot_detector',
    'campaign_detector',
    'synthesis_agent',
    'reviewer_agent'
  ];

  return (
    <div className="space-y-4">
      <h3 className="text-xl font-bold text-white mb-6">Agent Execution Progress</h3>
      
      {agentNames.map((name) => {
        const agent = agents[name];
        const isComplete = agent?.status === 'completed';
        const isRunning = agent?.status === 'in_progress';
        
        return (
          <div key={name} className="bg-gray-800/50 p-4 rounded-lg border border-gray-700 hover:border-blue-500 transition">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${
                  isComplete ? 'bg-green-400' : isRunning ? 'bg-blue-400 animate-pulse' : 'bg-gray-600'
                }`}/>
                <span className="text-white font-medium capitalize">{name.replace('_', ' ')}</span>
              </div>
              <span className={`text-xs font-bold ${
                isComplete ? 'text-green-400' : isRunning ? 'text-blue-400' : 'text-gray-500'
              }`}>
                {isComplete ? '✓ DONE' : isRunning ? '⚙ RUNNING' : 'PENDING'}
              </span>
            </div>
            
            <div className="w-full bg-gray-900 h-2 rounded-full overflow-hidden">
              <div className={`h-full rounded-full transition-all duration-500 ${
                isComplete ? 'w-full bg-green-500' : isRunning ? 'w-2/3 bg-blue-500' : 'w-0 bg-gray-600'
              }`} />
            </div>
            
            {agent?.findings && (
              <div className="mt-2 text-xs text-gray-400">
                Confidence: {Math.round((agent.confidence || 0) * 100)}%
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
