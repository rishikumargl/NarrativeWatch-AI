import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Brain, Zap, CheckCircle, TrendingUp } from 'lucide-react'

export default function LandingPage() {
  const [hoveredFeature, setHoveredFeature] = useState(null)

  return (
    <main className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">NarrativeWatch</h1>
          <Link to="/analyze" className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
            Analyze Now
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Left: Text */}
          <div className="space-y-8">
            <div className="space-y-4">
              <h2 className="text-5xl lg:text-6xl font-bold text-gray-900 leading-tight">
                Detect Misinformation in News
              </h2>
              <p className="text-xl text-gray-600 leading-relaxed">
                Analyze articles with 11 AI agents to identify bias, misinformation, and coordinated campaigns. Get trust scores in seconds.
              </p>
            </div>

            <div className="flex gap-4 pt-6">
              <Link to="/analyze" className="flex items-center gap-2 px-8 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition">
                Get Started
                <ArrowRight size={20} />
              </Link>
              <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="px-8 py-3 border-2 border-gray-300 text-gray-900 font-medium rounded-lg hover:border-blue-600 hover:text-blue-600 transition">
                API Docs
              </a>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-6 pt-8 border-t border-gray-200">
              <div>
                <div className="text-3xl font-bold text-gray-900">11</div>
                <p className="text-sm text-gray-600">Specialized Agents</p>
              </div>
              <div>
                <div className="text-3xl font-bold text-gray-900">~8s</div>
                <p className="text-sm text-gray-600">Analysis Time</p>
              </div>
              <div>
                <div className="text-3xl font-bold text-gray-900">95%+</div>
                <p className="text-sm text-gray-600">Accuracy</p>
              </div>
            </div>
          </div>

          {/* Right: Visual */}
          <div className="hidden lg:block">
            <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-12 border border-gray-200">
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex items-center gap-3 p-4 bg-white rounded-lg border border-gray-200 hover:border-blue-400 transition">
                    <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                    <div className="flex-1 h-2 bg-gray-300 rounded"></div>
                    <div className="text-sm text-gray-400">AI Agent {i}</div>
                  </div>
                ))}
              </div>
              <div className="mt-8 p-6 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center gap-2 text-sm text-blue-600 font-medium">
                  <CheckCircle size={18} />
                  Analysis Complete
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="bg-gray-50 border-t border-gray-200 py-20">
        <div className="max-w-7xl mx-auto px-6">
          <h3 className="text-4xl font-bold text-gray-900 mb-4">How It Works</h3>
          <p className="text-lg text-gray-600 mb-12">Four simple steps to analyze any article</p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { step: 1, title: 'Submit Article', desc: 'Paste text or search for news' },
              { step: 2, title: 'Run Analysis', desc: '11 agents analyze in parallel' },
              { step: 3, title: 'Get Results', desc: 'Detailed findings in ~8 seconds' },
              { step: 4, title: 'Review Trust Score', desc: 'See credibility and risk factors' },
            ].map((item, idx) => (
              <div key={idx} className="relative">
                <div className="bg-white p-8 rounded-lg border border-gray-200 hover:border-blue-400 transition h-full">
                  <div className="flex items-center justify-center w-12 h-12 rounded-full bg-blue-100 text-blue-600 font-bold mb-4">
                    {item.step}
                  </div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">{item.title}</h4>
                  <p className="text-gray-600 text-sm">{item.desc}</p>
                </div>
                {idx < 3 && <div className="hidden lg:block absolute top-1/3 -right-3 w-6 h-1 bg-gray-300"></div>}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <h3 className="text-4xl font-bold text-gray-900 mb-4">Powered By</h3>
        <p className="text-lg text-gray-600 mb-12">Advanced AI agents for comprehensive analysis</p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            { icon: Brain, title: 'Content Analyzer', desc: 'Extract key facts and claims' },
            { icon: TrendingUp, title: 'Bias Detector', desc: 'Identify political and media bias' },
            { icon: Zap, title: 'Real-time Processing', desc: 'Analyze in under 10 seconds' },
            { icon: CheckCircle, title: 'Fact Checking', desc: 'Cross-reference with research' },
            { icon: TrendingUp, title: 'Sentiment Analysis', desc: 'Measure emotional tone' },
            { icon: Brain, title: 'Pattern Detection', desc: 'Find coordinated narratives' },
          ].map((feature, idx) => (
            <div
              key={idx}
              onMouseEnter={() => setHoveredFeature(idx)}
              onMouseLeave={() => setHoveredFeature(null)}
              className={`p-6 border-2 rounded-lg transition ${
                hoveredFeature === idx
                  ? 'border-blue-600 bg-blue-50'
                  : 'border-gray-200 bg-white'
              }`}
            >
              <feature.icon
                size={24}
                className={`mb-4 transition ${
                  hoveredFeature === idx ? 'text-blue-600' : 'text-gray-400'
                }`}
              />
              <h4 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h4>
              <p className="text-gray-600 text-sm">{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gray-900 text-white py-20">
        <div className="max-w-3xl mx-auto px-6 text-center space-y-8">
          <h3 className="text-4xl font-bold">Ready to analyze?</h3>
          <p className="text-xl text-gray-300">
            Start detecting misinformation in news articles. No signup required.
          </p>
          <Link
            to="/analyze"
            className="inline-flex items-center gap-2 px-8 py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition text-lg"
          >
            Analyze Now
            <ArrowRight size={24} />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white py-12">
        <div className="max-w-7xl mx-auto px-6 text-center text-gray-600 text-sm">
          <p>&copy; 2026 NarrativeWatch AI. Detecting misinformation in real-time.</p>
        </div>
      </footer>
    </main>
  )
}
