import React, { useEffect, useState } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { Zap, CheckCircle2, AlertCircle, Loader, BarChart3, ArrowRight } from 'lucide-react';

export default function AnalyzePage() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const project = location.state?.project;

  const [agents, setAgents] = useState([
    { name: 'content_analyzer', label: 'Content Analyzer', status: 'pending', progress: 0, icon: '📝', color: 'blue' },
    { name: 'bias_detector', label: 'Bias Detector', status: 'pending', progress: 0, icon: '⚖️', color: 'purple' },
    { name: 'bot_detector', label: 'Bot Detector', status: 'pending', progress: 0, icon: '🤖', color: 'pink' },
    { name: 'misinformation_detector', label: 'Misinformation Detector', status: 'pending', progress: 0, icon: '🚨', color: 'red' }
  ]);

  const [analysisResult, setAnalysisResult] = useState(null);
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState(null);
  const [reflectionLoop, setReflectionLoop] = useState({
    active: false,
    iteration: 0,
    status: 'pending',
    message: ''
  });

  useEffect(() => {
    if (!id) {
      setError('No project provided');
      return;
    }

    let ws = null;
    let isComponentMounted = true;

    const connectWebSocket = () => {
      const wsUrl = `${process.env.REACT_APP_WS_URL || 'ws://localhost:8000'}/ws/analyze/${id}`;

      try {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          console.log('✅ WebSocket connected');
          // Send article content/URL to backend
          ws.send(JSON.stringify({
            title: project?.title || 'News Article',
            content: project?.fullContent || '',
            url: project?.url || ''  // Send URL if available
          }));
        };

        ws.onmessage = (event) => {
          if (!isComponentMounted) return;

          const data = JSON.parse(event.data);

          if (data.type === 'AGENT_START') {
            setAgents(prev => prev.map(agent =>
              agent.name === data.agent
                ? { ...agent, status: 'processing', progress: 10 }
                : agent
            ));
          } else if (data.type === 'AGENT_COMPLETE') {
            setAgents(prev => prev.map(agent =>
              agent.name === data.agent
                ? { ...agent, status: 'completed', progress: 100, data: data.data }
                : agent
            ));
          } else if (data.type === 'REFLECTION_LOOP_START') {
            setReflectionLoop({
              active: true,
              iteration: 0,
              status: 'processing',
              message: data.message || 'Starting synthesis with reviewer validation...',
              maxIterations: 3
            });
          } else if (data.type === 'REFLECTION_ITERATION') {
            setReflectionLoop(prev => ({
              ...prev,
              iteration: data.iteration,
              maxIterations: data.max_iterations,
              status: 'synthesizing',
              message: data.message || `Synthesis attempt ${data.iteration}/${data.max_iterations}...`
            }));
          } else if (data.type === 'REFLECTION_REVIEW') {
            setReflectionLoop(prev => ({
              ...prev,
              iteration: data.iteration,
              status: data.approved ? 'approved' : 'reviewing',
              approved: data.approved,
              qualityScore: data.quality_score,
              feedback: data.feedback,
              message: data.approved
                ? `✅ Approved on iteration ${data.iteration}!`
                : `Reviewer feedback: ${data.feedback.join(', ')}`
            }));
          } else if (data.type === 'REFLECTION_LOOP_COMPLETE') {
            setReflectionLoop({
              active: true,
              iteration: data.iteration || 1,
              status: 'approved',
              approved: true,
              message: `✅ Approved on iteration ${data.iteration || 1}`
            });
          } else if (data.type === 'ANALYSIS_FALLBACK') {
            setReflectionLoop({
              active: true,
              iteration: 3,
              status: 'fallback',
              approved: false,
              message: data.message || '⚠️ Unable to satisfy quality standards after 3 attempts'
            });
            setAnalysisResult({
              trustScore: data.fallback?.trust_score || 50,
              riskLevel: data.fallback?.risk_level || 'UNKNOWN',
              summary: data.fallback?.summary || 'Fallback analysis unable to complete full assessment.',
              reflectionLoop: data.reflection_loop,
              timestamp: data.timestamp,
              isFallback: true
            });
            setIsComplete(true);
          } else if (data.type === 'ANALYSIS_COMPLETE') {
            setAnalysisResult({
              trustScore: data.trust_score,
              riskLevel: data.risk_level,
              accuracy: data.accuracy,
              findings: data.all_findings,
              summary: data.summary,
              reflectionLoop: data.reflection_loop,
              timestamp: data.timestamp
            });
            setIsComplete(true);

            // Update project status in localStorage
            const saved = localStorage.getItem('narrativewatch_projects');
            if (saved) {
              const projects = JSON.parse(saved);
              console.log(`Found ${projects.length} projects, looking for id: ${id}`);
              const updatedProjects = projects.map(p => {
                if (p.id === id) {
                  console.log(`Updating project ${id} to completed`);
                  return {
                    ...p,
                    status: 'completed',
                    trustScore: data.trust_score,
                    riskLevel: data.risk_level,
                    summary: data.summary
                  };
                }
                return p;
              });
              localStorage.setItem('narrativewatch_projects', JSON.stringify(updatedProjects));
              console.log('Project status updated:', updatedProjects);
            } else {
              console.log('No projects found in localStorage');
            }

            // IMPORTANT: Close WebSocket when analysis is complete
            if (ws) {
              ws.close();
              console.log('✅ Analysis complete - WebSocket closed');
            }
          } else if (data.type === 'AGENT_ERROR') {
            setAgents(prev => prev.map(agent =>
              agent.name === data.agent
                ? { ...agent, status: 'error', progress: 0 }
                : agent
            ));
          }
        };

        ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          setError('WebSocket error');
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected');
        };

      } catch (err) {
        console.error('Failed to connect:', err);
        setError('Failed to connect to analysis server');
      }
    };

    connectWebSocket();

    // Cleanup on unmount
    return () => {
      isComponentMounted = false;
      if (ws) {
        ws.close();
      }
    };
  }, [id]);

  const getTrustScoreColor = (score) => {
    if (score >= 75) return { bg: 'from-green-500 to-green-600', text: 'text-green-300', label: 'HIGH TRUST' };
    if (score >= 50) return { bg: 'from-yellow-500 to-yellow-600', text: 'text-yellow-300', label: 'MEDIUM RISK' };
    return { bg: 'from-red-500 to-red-600', text: 'text-red-300', label: 'HIGH RISK' };
  };

  const getRiskBadge = (level) => {
    const badges = {
      'LOW': { color: 'bg-green-500/20 text-green-300 border-green-500/30', icon: '✓' },
      'MEDIUM': { color: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30', icon: '⚠' },
      'HIGH': { color: 'bg-red-500/20 text-red-300 border-red-500/30', icon: '!' }
    };
    return badges[level] || badges['MEDIUM'];
  };

  const allComplete = agents.every(a => a.status === 'completed');
  const anyError = agents.some(a => a.status === 'error');

  if (error && !isComplete) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black flex items-center justify-center p-6">
        <div className="bg-red-500/20 border border-red-500/50 rounded-xl p-8 max-w-md text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-red-300 mb-2">Error</h3>
          <p className="text-red-200">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black overflow-hidden">
      {/* Background animations */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
      </div>

      {/* Top Navigation */}
      <nav className="relative z-10 border-b border-gray-800/30 bg-gray-900/20 backdrop-blur-md sticky top-0">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-white">{project?.title || id || 'Analysis'}</h1>
            <p className="text-gray-400 text-sm mt-1">{isComplete ? 'Analysis Complete' : 'Analyzing in progress...'}</p>
          </div>
          <div className="text-right">
            <p className="text-gray-400 text-sm">Status: <span className={`font-semibold ${isComplete ? 'text-green-400' : 'text-blue-400'}`}>{isComplete ? 'Complete' : 'Processing'}</span></p>
          </div>
        </div>
      </nav>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-12">
        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Agents Column */}
          <div className="lg:col-span-2">
            <h2 className="text-2xl font-bold text-white mb-8">AI Agents Processing</h2>

            <div className="space-y-6">
              {agents.map((agent, idx) => (
                <div
                  key={agent.name}
                  className="group bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl overflow-hidden hover:border-blue-500/30 transition-all duration-300"
                >
                  {/* Header */}
                  <div className="bg-gradient-to-r from-gray-800/50 to-gray-900/50 p-4 border-b border-gray-800/30">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <span className="text-3xl">{agent.icon}</span>
                        <div>
                          <h3 className="text-lg font-semibold text-white">{agent.label}</h3>
                          <p className="text-gray-400 text-sm">ML Model Processing</p>
                        </div>
                      </div>

                      {/* Status Indicator */}
                      <div className="flex items-center gap-3">
                        {agent.status === 'pending' && (
                          <div className="flex items-center gap-2 text-gray-400">
                            <div className="w-2 h-2 rounded-full bg-gray-500"></div>
                            <span className="text-sm">Pending</span>
                          </div>
                        )}
                        {agent.status === 'processing' && (
                          <div className="flex items-center gap-2 text-blue-400">
                            <Loader className="w-4 h-4 animate-spin" />
                            <span className="text-sm">Processing</span>
                          </div>
                        )}
                        {agent.status === 'completed' && (
                          <div className="flex items-center gap-2 text-green-400">
                            <CheckCircle2 className="w-4 h-4" />
                            <span className="text-sm">Complete</span>
                          </div>
                        )}
                        {agent.status === 'error' && (
                          <div className="flex items-center gap-2 text-red-400">
                            <AlertCircle className="w-4 h-4" />
                            <span className="text-sm">Error</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="px-4 py-3 bg-gray-900/20">
                    <div className="h-2 bg-gray-700/50 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-500 ease-out rounded-full bg-gradient-to-r ${
                          agent.status === 'completed' ? 'from-green-400 to-green-500' :
                          agent.status === 'processing' ? 'from-blue-400 to-blue-500' :
                          agent.status === 'error' ? 'from-red-400 to-red-500' :
                          'from-gray-500 to-gray-600'
                        }`}
                        style={{width: `${agent.progress}%`}}
                      ></div>
                    </div>
                  </div>

                  {/* Details */}
                  {agent.data && (
                    <div className="px-4 py-4 bg-gray-800/20 border-t border-gray-800/30 max-h-40 overflow-y-auto">
                      <div className="text-gray-300 text-sm space-y-2">
                        {agent.name === 'content_analyzer' && agent.data.findings && (
                          <>
                            <p><span className="text-blue-400">Sentiment:</span> {agent.data.findings.analysis?.sentiment?.label?.toUpperCase() || 'N/A'}</p>
                            <p><span className="text-blue-400">Toxicity Score:</span> {Math.round(agent.data.findings.analysis?.toxicity?.toxicity_score || 0)}/100</p>
                            <p><span className="text-blue-400">Misinformation:</span> {Math.round(agent.data.findings.analysis?.misinformation?.misinformation_likelihood || 0)}%</p>
                            <p><span className="text-blue-400">Entities Found:</span> {agent.data.findings.analysis?.entity_count || 0} total (scored)</p>
                            {agent.data.findings.analysis?.entities?.entities?.length > 0 && (
                              <div className="mt-2 pt-2 border-t border-gray-700/50">
                                <p className="text-xs text-gray-400 mb-1">Top Entities:</p>
                                {agent.data.findings.analysis.entities.entities.slice(0, 3).map((ent, idx) => (
                                  <p key={idx} className="text-xs text-gray-300">
                                    • {ent.name} <span className="text-gray-500">({ent.type}, {ent.importance_score}%)</span>
                                  </p>
                                ))}
                              </div>
                            )}
                          </>
                        )}
                        {agent.name === 'bias_detector' && agent.data.findings && (
                          <>
                            <p><span className="text-purple-400">Bias Level:</span> {agent.data.findings.bias_analysis?.overall_bias_level?.toUpperCase() || 'LOW'}</p>
                            <p><span className="text-purple-400">Bias Score:</span> {(agent.data.findings.bias_analysis?.overall_bias_score || 0).toFixed(1)}/100</p>
                            <p><span className="text-purple-400">Political Bias:</span> {(agent.data.findings.bias_analysis?.pattern_based_biases?.political_bias || 0).toFixed(1)}/100</p>
                            <p><span className="text-purple-400">Gender Bias:</span> {(agent.data.findings.bias_analysis?.pattern_based_biases?.gender_bias || 0).toFixed(1)}/100</p>
                          </>
                        )}
                        {agent.name === 'bot_detector' && agent.data.findings && (
                          <>
                            <p><span className="text-pink-400">Bot Probability:</span> {Math.round(agent.data.findings.bot_analysis?.bot_probability || 0)}%</p>
                            <p><span className="text-pink-400">Toxicity Score:</span> {Math.round(agent.data.findings.bot_analysis?.toxicity?.toxicity_score || 0)}/100</p>
                            <p><span className="text-pink-400">Authenticity Score:</span> {Math.round(agent.data.findings.bot_analysis?.authenticity_score || 0)}%</p>
                          </>
                        )}
                        {agent.name === 'misinformation_detector' && agent.data.findings && (
                          <>
                            <p><span className="text-red-400">Misinformation Risk:</span> {Math.round(agent.data.findings.misinformation_analysis?.final_misinformation_score || 0)}/100</p>
                            <p><span className="text-red-400">Risk Level:</span> {agent.data.findings.misinformation_analysis?.risk_level || 'UNKNOWN'}</p>
                            <p><span className="text-red-400">Emotional Manipulation:</span> {Math.round(agent.data.findings.misinformation_analysis?.emotional_manipulation?.manipulation_score || 0)}/100</p>
                          </>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Processing Summary */}
            <div className="mt-8 p-6 bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl">
              <div className="flex items-center gap-3 mb-4">
                <BarChart3 className="w-5 h-5 text-blue-400" />
                <h3 className="text-lg font-semibold text-white">Processing Summary</h3>
                {!isComplete && <span className="ml-auto text-xs text-blue-400 animate-pulse">● Processing</span>}
              </div>

              {/* Progress Bar */}
              <div className="mb-6">
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-gray-400">Overall Progress</span>
                  <span className="text-sm font-semibold text-blue-400">{Math.round((agents.filter(a => a.status === 'completed').length / agents.length) * 100)}%</span>
                </div>
                <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-400 to-blue-600 transition-all duration-500"
                    style={{width: `${(agents.filter(a => a.status === 'completed').length / agents.length) * 100}%`}}
                  ></div>
                </div>
              </div>

              <div className="grid grid-cols-4 gap-4 text-center">
                <div className="bg-green-500/10 rounded-lg p-4 border border-green-500/20">
                  <div className="text-3xl font-bold text-green-400">{agents.filter(a => a.status === 'completed').length}</div>
                  <p className="text-gray-400 text-sm mt-1">Completed</p>
                </div>
                <div className="bg-blue-500/10 rounded-lg p-4 border border-blue-500/20">
                  <div className="text-3xl font-bold text-blue-400">{agents.filter(a => a.status === 'processing').length}</div>
                  <p className="text-gray-400 text-sm mt-1">Processing</p>
                </div>
                <div className="bg-yellow-500/10 rounded-lg p-4 border border-yellow-500/20">
                  <div className="text-3xl font-bold text-yellow-400">{agents.filter(a => a.status === 'pending').length}</div>
                  <p className="text-gray-400 text-sm mt-1">Pending</p>
                </div>
                <div className="bg-purple-500/10 rounded-lg p-4 border border-purple-500/20">
                  <div className="text-3xl font-bold text-purple-400">{isComplete ? '✓' : '~' + agents.length + 's'}</div>
                  <p className="text-gray-400 text-sm mt-1">{isComplete ? 'Complete' : 'Est. Time'}</p>
                </div>
              </div>
            </div>

            {/* Reflection Loop Status */}
            {reflectionLoop.active && (
              <div className={`mt-8 p-6 backdrop-blur border rounded-xl transition-all duration-500 ${
                reflectionLoop.status === 'approved' ? 'bg-green-500/10 border-green-500/30' :
                reflectionLoop.status === 'fallback' ? 'bg-red-500/10 border-red-500/30' :
                'bg-blue-500/10 border-blue-500/30'
              }`}>
                <div className="flex items-center gap-3 mb-3">
                  {reflectionLoop.status === 'approved' && (
                    <>
                      <CheckCircle2 className="w-5 h-5 text-green-400" />
                      <h3 className="text-lg font-semibold text-green-300">Synthesis Approved</h3>
                    </>
                  )}
                  {reflectionLoop.status === 'fallback' && (
                    <>
                      <AlertCircle className="w-5 h-5 text-red-400" />
                      <h3 className="text-lg font-semibold text-red-300">Fallback Applied</h3>
                    </>
                  )}
                  {reflectionLoop.status === 'processing' && (
                    <>
                      <Loader className="w-5 h-5 text-blue-400 animate-spin" />
                      <h3 className="text-lg font-semibold text-blue-300">Reflection Loop Active</h3>
                    </>
                  )}
                </div>
                <p className="text-gray-300 text-sm">{reflectionLoop.message}</p>
                {reflectionLoop.status !== 'processing' && (
                  <p className="text-gray-400 text-xs mt-2">
                    {reflectionLoop.status === 'approved' ? `✓ Quality standards met on iteration ${reflectionLoop.iteration}` :
                     reflectionLoop.status === 'fallback' ? '✗ Unable to satisfy quality standards after 3 attempts' :
                     'Processing...'}
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Results Column */}
          <div>
            {isComplete && analysisResult && (
              <div className="sticky top-24 space-y-6">
                {/* Trust Score Card */}
                <div className={`bg-gradient-to-br ${getTrustScoreColor(analysisResult.trustScore).bg} rounded-xl p-8 text-center`}>
                  <p className="text-white/80 text-sm mb-2">Trust Score</p>
                  <div className="text-6xl font-bold text-white mb-2">{analysisResult.trustScore}</div>
                  <p className="text-white/90 font-semibold">{getTrustScoreColor(analysisResult.trustScore).label}</p>

                  {/* Score Ring */}
                  <div className="mt-6 relative w-24 h-24 mx-auto">
                    <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                      <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth="3" />
                      <circle
                        cx="50"
                        cy="50"
                        r="40"
                        fill="none"
                        stroke="white"
                        strokeWidth="3"
                        strokeDasharray={`${analysisResult.trustScore * 2.51} 251`}
                        strokeLinecap="round"
                      />
                    </svg>
                  </div>
                </div>

                {/* Risk Level Card */}
                <div className="bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl p-6">
                  <h3 className="text-white font-semibold mb-4">Risk Assessment</h3>
                  <div className={`px-4 py-3 rounded-lg text-center border ${getRiskBadge(analysisResult.riskLevel || 'MEDIUM').color}`}>
                    <span className="text-lg font-bold">{analysisResult.riskLevel || 'UNKNOWN'}</span>
                  </div>

                  {/* Detailed Breakdown */}
                  <div className="mt-4 space-y-3 text-sm text-gray-300">
                    <div className="bg-gray-800/30 p-3 rounded-lg">
                      <p className="text-gray-400">Trust Score: <span className="text-white font-semibold">{analysisResult.trustScore || 50}/100</span></p>
                    </div>
                    {analysisResult.findings && (
                      <>
                        <div className="bg-gray-800/30 p-3 rounded-lg">
                          <p className="text-gray-400">Sentiment: <span className="text-white font-semibold">{analysisResult.findings.content_analyzer?.findings?.analysis?.sentiment?.label?.toUpperCase() || 'N/A'}</span></p>
                        </div>
                        <div className="bg-gray-800/30 p-3 rounded-lg">
                          <p className="text-gray-400">Bias Score: <span className="text-white font-semibold">{(analysisResult.findings.bias_detector?.findings?.bias_analysis?.overall_bias_score || 0).toFixed(1)}/10</span></p>
                        </div>
                        <div className="bg-gray-800/30 p-3 rounded-lg">
                          <p className="text-gray-400">Bot Probability: <span className="text-white font-semibold">{Math.round(analysisResult.findings.bot_detector?.findings?.bot_analysis?.bot_probability || 0)}%</span></p>
                        </div>
                        <div className="bg-gray-800/30 p-3 rounded-lg">
                          <p className="text-gray-400">Misinformation: <span className="text-white font-semibold">{Math.round(analysisResult.findings.misinformation_detector?.findings?.misinformation_analysis?.final_misinformation_score || 0)}/100</span></p>
                        </div>
                      </>
                    )}
                  </div>
                </div>


                {/* View Report Button */}
                <button
                  onClick={() => navigate(`/results/${id}`, { state: { project, analysisResult } })}
                  className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-gradient-to-r from-green-500 to-emerald-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-green-500/50 transition-all duration-300 group"
                >
                  View Full Report
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
              </div>
            )}

            {!isComplete && (
              <div className="sticky top-24 bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl p-8 text-center">
                <div className="mb-6">
                  <Loader className="w-16 h-16 text-blue-400 mx-auto animate-spin" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">Analysis in Progress</h3>
                <p className="text-gray-400 mb-4">Our AI agents are processing your article</p>
                <p className="text-sm text-gray-500">This typically takes 1-2 seconds...</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fade-in {
          animation: fadeIn 0.5s ease-out forwards;
          opacity: 0;
        }
      `}</style>
    </div>
  );
}
