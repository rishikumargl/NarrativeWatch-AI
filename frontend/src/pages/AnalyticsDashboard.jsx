import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart, Bar, PieChart, Pie, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { TrendingUp, BarChart3, PieChart as PieIcon, TrendingDown, ArrowLeft, Home } from 'lucide-react';

export default function AnalyticsDashboard() {
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState(null);
  const [trustDist, setTrustDist] = useState(null);
  const [riskDist, setRiskDist] = useState(null);
  const [sentimentDist, setSentimentDist] = useState(null);
  const [categoryTrust, setCategoryTrust] = useState(null);
  const [topSources, setTopSources] = useState(null);
  const [trustTrend, setTrustTrend] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

      console.log('🔍 Fetching analytics from:', apiUrl);

      const [
        dashRes,
        trustRes,
        riskRes,
        sentimentRes,
        categoryRes,
        sourcesRes,
        trendRes
      ] = await Promise.all([
        fetch(`${apiUrl}/api/v1/analytics/dashboard`),
        fetch(`${apiUrl}/api/v1/analytics/trust-distribution`),
        fetch(`${apiUrl}/api/v1/analytics/risk-distribution`),
        fetch(`${apiUrl}/api/v1/analytics/sentiment-distribution`),
        fetch(`${apiUrl}/api/v1/analytics/trust-by-category`),
        fetch(`${apiUrl}/api/v1/analytics/top-sources`),
        fetch(`${apiUrl}/api/v1/analytics/trust-over-time`)
      ]);

      const dashData = await dashRes.json();
      const trustData = await trustRes.json();
      const riskData = await riskRes.json();
      const sentimentData = await sentimentRes.json();
      const categoryData = await categoryRes.json();
      const sourcesData = await sourcesRes.json();
      const trendData = await trendRes.json();

      console.log('📊 Dashboard:', dashData);
      console.log('📈 Trust Distribution:', trustData);
      console.log('⚠️ Risk Distribution:', riskData);

      setDashboard(dashData);
      setTrustDist(trustData);
      setRiskDist(riskData);
      setSentimentDist(sentimentData);
      setCategoryTrust(categoryData);
      setTopSources(sourcesData);
      setTrustTrend(trendData);
      setLoading(false);
    } catch (error) {
      console.error('❌ Failed to fetch analytics:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black flex items-center justify-center"><p className="text-white text-xl">Loading analytics...</p></div>;
  }

  const sum = dashboard?.summary || {};

  const trustDistData = trustDist ? [
    { name: '90-100', value: trustDist['90_100'] || 0 },
    { name: '75-89', value: trustDist['75_89'] || 0 },
    { name: '50-74', value: trustDist['50_74'] || 0 },
    { name: '25-49', value: trustDist['25_49'] || 0 },
    { name: '0-24', value: trustDist['0_24'] || 0 }
  ] : [];

  const riskData = riskDist ? [
    { name: 'LOW', value: riskDist.LOW || 0, fill: '#22c55e' },
    { name: 'MEDIUM', value: riskDist.MEDIUM || 0, fill: '#eab308' },
    { name: 'HIGH', value: riskDist.HIGH || 0, fill: '#f97316' },
    { name: 'CRITICAL', value: riskDist.CRITICAL || 0, fill: '#ef4444' }
  ] : [];

  const sentimentData = sentimentDist ? [
    { name: 'POSITIVE', value: sentimentDist.POSITIVE || 0, fill: '#22c55e' },
    { name: 'NEUTRAL', value: sentimentDist.NEUTRAL || 0, fill: '#6b7280' },
    { name: 'NEGATIVE', value: sentimentDist.NEGATIVE || 0, fill: '#ef4444' }
  ] : [];

  const categoryData = categoryTrust ? Object.entries(categoryTrust).map(([cat, trust]) => ({
    category: cat.replace(/_/g, ' ').toUpperCase(),
    trust_score: trust || 0
  })) : [];

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black overflow-hidden">
      {/* Background animations */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
      </div>

      {/* Header */}
      <nav className="relative z-10 border-b border-gray-800/30 bg-gray-900/20 backdrop-blur-md sticky top-0">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/projects')}
              className="p-2 hover:bg-gray-800/50 rounded-lg transition-colors"
              title="Back to projects"
            >
              <ArrowLeft className="w-5 h-5 text-gray-400 hover:text-white transition-colors" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-white">📊 Analytics Dashboard</h1>
              <p className="text-gray-400 text-sm mt-1">Insights and trends from your analysis history</p>
            </div>
          </div>
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 px-6 py-3 bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700 rounded-lg text-gray-300 font-semibold transition-all duration-300 hover:border-blue-500/50 group"
          >
            <Home className="w-5 h-5 group-hover:scale-110 transition-transform" />
            Home
          </button>
        </div>
      </nav>

      <div className="relative z-10 container mx-auto px-4 py-12">
        <div className="max-w-7xl mx-auto">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-6">
              <p className="text-blue-300 text-sm mb-2">Total Articles</p>
              <p className="text-3xl font-bold text-white">{sum.total_articles || 0}</p>
            </div>
            <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-6">
              <p className="text-green-300 text-sm mb-2">Avg Trust Score</p>
              <p className="text-3xl font-bold text-white">{sum.average_trust_score || 0}%</p>
            </div>
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-6">
              <p className="text-yellow-300 text-sm mb-2">Avg Bias Score</p>
              <p className="text-3xl font-bold text-white">{sum.average_bias_score || 0}</p>
            </div>
            <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-6">
              <p className="text-purple-300 text-sm mb-2">Approval Rate</p>
              <p className="text-3xl font-bold text-white">{sum.approval_rate || 0}%</p>
            </div>
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Trust Score Distribution */}
            <div className="bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Trust Score Distribution
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={trustDistData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip contentStyle={{backgroundColor: '#1f2937', border: '1px solid #374151'}} />
                  <Bar dataKey="value" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Risk Level Distribution */}
            <div className="bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Risk Level Distribution
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={riskData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({name, value}) => `${name}: ${value}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {riskData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{backgroundColor: '#1f2937', border: '1px solid #374151'}} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Sentiment Distribution */}
            <div className="bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <PieIcon className="w-5 h-5" />
                Sentiment Breakdown
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={sentimentData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({name, value}) => `${name}: ${value}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {sentimentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{backgroundColor: '#1f2937', border: '1px solid #374151'}} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Category Trust Scores */}
            <div className="bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Trust Score by Category
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={categoryData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="category" stroke="#9ca3af" angle={-45} textAnchor="end" height={80} />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip contentStyle={{backgroundColor: '#1f2937', border: '1px solid #374151'}} />
                  <Bar dataKey="trust_score" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Trust Trend */}
          {trustTrend && trustTrend.length > 0 && (
            <div className="bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl p-6 mb-8">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <TrendingDown className="w-5 h-5" />
                Trust Score Trend (30 Days)
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={trustTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="date" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <YAxis yAxisId="right" orientation="right" stroke="#ec4899" />
                  <Tooltip contentStyle={{backgroundColor: '#1f2937', border: '1px solid #374151'}} />
                  <Legend />
                  <Line type="monotone" dataKey="average_trust_score" stroke="#3b82f6" dot={{fill: '#3b82f6'}} />
                  <Line type="monotone" dataKey="articles_analyzed" stroke="#ec4899" yAxisId="right" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Top Sources */}
          {topSources && topSources.length > 0 && (
            <div className="bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">🔗 Top Sources</h3>
              <div className="space-y-3">
                {topSources.map((source, idx) => (
                  <div key={idx} className="bg-gray-800/30 rounded-lg p-4 flex justify-between items-center">
                    <div>
                      <p className="text-white font-semibold">{source.source}</p>
                      <p className="text-gray-400 text-sm">{source.article_count} articles analyzed</p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-blue-400">{source.average_trust_score}</p>
                      <p className="text-gray-400 text-xs">avg trust</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
