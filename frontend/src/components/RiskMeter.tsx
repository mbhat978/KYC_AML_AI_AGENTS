import React from 'react';
import type { RiskCategory } from '../types';

interface RiskMeterProps {
  score: number;
  category: RiskCategory;
}

export const RiskMeter: React.FC<RiskMeterProps> = ({ score, category }) => {
  // Safely handle undefined or null score values (1-10 scale)
  const safeScore = score ?? 1;
  // Convert 1-10 scale to 0-100 percentage for visual display only
  const percentage = Math.min(Math.max(((safeScore - 1) / 9) * 100, 0), 100);
  
  const getRiskColor = () => {
    switch (category) {
      case 'LOW':
        return {
          bg: 'bg-green-100',
          border: 'border-green-500',
          text: 'text-green-700',
          fill: 'bg-green-500',
          glow: 'shadow-green-500/50'
        };
      case 'MEDIUM':
        return {
          bg: 'bg-yellow-100',
          border: 'border-yellow-500',
          text: 'text-yellow-700',
          fill: 'bg-yellow-500',
          glow: 'shadow-yellow-500/50'
        };
      case 'HIGH':
        return {
          bg: 'bg-orange-100',
          border: 'border-orange-500',
          text: 'text-orange-700',
          fill: 'bg-orange-500',
          glow: 'shadow-orange-500/50'
        };
      case 'CRITICAL':
        return {
          bg: 'bg-red-100',
          border: 'border-red-500',
          text: 'text-red-700',
          fill: 'bg-red-500',
          glow: 'shadow-red-500/50'
        };
      default:
        return {
          bg: 'bg-gray-100',
          border: 'border-gray-500',
          text: 'text-gray-700',
          fill: 'bg-gray-500',
          glow: 'shadow-gray-500/50'
        };
    }
  };

  const getRiskIcon = () => {
    switch (category) {
      case 'LOW':
        return '✅';
      case 'MEDIUM':
        return '⚠️';
      case 'HIGH':
        return '🔴';
      case 'CRITICAL':
        return '🚨';
      default:
        return '❓';
    }
  };

  const colors = getRiskColor();

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
          <span className="text-2xl">📊</span>
          Risk Assessment
        </h2>
      </div>

      <div className={`rounded-lg p-6 ${colors.bg} border-2 ${colors.border}`}>
        {/* Risk Score Circle */}
        <div className="flex items-center justify-center mb-6">
          <div className="relative">
            <svg className="transform -rotate-90 w-40 h-40">
              {/* Background circle */}
              <circle
                cx="80"
                cy="80"
                r="70"
                stroke="currentColor"
                strokeWidth="12"
                fill="transparent"
                className="text-gray-300"
              />
              {/* Progress circle */}
              <circle
                cx="80"
                cy="80"
                r="70"
                stroke="currentColor"
                strokeWidth="12"
                fill="transparent"
                strokeDasharray={`${2 * Math.PI * 70}`}
                strokeDashoffset={`${2 * Math.PI * 70 * (1 - percentage / 100)}`}
                className={`${colors.text} transition-all duration-1000 ease-out`}
                strokeLinecap="round"
              />
            </svg>
            {/* Center content */}
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
              <div className="text-4xl mb-1">{getRiskIcon()}</div>
              <div className={`text-3xl font-bold ${colors.text}`}>
                {safeScore.toFixed(1)}
              </div>
              <div className="text-xs text-gray-600">Risk Score</div>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-sm mb-2">
            <span className={`font-medium ${colors.text}`}>
              {category} RISK
            </span>
            <span className="text-gray-600">{safeScore.toFixed(1)} / 10</span>
          </div>
          <div className="w-full bg-gray-300 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full ${colors.fill} transition-all duration-1000 ease-out rounded-full ${colors.glow} shadow-lg`}
              style={{ width: `${percentage}%` }}
            />
          </div>
        </div>

        {/* Risk Scale Legend */}
        <div className="grid grid-cols-4 gap-2 text-xs mt-4">
          <div className="text-center">
            <div className="w-full bg-green-500 h-2 rounded mb-1"></div>
            <span className="text-green-700 font-medium">LOW</span>
            <div className="text-gray-600">1-2.5</div>
          </div>
          <div className="text-center">
            <div className="w-full bg-yellow-500 h-2 rounded mb-1"></div>
            <span className="text-yellow-700 font-medium">MEDIUM</span>
            <div className="text-gray-600">2.5-5</div>
          </div>
          <div className="text-center">
            <div className="w-full bg-orange-500 h-2 rounded mb-1"></div>
            <span className="text-orange-700 font-medium">HIGH</span>
            <div className="text-gray-600">5-7.5</div>
          </div>
          <div className="text-center">
            <div className="w-full bg-red-500 h-2 rounded mb-1"></div>
            <span className="text-red-700 font-medium">CRITICAL</span>
            <div className="text-gray-600">7.5-10</div>
          </div>
        </div>
      </div>
    </div>
  );
};