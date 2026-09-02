import React from 'react';

const AgentScoreBadge = ({ score, confidence, inverted = false }) => {
  // Determine score color
  let scoreColor = "text-success bg-success/10 border-success/30";
  
  if (inverted) {
    if (score > 60) scoreColor = "text-error bg-error/10 border-error/30";
    else if (score > 30) scoreColor = "text-warning bg-warning/10 border-warning/30";
  } else {
    if (score < 60) scoreColor = "text-error bg-error/10 border-error/30";
    else if (score < 80) scoreColor = "text-warning bg-warning/10 border-warning/30";
  }

  // Determine confidence color
  let confColor = "text-success bg-success/10";
  if (confidence?.toLowerCase() === "low") confColor = "text-error bg-error/10";
  else if (confidence?.toLowerCase() === "medium") confColor = "text-warning bg-warning/10";

  return (
    <div className="ml-auto flex items-center gap-3">
      {confidence && (
        <div className={`text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-md ${confColor}`}>
          {confidence} Confidence
        </div>
      )}
      {score !== undefined && (
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border ${scoreColor}`}>
          <span className="text-[10px] uppercase font-bold tracking-widest opacity-80">Section Score</span>
          <span className="text-xl font-black">{score}</span>
        </div>
      )}
    </div>
  );
};

export default AgentScoreBadge;
