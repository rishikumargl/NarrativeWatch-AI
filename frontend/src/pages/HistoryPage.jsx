import React, { useState, useEffect } from 'react';
import { getHistory } from '../services/api';

export default function HistoryPage() {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await getHistory();
        setAnalyses(data.analyses || []);
      } catch (err) {
        console.error('Failed to load history:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-4xl font-bold text-white mb-8">📚 Analysis History</h2>

        {loading ? (
          <p className="text-gray-300">Loading...</p>
        ) : analyses.length === 0 ? (
          <div className="bg-gray-800/50 p-12 rounded-lg border border-gray-700 text-center">
            <p className="text-gray-400 mb-4">No analyses yet</p>
            <a href="/" className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg">
              Start Your First Analysis
            </a>
          </div>
        ) : (
          <div className="space-y-4">
            {analyses.map((analysis) => (
              <div key={analysis.id} className="bg-gray-800/50 p-6 rounded-lg border border-gray-700 hover:border-blue-500 transition">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-white font-bold text-lg">{analysis.url}</h3>
                    <p className="text-gray-400 text-sm mt-1">{new Date(analysis.created_at).toLocaleString()}</p>
                  </div>
                  <div className="text-right">
                    <div className={`text-3xl font-bold ${analysis.trust_score >= 75 ? 'text-green-400' : analysis.trust_score >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>
                      {analysis.trust_score}
                    </div>
                    <p className="text-gray-400 text-sm">Trust Score</p>
                  </div>
                </div>
                <a href={`/results/${analysis.id}`} className="mt-4 inline-block text-blue-400 hover:text-blue-300">
                  View Details →
                </a>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
