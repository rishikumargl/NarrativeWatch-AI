import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Brain, Database, Code, Shield, Sparkles, Rocket, Zap } from 'lucide-react'

export default function Home() {
  const [hoveredFeature, setHoveredFeature] = useState(null)

  const features = [
    {
      icon: Brain,
      title: '11 AI Agents',
      desc: 'Intelligent orchestration for comprehensive analysis',
      color: 'from-cyan-400 to-cyan-600'
    },
    {
      icon: Database,
      title: 'Vector Database',
      desc: 'pgvector for semantic search and RAG',
      color: 'from-purple-400 to-purple-600'
    },
    {
      icon: Code,
      title: 'REST API',
      desc: 'Production-ready FastAPI endpoints',
      color: 'from-blue-400 to-blue-600'
    },
    {
      icon: Shield,
      title: 'Quality Assurance',
      desc: 'Reflection loop with quality review',
      color: 'from-cyan-400 via-blue-400 to-purple-400'
    },
    {
      icon: Zap,
      title: 'Fast Analysis',
      desc: '~8 seconds per article with 11 agents',
      color: 'from-yellow-400 to-orange-400'
    },
    {
      icon: Rocket,
      title: 'Scalable',
      desc: '10,800+ articles per day capacity',
      color: 'from-red-400 to-pink-400'
    },
  ]

  return (
    <main className="overflow-hidden bg-dark-900">
      {/* Hero Section */}
      <section className="relative pt-12 md:pt-20 pb-24 md:pb-32 space-y-10 text-center min-h-screen flex flex-col justify-center px-4 md:px-0">
        {/* Animated Background Blobs */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -left-40 w-96 h-96 bg-cyan-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
          <div className="absolute top-1/2 -right-40 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
          <div className="absolute -bottom-40 left-1/3 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>
        </div>

        <div className="relative z-10 space-y-8 max-w-5xl mx-auto">
          {/* Badge */}
          <div className="inline-block animate-fade-in-down">
            <div className="px-5 py-2.5 bg-gradient-to-r from-cyan-400/20 to-blue-400/20 border border-cyan-400/50 rounded-full text-cyan-300 text-sm font-semibold flex items-center justify-center gap-2 hover:border-cyan-300 transition-colors">
              <Sparkles size={16} className="animate-spin-slow" />
              Powered by Groq AI
            </div>
          </div>

          {/* Main Headline */}
          <div className="space-y-6 animate-fade-in-up animation-delay-200">
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-black leading-tight tracking-tight">
              <span className="block bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
                Detect
              </span>
              <span className="block bg-gradient-to-r from-purple-400 via-pink-400 to-red-400 bg-clip-text text-transparent">
                Misinformation & Bias
              </span>
            </h1>
          </div>

          {/* Subheading */}
          <div className="animate-fade-in-up animation-delay-400">
            <p className="text-lg md:text-2xl text-gray-300 max-w-3xl mx-auto leading-relaxed font-light">
              Analyze news articles with <span className="text-cyan-300 font-semibold">11 intelligent agents</span> to detect <span className="text-purple-300 font-semibold">misinformation</span>, <span className="text-blue-300 font-semibold">bias</span>, and <span className="text-pink-300 font-semibold">coordinated campaigns</span>
            </p>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-6 animate-fade-in-up animation-delay-600">
            <Link to="/analyze" className="group">
              <button className="flex items-center justify-center gap-3 w-full sm:w-auto px-8 py-4 text-lg bg-gradient-to-r from-cyan-400 to-blue-500 hover:from-cyan-300 hover:to-blue-400 text-dark-900 shadow-2xl shadow-cyan-500/50 hover:shadow-cyan-500/80 transition-all duration-300 font-bold rounded-xl hover:scale-105 active:scale-95">
                <span>Start Analysis</span>
                <ArrowRight size={24} className="group-hover:translate-x-1 transition-transform" />
              </button>
            </Link>
            <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="group">
              <button className="flex items-center justify-center gap-3 w-full sm:w-auto px-8 py-4 text-lg bg-dark-700 border-2 border-cyan-400 text-cyan-300 hover:bg-dark-600 transition-all duration-300 font-bold rounded-xl hover:border-cyan-300">
                <span>API Docs</span>
                <Code size={20} />
              </button>
            </a>
          </div>

          {/* Scroll Indicator */}
          <div className="absolute bottom-10 left-1/2 transform -translate-x-1/2 animate-bounce z-20">
            <div className="w-6 h-10 border-2 border-cyan-400 rounded-full flex items-center justify-center">
              <div className="w-1 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-24 md:py-32 px-4 md:px-0">
        <div className="max-w-7xl mx-auto">
          <div className="text-center space-y-6 mb-16 animate-fade-in-up">
            <h2 className="text-5xl md:text-6xl font-black bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
              Core Capabilities
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">Enterprise-grade features built for production</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, i) => (
              <div
                key={i}
                onMouseEnter={() => setHoveredFeature(i)}
                onMouseLeave={() => setHoveredFeature(null)}
                className="group rounded-xl p-8 bg-gradient-to-br from-dark-700 to-dark-800 border-2 border-dark-600 hover:border-cyan-400 transition-all duration-500 cursor-pointer hover:scale-105 hover:shadow-2xl hover:shadow-cyan-500/20 animate-fade-in-up"
                style={{ animationDelay: `${i * 80}ms` }}
              >
                <div className={`w-14 h-14 rounded-lg bg-gradient-to-br ${feature.color} flex items-center justify-center mb-6 group-hover:scale-125 group-hover:shadow-2xl transition-all duration-300 shadow-lg text-dark-900 font-bold`}>
                  <feature.icon size={28} />
                </div>
                <h3 className="text-xl font-bold text-gray-100 mb-2">{feature.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-24 md:py-32 px-4 md:px-0">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {[
              { label: 'Agents', value: '11', icon: Brain },
              { label: 'Analysis Time', value: '~8s', icon: Zap },
              { label: 'APIs', value: '3', icon: Code },
              { label: 'Accuracy', value: '95%+', icon: Shield },
            ].map((stat, i) => (
              <div key={i} className="text-center animate-fade-in-up" style={{ animationDelay: `${i * 100}ms` }}>
                <div className="flex justify-center mb-4">
                  <div className="w-16 h-16 rounded-lg bg-gradient-to-br from-cyan-400/20 to-purple-400/20 border border-cyan-400/50 flex items-center justify-center text-cyan-400">
                    <stat.icon size={32} />
                  </div>
                </div>
                <div className="text-4xl md:text-5xl font-black bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-400 font-semibold">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-24 md:py-32 px-4 md:px-0">
        <div className="max-w-5xl mx-auto">
          <div className="relative rounded-3xl overflow-hidden">
            {/* Animated Background */}
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/20 via-purple-500/20 to-blue-500/20 blur-2xl"></div>
            <div className="absolute inset-0 bg-gradient-to-br from-dark-800 to-dark-900 border border-cyan-400/40"></div>

            {/* Content */}
            <div className="relative p-12 md:p-24 text-center space-y-10">
              <h2 className="text-5xl md:text-7xl font-black bg-gradient-to-r from-cyan-300 via-purple-300 to-blue-300 bg-clip-text text-transparent leading-tight">
                Experience Intelligent<br />Analysis
              </h2>

              <p className="text-xl text-gray-300 max-w-2xl mx-auto font-light">
                Join organizations detecting misinformation and bias in news with AI-powered intelligence
              </p>

              <div className="flex justify-center pt-4">
                <Link to="/analyze">
                  <button className="flex items-center justify-center gap-3 px-10 py-4 text-lg bg-gradient-to-r from-cyan-400 to-blue-500 text-dark-900 shadow-2xl shadow-cyan-500/60 hover:shadow-cyan-500/90 hover:scale-105 active:scale-95 transition-all duration-300 font-bold rounded-xl">
                    <Rocket size={24} />
                    Start Building Now
                  </button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}
