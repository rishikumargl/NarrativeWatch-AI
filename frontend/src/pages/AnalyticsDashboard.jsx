import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { BarChart, Bar, PieChart, Pie, LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { TrendingUp, BarChart3, PieChart as PieIcon, TrendingDown, ArrowLeft, Home, RefreshCw, Calendar } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import '../styles/dashboard.css';

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
  const [refreshing, setRefreshing] = useState(false);

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

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchAnalytics();
    setRefreshing(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <div className="spinner mx-auto mb-6"></div>
          <motion.p
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="text-white text-xl font-semibold"
          >
            Loading analytics dashboard...
          </motion.p>
          <p className="text-gray-400 text-sm mt-4">Preparing charts and insights</p>
        </motion.div>
      </div>
    );
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

  // Generate fake data for new charts (in real app, these would come from API)
  const botDetectionData = [
    { subject: 'Bot Score', A: 25, fullMark: 100 },
    { subject: 'Authenticity', A: 85, fullMark: 100 },
    { subject: 'Engagement', A: 70, fullMark: 100 },
    { subject: 'Interaction', A: 60, fullMark: 100 },
    { subject: 'Consistency', A: 75, fullMark: 100 }
  ];

  const misinformationData = [
    { name: 'Verified', value: sum.total_articles ? Math.floor(sum.total_articles * 0.7) : 0, fill: '#22c55e' },
    { name: 'Suspicious', value: sum.total_articles ? Math.floor(sum.total_articles * 0.2) : 0, fill: '#eab308' },
    { name: 'High Risk', value: sum.total_articles ? Math.floor(sum.total_articles * 0.1) : 0, fill: '#ef4444' }
  ];

  const entityData = [
    { entity: 'OpenAI', mentions: 45, fill: '#3b82f6' },
    { entity: 'Microsoft', mentions: 38, fill: '#8b5cf6' },
    { entity: 'Google', mentions: 35, fill: '#ec4899' },
    { entity: 'Meta', mentions: 28, fill: '#f59e0b' },
    { entity: 'Tesla', mentions: 22, fill: '#10b981' }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.8, ease: 'easeOut' }
    }
  };

  const chartVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: { duration: 1, ease: 'easeOut' }
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black overflow-hidden">
      {/* Background animations */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
      </div>

      {/* Header */}
      <motion.nav
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="relative z-10 border-b border-gray-800/30 bg-gray-900/20 backdrop-blur-md sticky top-0"
      >
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/projects')}
              className="p-2 hover:bg-gray-800/50 rounded-lg transition-colors"
              title="Back to projects"
            >
              <ArrowLeft className="w-5 h-5 text-gray-400 hover:text-white transition-colors" />
            </motion.button>
            <div>
              <h1 className="text-2xl font-bold text-white">📊 Analytics Dashboard</h1>
              <p className="text-gray-400 text-sm mt-1">Real-time insights and trends</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <motion.button
              whileHover={{ rotate: 360 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleRefresh}
              disabled={refreshing}
              className="p-2 hover:bg-gray-800/50 rounded-lg transition-colors"
              title="Refresh data"
            >
              <RefreshCw className={`w-5 h-5 text-gray-400 hover:text-white transition-colors ${refreshing ? 'animate-rotate' : ''}`} />
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/')}
              className="flex items-center gap-2 px-6 py-3 bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700 rounded-lg text-gray-300 font-semibold transition-all duration-300 hover:border-blue-500/50"
            >
              <Home className="w-5 h-5" />
              Home
            </motion.button>
          </div>
        </div>
      </motion.nav>

      <div className="relative z-10 container mx-auto px-4 py-12">
        <div className="max-w-7xl mx-auto">
          {/* Key Metrics */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8"
          >
            <MetricCard
              label="Total Articles"
              value={sum.total_articles || 0}
              color="blue"
              icon={BarChart3}
              delay={0}
            />
            <MetricCard
              label="Avg Trust Score"
              value={sum.average_trust_score || 0}
              color="green"
              icon={TrendingUp}
              suffix="%"
              decimals={1}
              delay={0.1}
            />
            <MetricCard
              label="Avg Bias Score"
              value={sum.average_bias_score || 0}
              color="yellow"
              icon={PieIcon}
              decimals={2}
              delay={0.2}
            />
            <MetricCard
              label="Approval Rate"
              value={sum.approval_rate || 0}
              color="purple"
              icon={TrendingDown}
              suffix="%"
              decimals={1}
              delay={0.3}
            />
          </motion.div>

          {/* Charts Grid - Row 1 (Trust, Risk, Sentiment, Category) */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8"
          >
            {/* Trust Score Distribution */}
            <motion.div
              variants={chartVariants}
              className="chart-container bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl p-6 card-hover"
            >
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Trust Score Distribution
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={trustDistData}>
                  <defs>
                    <linearGradient id="trustGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.8} />
                      <stop offset="100%" stopColor="#1e40af" stopOpacity={0.4} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip contentStyle={{backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px'}} />
                  <Bar dataKey="value" fill="url(#trustGradient)" animationDuration={1500} animationEasing="ease-in-out" />
                </BarChart>
              </ResponsiveContainer>
            </motion.div>

            {/* Risk Level Distribution */}
            <motion.div
              variants={chartVariants}
              className="chart-container bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl p-6 card-hover"
              transition={{ delay: 0.2 }}
            >
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
                    animationDuration={1500}
                    animationEasing="ease-in-out"
                  >
                    {riskData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px'}} />
                </PieChart>
              </ResponsiveContainer>
            </motion.div>

            {/* Sentiment Distribution */}
            <motion.div
              variants={chartVariants}
              className="chart-container bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl p-6 card-hover"
              transition={{ delay: 0.3 }}
            >
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
                    animationDuration={1500}
                    animationEasing="ease-in-out"
                  >
                    {sentimentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px'}} />
                </PieChart>
              </ResponsiveContainer>
            </motion.div>

            {/* Category Trust Scores */}
            <motion.div
              variants={chartVariants}
              className="chart-container bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl p-6 card-hover"
              transition={{ delay: 0.4 }}
            >
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Trust by Category
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={categoryData}>
                  <defs>
                    <linearGradient id="categoryGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#10b981" stopOpacity={0.8} />
                      <stop offset="100%" stopColor="#047857" stopOpacity={0.4} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="category" stroke="#9ca3af" angle={-45} textAnchor="end" height={80} />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip contentStyle={{backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px'}} />
                  <Bar dataKey="trust_score" fill="url(#categoryGradient)" animationDuration={1500} animationEasing="ease-in-out" />
                </BarChart>
              </ResponsiveContainer>
            </motion.div>
          </motion.div>

          {/* Charts Grid - Row 2 (New Charts) */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8"
          >
            {/* Bot Detection Radar */}
            <motion.div
              variants={chartVariants}
              className="chart-container bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl p-6 card-hover"
            >
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                🤖 Bot Detection Analysis
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={botDetectionData}>
                  <PolarGrid stroke="#374151" />
                  <PolarAngleAxis dataKey="subject" stroke="#9ca3af" />
                  <PolarRadiusAxis stroke="#9ca3af" />
                  <Radar name="Detection Score" dataKey="A" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.6} animationDuration={1500} />
                  <Tooltip contentStyle={{backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px'}} />
                </RadarChart>
              </ResponsiveContainer>
            </motion.div>

            {/* Misinformation Risk */}
            <motion.div
              variants={chartVariants}
              className="chart-container bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl p-6 card-hover"
              transition={{ delay: 0.2 }}
            >
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                ⚠️ Misinformation Risk Distribution
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={misinformationData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({name, value}) => `${name}: ${value}`}
                    outerRadius={80}
                    innerRadius={40}
                    fill="#8884d8"
                    dataKey="value"
                    animationDuration={1500}
                    animationEasing="ease-in-out"
                  >
                    {misinformationData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px'}} />
                </PieChart>
              </ResponsiveContainer>
            </motion.div>

            {/* Entity Frequency */}
            <motion.div
              variants={chartVariants}
              className="chart-container bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl p-6 card-hover"
              transition={{ delay: 0.3 }}
            >
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                🏆 Top Entities Mentioned
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={entityData}
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 150, bottom: 5 }}
                >
                  <defs>
                    <linearGradient id="entityGradient" x1="0" y1="0" x2="1" y2="0">
                      <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.8} />
                      <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0.4} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis type="number" stroke="#9ca3af" />
                  <YAxis dataKey="entity" type="category" stroke="#9ca3af" width={140} />
                  <Tooltip contentStyle={{backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px'}} />
                  <Bar dataKey="mentions" fill="url(#entityGradient)" animationDuration={1500} animationEasing="ease-in-out" />
                </BarChart>
              </ResponsiveContainer>
            </motion.div>

            {/* Article Volume Timeline */}
            {trustTrend && trustTrend.length > 0 && (
              <motion.div
                variants={chartVariants}
                className="chart-container bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl p-6 card-hover"
                transition={{ delay: 0.4 }}
              >
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  📈 Article Volume Timeline
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={trustTrend}>
                    <defs>
                      <linearGradient id="volumeGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.8} />
                        <stop offset="100%" stopColor="#f59e0b" stopOpacity={0.1} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="date" stroke="#9ca3af" />
                    <YAxis stroke="#9ca3af" />
                    <Tooltip contentStyle={{backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px'}} />
                    <Area
                      type="monotone"
                      dataKey="articles_analyzed"
                      stroke="#f59e0b"
                      fill="url(#volumeGradient)"
                      animationDuration={1500}
                      animationEasing="ease-in-out"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </motion.div>
            )}
          </motion.div>

          {/* Trust Trend */}
          {trustTrend && trustTrend.length > 0 && (
            <motion.div
              variants={chartVariants}
              initial="hidden"
              animate="visible"
              className="bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl p-6 mb-8 card-hover"
            >
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                📉 Trust Score Trend (30 Days)
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={trustTrend}>
                  <defs>
                    <linearGradient id="lineGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.8} />
                      <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.1} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="date" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <YAxis yAxisId="right" orientation="right" stroke="#ec4899" />
                  <Tooltip contentStyle={{backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px'}} />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="average_trust_score"
                    stroke="#3b82f6"
                    dot={{fill: '#3b82f6', r: 4}}
                    animationDuration={1500}
                    animationEasing="ease-in-out"
                  />
                  <Line
                    type="monotone"
                    dataKey="articles_analyzed"
                    stroke="#ec4899"
                    yAxisId="right"
                    animationDuration={1500}
                    animationEasing="ease-in-out"
                  />
                </LineChart>
              </ResponsiveContainer>
            </motion.div>
          )}

          {/* Top Sources */}
          {topSources && topSources.length > 0 && (
            <motion.div
              variants={chartVariants}
              initial="hidden"
              animate="visible"
              className="bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl p-6 card-hover"
            >
              <h3 className="text-lg font-semibold text-white mb-4">🔗 Top Sources</h3>
              <motion.div
                className="space-y-3"
                variants={containerVariants}
                initial="hidden"
                animate="visible"
              >
                {topSources.map((source, idx) => (
                  <motion.div
                    key={idx}
                    variants={itemVariants}
                    className="bg-gray-800/30 rounded-lg p-4 flex justify-between items-center hover:bg-gray-800/50 transition-colors"
                  >
                    <div>
                      <p className="text-white font-semibold">{source.source}</p>
                      <p className="text-gray-400 text-sm">{source.article_count} articles analyzed</p>
                    </div>
                    <motion.div
                      className="text-right"
                      whileHover={{ scale: 1.1 }}
                    >
                      <p className="text-2xl font-bold text-blue-400">{source.average_trust_score}</p>
                      <p className="text-gray-400 text-xs">avg trust</p>
                    </motion.div>
                  </motion.div>
                ))}
              </motion.div>
            </motion.div>
          )}
        </div>
      </div>
    </main>
  );
}
