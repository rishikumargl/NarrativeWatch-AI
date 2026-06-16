import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Play, Trash2, Calendar, TrendingUp, Search, Filter, Clock, ArrowLeft, BarChart3, Upload } from 'lucide-react';

export default function ProjectsPage() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [showNewProject, setShowNewProject] = useState(false);
  const [formData, setFormData] = useState({ url: '', text: '', title: '', articleType: 'url' });
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [deleteConfirm, setDeleteConfirm] = useState({ show: false, id: null, title: '' });

  useEffect(() => {
    const loadProjects = async () => {
      const saved = localStorage.getItem('narrativewatch_projects');
      const localProjects = saved ? JSON.parse(saved) : [];

      try {
        const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

        // Try to fetch projects from /api/projects first
        const response = await fetch(`${apiUrl}/api/projects`);
        if (response.ok) {
          const dbProjects = await response.json();
          const converted = dbProjects.map(p => ({
            id: p.id.toString(),
            title: p.name || 'Untitled Project',
            content: p.description || 'No description',
            fullContent: p.description || '',
            url: '',
            status: 'completed',
            createdAt: p.created_at,
            trustScore: null,
            validationScore: null,
            combinedTrustScore: null,
            riskLevel: null,
            summary: p.description
          }));

          // Merge with local projects, prioritizing DB records
          const merged = [...converted];
          localProjects.forEach(local => {
            if (!merged.find(m => m.id === local.id)) {
              merged.push(local);
            }
          });

          setProjects(merged.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt)));
          return;
        }
      } catch (error) {
        console.error('Failed to fetch projects from API:', error);
      }

      // Fallback to localStorage only
      if (localProjects.length > 0) {
        setProjects(localProjects.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt)));
      }
    };

    loadProjects();
  }, []);

  useEffect(() => {
    localStorage.setItem('narrativewatch_projects', JSON.stringify(projects));
  }, [projects]);

  const handleCreateProject = async () => {
    const content = formData.articleType === 'url' ? formData.url : formData.text;

    if (!content.trim()) {
      alert('Please enter article URL or content');
      return;
    }

    if (!formData.title.trim()) {
      alert('Please enter a project title');
      return;
    }

    const newProject = {
      id: Date.now().toString(),
      title: formData.title,
      content: content.substring(0, 150) + (content.length > 150 ? '...' : ''),
      fullContent: content,
      url: formData.articleType === 'url' ? formData.url : '',
      status: 'analyzing',
      createdAt: new Date().toISOString(),
      trustScore: null,
      riskLevel: null,
      summary: null,
      agents: []
    };

    setProjects([newProject, ...projects]);
    setFormData({ url: '', text: '', title: '', articleType: 'url' });
    setShowNewProject(false);

    navigate(`/analysis/${newProject.id}`, { state: { project: newProject } });
  };

  const handleDeleteClick = (id, title) => {
    setDeleteConfirm({ show: true, id, title });
  };

  const handleConfirmDelete = async () => {
    const { id } = deleteConfirm;

    const updatedProjects = projects.filter(project => project.id !== id);
    setProjects(updatedProjects);

    const localStorageProjects = updatedProjects.filter(p => p.status !== 'completed');
    localStorage.setItem('narrativewatch_projects', JSON.stringify(localStorageProjects));

    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/analysis/${id}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();
      if (response.ok && data.success) {
        console.log('Project deleted from database');
      }
    } catch (error) {
      console.warn('Database delete failed:', error.message);
    }

    setDeleteConfirm({ show: false, id: null, title: '' });
  };

  const handleCancelDelete = () => {
    setDeleteConfirm({ show: false, id: null, title: '' });
  };

  const filteredProjects = projects.filter(p => {
    const title = p.title || '';
    const matchesSearch = title.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || p.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const getStatusColor = (status) => {
    switch(status) {
      case 'completed': return 'bg-green-500/20 text-green-300 border-green-500/30';
      case 'analyzing': return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      case 'failed': return 'bg-red-500/20 text-red-300 border-red-500/30';
      default: return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
    }
  };

  const getRiskColor = (score) => {
    if (!score) return 'text-gray-400';
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
      </div>

      <nav className="z-10 border-b border-gray-800/30 bg-gray-900/20 backdrop-blur-md sticky top-0">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/')}
              className="p-2 hover:bg-gray-800/50 rounded-lg transition-colors"
              title="Go back to home"
            >
              <ArrowLeft className="w-5 h-5 text-gray-400 hover:text-white transition-colors" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-white">Projects</h1>
              <p className="text-gray-400 text-sm">Manage your analysis projects</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/documents')}
              className="flex items-center gap-2 px-6 py-3 bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700 rounded-lg text-gray-300 font-semibold transition-all duration-300 hover:border-purple-500/50 group"
            >
              <Upload className="w-5 h-5 group-hover:scale-110 transition-transform" />
              Upload Docs
            </button>
            <button
              onClick={() => navigate('/analytics')}
              className="flex items-center gap-2 px-6 py-3 bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700 rounded-lg text-gray-300 font-semibold transition-all duration-300 hover:border-green-500/50 group"
            >
              <BarChart3 className="w-5 h-5 group-hover:scale-110 transition-transform" />
              Analytics
            </button>
            <button
              onClick={() => setShowNewProject(!showNewProject)}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all duration-300 group"
            >
              <Plus className="w-5 h-5 group-hover:scale-110 transition-transform" />
              New Project
            </button>
          </div>
        </div>
      </nav>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-12">
        {showNewProject && (
          <div className="mb-12 animate-fade-in">
            <div className="bg-gray-900/50 backdrop-blur border border-blue-500/30 rounded-xl p-8">
              <h2 className="text-2xl font-bold text-white mb-6">Create New Project</h2>

              <div className="space-y-6">
                <div>
                  <label className="block text-white font-semibold mb-2">Project Title</label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({...formData, title: e.target.value})}
                    placeholder="e.g., ABP News Article Analysis"
                    className="w-full bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 focus:border-blue-500 focus:outline-none transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-white font-semibold mb-3">Source Type</label>
                  <div className="flex gap-4">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="type"
                        value="url"
                        checked={formData.articleType === 'url'}
                        onChange={(e) => setFormData({...formData, articleType: e.target.value})}
                        className="w-4 h-4"
                      />
                      <span className="text-gray-300">Article URL</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="type"
                        value="text"
                        checked={formData.articleType === 'text'}
                        onChange={(e) => setFormData({...formData, articleType: e.target.value})}
                        className="w-4 h-4"
                      />
                      <span className="text-gray-300">Paste Content</span>
                    </label>
                  </div>
                </div>

                {formData.articleType === 'url' ? (
                  <div>
                    <label className="block text-white font-semibold mb-2">Article URL</label>
                    <input
                      type="url"
                      value={formData.url}
                      onChange={(e) => setFormData({...formData, url: e.target.value})}
                      placeholder="https://example.com/article"
                      className="w-full bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 focus:border-blue-500 focus:outline-none transition-colors"
                    />
                  </div>
                ) : (
                  <div>
                    <label className="block text-white font-semibold mb-2">Article Content</label>
                    <textarea
                      value={formData.text}
                      onChange={(e) => setFormData({...formData, text: e.target.value})}
                      placeholder="Paste your article text here..."
                      className="w-full h-40 bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 focus:border-blue-500 focus:outline-none transition-colors resize-none"
                    />
                  </div>
                )}

                <div className="flex gap-4 pt-4">
                  <button
                    onClick={handleCreateProject}
                    disabled={loading}
                    className="flex-1 bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold py-3 rounded-lg hover:shadow-lg hover:shadow-blue-500/50 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? 'Creating...' : 'Create & Analyze'}
                  </button>
                  <button
                    onClick={() => setShowNewProject(false)}
                    className="flex-1 bg-gray-800 text-white font-semibold py-3 rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="mb-8 flex gap-4 flex-col md:flex-row">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search projects..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-gray-800/50 border border-gray-700/50 text-white rounded-lg pl-12 pr-4 py-3 focus:border-blue-500 focus:outline-none transition-colors"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setFilterStatus('all')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${filterStatus === 'all' ? 'bg-blue-500 text-white' : 'bg-gray-800/50 text-gray-300 hover:bg-gray-700/50'}`}
            >
              All
            </button>
            <button
              onClick={() => setFilterStatus('completed')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${filterStatus === 'completed' ? 'bg-green-500 text-white' : 'bg-gray-800/50 text-gray-300 hover:bg-gray-700/50'}`}
            >
              Completed
            </button>
          </div>
        </div>

        {filteredProjects.length === 0 ? (
          <div className="text-center py-16">
            <TrendingUp className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-300 mb-2">No projects yet</h3>
            <p className="text-gray-400 mb-6">Create your first project to start analyzing articles</p>
            <button
              onClick={() => setShowNewProject(true)}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all"
            >
              <Plus className="w-5 h-5" />
              Create Project
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProjects.map((project) => (
              <div
                key={project.id}
                className="group bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl overflow-hidden hover:border-blue-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/10 animate-fade-in"
              >
                <div className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 p-6 border-b border-gray-800/30">
                  <div className="flex justify-between items-start gap-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-white group-hover:text-blue-300 transition-colors truncate">
                        {project.title}
                      </h3>
                      <p className="text-gray-400 text-sm mt-1 line-clamp-2">{project.content}</p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(project.status)} whitespace-nowrap`}>
                      {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                    </span>
                  </div>
                </div>

                <div className="p-6 space-y-4">
                  {project.summary && (
                    <div className="mb-4">
                      <p className="text-gray-300 text-sm leading-relaxed line-clamp-3">
                        {project.summary}
                      </p>
                    </div>
                  )}

                  {project.trustScore !== null && (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400 text-sm">Model Trust</span>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 h-1.5 bg-gray-700 rounded-full w-12 overflow-hidden">
                            <div
                              className={`h-full transition-all ${project.trustScore >= 70 ? 'bg-blue-500' : project.trustScore >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`}
                              style={{width: `${project.trustScore}%`}}
                            ></div>
                          </div>
                          <span className={`font-bold text-xs ${getRiskColor(project.trustScore)}`}>
                            {project.trustScore}/100
                          </span>
                        </div>
                      </div>

                      {project.validationScore !== null && project.validationScore !== undefined && (
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400 text-sm">Validation</span>
                          <div className="flex items-center gap-2">
                            <div className="flex-1 h-1.5 bg-gray-700 rounded-full w-12 overflow-hidden">
                              <div
                                className={`h-full transition-all ${project.validationScore >= 70 ? 'bg-cyan-500' : project.validationScore >= 50 ? 'bg-blue-500' : 'bg-gray-500'}`}
                                style={{width: `${Math.min(project.validationScore, 100)}%`}}
                              ></div>
                            </div>
                            <span className="font-bold text-xs text-cyan-400">
                              {Math.round(project.validationScore)}/100
                            </span>
                          </div>
                        </div>
                      )}

                      {project.combinedTrustScore !== null && project.combinedTrustScore !== undefined && (
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400 text-sm">Combined</span>
                          <div className="flex items-center gap-2">
                            <div className="flex-1 h-1.5 bg-gray-700 rounded-full w-12 overflow-hidden">
                              <div
                                className={`h-full transition-all ${project.combinedTrustScore >= 70 ? 'bg-indigo-500' : project.combinedTrustScore >= 50 ? 'bg-purple-500' : 'bg-pink-500'}`}
                                style={{width: `${Math.min(project.combinedTrustScore, 100)}%`}}
                              ></div>
                            </div>
                            <span className="font-bold text-xs text-indigo-400">
                              {Math.round(project.combinedTrustScore)}/100
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {project.riskLevel && (
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400 text-sm">Risk Level</span>
                      <span className={`px-3 py-1 rounded text-xs font-semibold ${
                        project.riskLevel === 'LOW' ? 'bg-green-500/20 text-green-300' :
                        project.riskLevel === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-300' :
                        'bg-red-500/20 text-red-300'
                      }`}>
                        {project.riskLevel}
                      </span>
                    </div>
                  )}

                  <div className="flex items-center gap-2 text-gray-400 text-sm">
                    <Clock className="w-4 h-4" />
                    <span>{new Date(project.createdAt).toLocaleDateString()}</span>
                  </div>
                </div>

                <div className="border-t border-gray-800/30 px-6 py-4 flex gap-3">
                  <button
                    onClick={() => navigate(`/analysis/${project.id}`, { state: { project } })}
                    className="flex-1 flex items-center justify-center gap-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 font-semibold py-2 rounded-lg transition-colors group/btn"
                  >
                    <Play className="w-4 h-4 group-hover/btn:translate-x-0.5 transition-transform" />
                    {project.status === 'analyzing' ? 'View' : 'Analyze'}
                  </button>
                  <button
                    onClick={() => handleDeleteClick(project.id, project.title)}
                    className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-300 font-semibold rounded-lg transition-colors group/btn"
                  >
                    <Trash2 className="w-4 h-4 group-hover/btn:scale-110 transition-transform" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {deleteConfirm.show && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in">
          <div className="bg-gray-900 border border-red-500/30 rounded-xl p-8 max-w-md w-full mx-4 shadow-2xl shadow-red-500/20 animate-fade-in">
            <div className="mb-6">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-red-500/20 rounded-lg mb-4">
                <Trash2 className="w-6 h-6 text-red-400" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">Delete Project?</h3>
              <p className="text-gray-400">
                Are you sure you want to delete <span className="text-red-300 font-semibold">{deleteConfirm.title}</span>? This action cannot be undone.
              </p>
            </div>

            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-6">
              <p className="text-sm text-red-300">
                This will permanently delete the project and all its analysis data.
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleCancelDelete}
                className="flex-1 px-4 py-3 bg-gray-800 hover:bg-gray-700 text-gray-300 font-semibold rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmDelete}
                className="flex-1 px-4 py-3 bg-red-500 hover:bg-red-600 text-white font-semibold rounded-lg transition-colors shadow-lg shadow-red-500/30"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

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
