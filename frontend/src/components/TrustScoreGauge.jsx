import React from 'react';

export default function TrustScoreGauge({ score = 75, riskLevel = "MEDIUM" }) {
  const getColor = () => {
    if (score >= 75) return "text-green-400";
    if (score >= 50) return "text-yellow-400";
    if (score >= 25) return "text-orange-400";
    return "text-red-400";
  };

  const getRiskColor = () => {
    if (riskLevel === "LOW") return "bg-green-500/20 border-green-500 text-green-300";
    if (riskLevel === "MEDIUM") return "bg-yellow-500/20 border-yellow-500 text-yellow-300";
    if (riskLevel === "HIGH") return "bg-orange-500/20 border-orange-500 text-orange-300";
    return "bg-red-500/20 border-red-500 text-red-300";
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative w-48 h-48">
        <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-90">
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="#374151"
            strokeWidth="8"
          />
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            strokeDasharray={`${(score / 100) * 283} 283`}
            className={getColor()}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className={`text-5xl font-bold ${getColor()}`}>{score}</div>
            <div className="text-gray-400 text-sm">Trust Score</div>
          </div>
        </div>
      </div>
      
      <div className={`px-4 py-2 rounded-lg border-2 font-semibold ${getRiskColor()}`}>
        Risk Level: {riskLevel}
      </div>
    </div>
  );
}
