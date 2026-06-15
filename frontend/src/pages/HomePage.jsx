import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight, Zap, Shield, BarChart3, Sparkles, ArrowRight, LogIn } from 'lucide-react';

export default function HomePage() {
  const navigate = useNavigate();
  const [isHovering, setIsHovering] = useState(false);

  const features = [
    {
      icon: Zap,
      title: 'Lightning Fast',
      desc: '90.25% accuracy with real-time analysis'
    },
    {
      icon: Shield,
      title: 'Advanced Detection',
      desc: 'Misinformation, bias, bots & campaigns'
    },
    {
      icon: BarChart3,
      title: 'Deep Insights',
      desc: 'Trust scores, evidence & detailed findings'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black overflow-hidden">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl"></div>
      </div>

      {/* Navigation */}
      <nav className="relative z-10 px-6 py-6 flex justify-between items-center border-b border-gray-800/30 backdrop-blur-md animate-slide-down">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg hover:scale-110 transition-transform duration-300">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              NarrativeWatch
            </h1>
            <p className="text-sm text-gray-500">AI-Powered News Intelligence</p>
          </div>
        </div>
        <button
          onClick={() => alert('Sign-in feature coming soon!')}
          className="flex items-center gap-2 px-6 py-3 bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700 rounded-lg text-gray-300 font-semibold transition-all duration-300 hover:border-blue-500/50 hover:shadow-lg hover:shadow-blue-500/20 group"
        >
          <LogIn className="w-5 h-5 group-hover:scale-110 transition-transform" />
          Sign In
        </button>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 px-6 py-24 max-w-7xl mx-auto">
        {/* Main Content */}
        <div className="text-center mb-24">
          {/* Title with animation */}
          <div className="mb-8 animate-fade-in">
            <h2 className="text-8xl md:text-9xl font-black mb-6 leading-tight">
              <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-purple-400 bg-clip-text text-transparent block mb-4 hover:from-pink-400 hover:via-purple-400 hover:to-blue-400 transition-all duration-500">
                Detect Truth.
              </span>
              <span className="text-white block text-7xl md:text-8xl">
                Expose Lies.
              </span>
            </h2>
          </div>

          {/* Tagline */}
          <p className="text-xl md:text-3xl text-gray-300 mb-12 max-w-4xl mx-auto leading-relaxed animate-fade-in font-light" style={{animationDelay: '0.2s'}}>
            Real-time AI-powered analysis of news articles. Detect misinformation, bias, bot activity, and coordinated campaigns powered by 7 advanced machine learning models with 90.25% accuracy.
          </p>

          {/* CTA Button with hover animation */}
          <div className="animate-fade-in flex justify-center" style={{animationDelay: '0.4s'}}>
            <button
              onClick={() => navigate('/projects')}
              onMouseEnter={() => setIsHovering(true)}
              onMouseLeave={() => setIsHovering(false)}
              className="group relative inline-flex items-center gap-3 px-12 py-6 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl font-bold text-white text-xl hover:shadow-2xl hover:shadow-blue-500/50 transition-all duration-300 overflow-hidden hover:scale-105 hover:-translate-y-1"
            >
              {/* Animated background */}
              <div className={`absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 transition-opacity duration-300 ${isHovering ? 'opacity-100' : 'opacity-0'}`}></div>

              {/* Content */}
              <span className="relative flex items-center gap-2">
                Start Analyzing
                <ArrowRight className={`w-6 h-6 transition-transform duration-300 ${isHovering ? 'translate-x-2' : ''}`} />
              </span>
            </button>
          </div>

          {/* Scroll indicator */}
          <div className="mt-16 animate-bounce">
            <div className="text-gray-600 text-sm">Scroll to explore</div>
            <ChevronRight className="w-5 h-5 mx-auto text-gray-600 rotate-90" />
          </div>
        </div>


        {/* Features Section */}
        <div className="mb-24">
          <h3 className="text-5xl md:text-6xl font-black text-white mb-12 text-center animate-fade-in" style={{animationDelay: '0.8s'}}>
            Powered by <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Advanced AI</span>
          </h3>
          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <div
                  key={idx}
                  className="group relative bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl p-8 hover:border-blue-500/50 transition-all duration-300 hover:bg-gray-800/50 animate-fade-in"
                  style={{animationDelay: `${0.8 + idx * 0.1}s`}}
                >
                  {/* Hover gradient background */}
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 rounded-xl transition-opacity duration-300"></div>

                  {/* Content */}
                  <div className="relative z-10">
                    <div className="mb-4 inline-block p-3 bg-gray-800/50 rounded-lg group-hover:bg-blue-500/20 transition-colors">
                      <Icon className="w-6 h-6 text-blue-400 group-hover:text-purple-400 transition-colors" />
                    </div>
                    <h3 className="text-xl font-semibold text-white mb-3">{feature.title}</h3>
                    <p className="text-gray-400 leading-relaxed">{feature.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Capabilities */}
        <div className="mb-24 animate-fade-in" style={{animationDelay: '1.0s'}}>
          <h3 className="text-3xl font-bold text-white mb-12 text-center">What We Detect</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { icon: '🚨', label: 'Misinformation' },
              { icon: '⚖️', label: 'Bias & Prejudice' },
              { icon: '🤖', label: 'Bot Activity' },
              { icon: '🎭', label: 'Propaganda' },
              { icon: '📊', label: 'Fact-Checks' },
              { icon: '🔗', label: 'Coordination' },
              { icon: '💬', label: 'Sentiment' },
              { icon: '⚡', label: 'Toxicity' }
            ].map((item, idx) => (
              <div
                key={idx}
                className="bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-lg p-6 text-center hover:border-blue-500/50 hover:bg-gray-800/50 transition-all duration-300 group"
              >
                <div className="text-4xl mb-3 group-hover:scale-110 transition-transform">{item.icon}</div>
                <p className="text-gray-300 font-medium text-sm">{item.label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom CTA Section */}
        <div className="mt-32 text-center animate-fade-in" style={{animationDelay: '1.2s'}}>
          <h3 className="text-2xl font-bold text-white mb-4">Ready to analyze your first article?</h3>
          <p className="text-gray-400 mb-8">Create a project and start detecting misinformation in seconds</p>
          <div className="flex justify-center gap-4 flex-wrap">
            <button
              onClick={() => navigate('/projects')}
              className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all duration-300 group"
            >
              Launch Dashboard
              <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
            <button
              onClick={() => navigate('/analytics')}
              className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-green-500/50 transition-all duration-300 group"
            >
              📊 View Analytics
              <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-gray-800/30 bg-gray-900/20 backdrop-blur-md mt-32 px-6 py-8 animate-slide-up">
        <div className="max-w-7xl mx-auto text-center text-gray-400 text-base">
          <p>NarrativeWatch AI | Powered by 7 HuggingFace ML Models & HF Inference API | <span className="text-blue-400">Open Source</span></p>
        </div>
      </footer>

      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes bounce {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-15px);
          }
        }

        @keyframes glow {
          0%, 100% {
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
          }
          50% {
            box-shadow: 0 0 40px rgba(168, 85, 247, 0.6);
          }
        }

        .animate-fade-in {
          animation: fadeIn 0.8s ease-out forwards;
          opacity: 0;
        }

        .animate-slide-down {
          animation: slideDown 0.6s ease-out;
        }

        .animate-slide-up {
          animation: slideUp 0.6s ease-out;
        }

        .animate-bounce {
          animation: bounce 2s infinite;
        }

        .animate-glow {
          animation: glow 3s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
