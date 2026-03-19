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
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
          <span className="text-2xl">🎯</span>
          Agent Activity Feed
        </h2>
        {isActive && (
          <div className="flex items-center gap-2">
            <div className="animate-pulse w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-sm text-green-600 font-medium">Live</span>
          </div>
        )}
      </div>

      <div
        ref={feedRef}
        className="bg-gray-900 rounded-lg p-4 h-96 overflow-y-auto font-mono text-sm shadow-inner"
        style={{ scrollBehavior: 'smooth' }}
      >
        {events.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <p className="text-lg mb-2">🤖</p>
              <p>Waiting for KYC document upload...</p>
              <p className="text-xs mt-2">Agent reasoning logs will appear here</p>
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            {events.map((event, index) => (
              <div
                key={index}
                className="border-l-2 border-gray-700 pl-3 py-1 hover:bg-gray-800 transition-colors"
              >
                <div className="flex items-start gap-2">
                  <span className="text-lg leading-none">{getEventIcon(event.type)}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`font-semibold ${getEventColor(event.type)}`}>
                        {event.agent?.toUpperCase() || event.type.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500">
                        {formatTimestamp(event.timestamp)}
                      </span>
                    </div>
                    <div className="text-gray-300 whitespace-pre-wrap break-words">
                      {event.message}
                    </div>
                    {event.details && (
                      <details className="mt-2">
                        <summary className="text-xs text-blue-400 cursor-pointer hover:text-blue-300">
                          View Details
                        </summary>
                        <pre className="mt-2 text-xs text-gray-400 bg-gray-800 p-2 rounded overflow-x-auto">
                          {JSON.stringify(event.details, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                </div>
              </div>
            ))}
            
            {isActive && (
              <div className="flex items-center gap-2 text-gray-500 animate-pulse">
                <span className="text-lg">⚙️</span>
                <span>Processing...</span>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
        <span>{events.length} events</span>
        {events.length > 0 && (
          <button
            onClick={() => {
              if (feedRef.current) {
                feedRef.current.scrollTop = feedRef.current.scrollHeight;
              }
            }}
            className="text-blue-600 hover:text-blue-700"
          >
            Scroll to bottom
          </button>
        )}
      </div>
    </div>
  );
};