import React, { useEffect, useRef } from 'react';
import type { StreamEvent } from '../types';

interface LiveFeedProps {
  events: StreamEvent[];
  isActive: boolean;
}

export const LiveFeed: React.FC<LiveFeedProps> = ({ events, isActive }) => {
  const feedRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new events arrive
  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [events]);

  const getEventColor = (type: string) => {
    switch (type) {
      case 'agent_start':
        return 'text-blue-400';
      case 'agent_end':
        return 'text-green-400';
      case 'reasoning':
        return 'text-yellow-300';
      case 'error':
        return 'text-red-400';
      case 'verification':
        return 'text-purple-400';
      case 'assessment':
        return 'text-orange-400';
      case 'decision':
        return 'text-cyan-400';
      default:
        return 'text-gray-300';
    }
  };

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'agent_start':
        return '▶️';
      case 'agent_end':
        return '✅';
      case 'reasoning':
        return '💭';
      case 'error':
        return '❌';
      case 'verification':
        return '🔍';
      case 'assessment':
        return '📊';
      case 'decision':
        return '⚖️';
      default:
        return '📝';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit',
      fractionalSecondDigits: 3
    });
  };

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          <span className="text-2xl">🎯</span>
          Agent Activity Feed
        </h2>
        {isActive && (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 border border-green-200 rounded-full animate-[slideIn_0.3s_ease-out]">
            <div className="animate-pulse w-2 h-2 bg-green-500 rounded-full shadow-lg shadow-green-500/50"></div>
            <span className="text-sm text-green-700 font-bold uppercase tracking-wide">Live</span>
          </div>
        )}
      </div>

      <div
        ref={feedRef}
        className="modern-card bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-5 h-96 overflow-y-auto font-mono text-sm shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-700"
        style={{ scrollBehavior: 'smooth' }}
      >
        {events.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-400">
            <div className="text-center">
              <p className="text-4xl mb-3 animate-pulse">🤖</p>
              <p className="text-base font-medium">Waiting for KYC document upload...</p>
              <p className="text-xs mt-2 opacity-75">Agent reasoning logs will appear here</p>
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            {events.map((event, index) => (
              <div
                key={index}
                className="border-l-3 border-gray-600 pl-4 py-2 hover:bg-gray-800/50 hover:border-blue-400 transition-all duration-200 rounded-r-lg animate-[slideIn_0.3s_ease-out]"
              >
                <div className="flex items-start gap-3">
                  <span className="text-xl leading-none transition-transform duration-200 hover:scale-125">{getEventIcon(event.type)}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-1.5">
                      <span className={`font-bold text-sm ${getEventColor(event.type)} uppercase tracking-wide`}>
                        {event.agent?.toUpperCase() || event.type.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500 font-medium">
                        {formatTimestamp(event.timestamp)}
                      </span>
                    </div>
                    <div className="text-gray-300 whitespace-pre-wrap break-words leading-relaxed">
                      {event.message}
                    </div>
                    {event.details && (
                      <details className="mt-2 group">
                        <summary className="text-xs text-blue-400 cursor-pointer hover:text-blue-300 font-medium transition-colors duration-200 flex items-center gap-1">
                          <span className="group-open:rotate-90 transition-transform duration-200">▶</span>
                          View Details
                        </summary>
                        <pre className="mt-2 text-xs text-gray-400 bg-gray-800/80 p-3 rounded-lg overflow-x-auto border border-gray-700 hover:border-gray-600 transition-colors duration-200">
                          {JSON.stringify(event.details, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                </div>
              </div>
            ))}
            
            {isActive && (
              <div className="flex items-center gap-3 text-gray-400 animate-pulse py-2 px-3 bg-gray-800/50 rounded-lg border border-gray-700">
                <span className="text-xl animate-spin">⚙️</span>
                <span className="font-medium">Processing...</span>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="mt-3 flex items-center justify-between text-xs">
        <span className="text-gray-600 font-medium flex items-center gap-2">
          <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
          {events.length} events
        </span>
        {events.length > 0 && (
          <button
            onClick={() => {
              if (feedRef.current) {
                feedRef.current.scrollTop = feedRef.current.scrollHeight;
              }
            }}
            className="modern-button text-blue-600 hover:text-blue-700 font-medium px-3 py-1.5 rounded-lg hover:bg-blue-50 transition-all duration-200"
          >
            ↓ Scroll to bottom
          </button>
        )}
      </div>
    </div>
  );
};