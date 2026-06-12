import { Link } from 'react-router-dom'
import { ArrowRight, Brain, Shield, TrendingUp, Zap, Search, Target, BarChart3 } from 'lucide-react'
import { useState } from 'react'

export default function HomePage() {
  const [hoveredFeature, setHoveredFeature] = useState(null)

  const features = [
    { icon: Brain, title: 'Content Analysis', desc: 'Extract facts and claims from any article' },
    { icon: Shield, title: 'Bias Detection', desc: 'Identify political and media bias patterns' },
    { icon: Zap, title: 'Real-Time Results', desc: 'Analyze articles in under 10 seconds' },
    { icon: Target, title: 'Risk Assessment', desc: 'Detect misinformation and coordinated campaigns' },
    { icon: Search, title: 'News Search', desc: 'Analyze multiple articles from one query' },
    { icon: BarChart3, title: 'Trust Scores', desc: 'Get credibility scores with explanations' },
  ]

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 pt-32 pb-24">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <div className="space-y-8">
            <div className="space-y-4 animate-fade-in-up">
              <div className="inline-block px-4 py-2 bg-accent-500/10 border border-accent-500/30 rounded-full">
                <span className="text-accent-400 text-sm font-semibold">Powered by 11 AI Agents</span>
              </div>
              <h1 className="text-6xl lg:text-7xl font-bold leading-tight">
                <span className="bg-gradient-to-r from-accent-500 via-accent-400 to-blue-400 bg-clip-text text-transparent">
                  Detect
                </span>
                <br />
                <span className="text-white">Misinformation</span>
                <br />
                <span className="text-white">Instantly</span>
              </h1>
              <p className="text-xl text-slate-300 leading-relaxed max-w-lg">
                Analyze news articles with AI-powered agents. Get trust scores, bias indicators, and credibility assessments in seconds.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 pt-6 animate-fade-in-up [animation-delay:200ms]">
              <Link to="/analyze" className="btn-primary flex items-center justify-center gap-2">
                Start Analysis <ArrowRight size={20} />
              </Link>
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-secondary flex items-center justify-center gap-2"
              >
                API Docs <ArrowRight size={20} />
              </a>
            </div>

            <div className="grid grid-cols-3 gap-6 pt-8 border-t border-accent-500/10 animate-fade-in-up [animation-delay:400ms]">
              <div>
                <div className="text-4xl font-bold text-accent-400">11</div>
                <p className="text-sm text-slate-400 mt-2">AI Agents</p>
              </div>
              <div>
                <div className="text-4xl font-bold text-accent-400">~8s</div>
                <p className="text-sm text-slate-400 mt-2">Analysis Time</p>
              </div>
              <div>
                <div className="text-4xl font-bold text-accent-400">95%+</div>
                <p className="text-sm text-slate-400 mt-2">Accuracy</p>
              </div>
            </div>
          </div>

          <div className="hidden lg:block animate-fade-in-up [animation-delay:300ms]">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-accent-500/20 to-blue-500/20 rounded-3xl blur-3xl"></div>
              <div className="relative glass-effect p-8 rounded-3xl space-y-6">
                {[
                  { title: 'Submit', desc: 'Article or search query', num: '1' },
                  { title: 'Analyze', desc: '11 agents process in parallel', num: '2' },
                  { title: 'Results', desc: 'Trust score + full report', num: '3' }
                ].map((step, idx) => (
                  <div key={idx} className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-accent-500 to-accent-400 flex items-center justify-center font-bold text-slate-950">
                      {step.num}
                    </div>
                    <div>
                      <div className="font-semibold text-white">{step.title}</div>
                      <div className="text-sm text-slate-400">{step.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-6 py-20 border-t border-accent-500/10">
        <div className="space-y-16">
          <div className="text-center space-y-4">
            <h2 className="text-5xl font-bold">How It Works</h2>
            <p className="text-xl text-slate-400">6 powerful capabilities working together</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, idx) => (
              <div
                key={idx}
                onMouseEnter={() => setHoveredFeature(idx)}
                onMouseLeave={() => setHoveredFeature(null)}
                className={`card-dark p-6 rounded-xl transition-all duration-300 cursor-pointer group ${
                  hoveredFeature === idx
                    ? 'border-accent-500/50 bg-slate-800/80 shadow-xl shadow-accent-500/10'
                    : 'hover:bg-slate-800/60'
                }`}
              >
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center mb-4 transition-all ${
                  hoveredFeature === idx
                    ? 'bg-gradient-to-br from-accent-500 to-accent-400'
                    : 'bg-accent-500/10'
                }`}>
                  <feature.icon
                    size={24}
                    className={hoveredFeature === idx ? 'text-slate-950' : 'text-accent-400'}
                  />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-accent-300 transition">
                  {feature.title}
                </h3>
                <p className="text-slate-400 text-sm leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Capabilities Section */}
      <section className="max-w-7xl mx-auto px-6 py-20 border-t border-accent-500/10">
        <div className="space-y-12">
          <h2 className="text-5xl font-bold text-center">What You Can Do</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="card-dark p-8 rounded-2xl space-y-4">
              <h3 className="text-2xl font-bold text-accent-400">Analyze Single Articles</h3>
              <ul className="space-y-3 text-slate-300">
                <li className="flex items-start gap-3">
                  <span className="text-accent-400 mt-1">✓</span>
                  <span>Submit article text, URL, or details</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-accent-400 mt-1">✓</span>
                  <span>Get misinformation detection</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-accent-400 mt-1">✓</span>
                  <span>Identify bias and risk factors</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-accent-400 mt-1">✓</span>
                  <span>See trust score with reasoning</span>
                </li>
              </ul>
            </div>

            <div className="card-dark p-8 rounded-2xl space-y-4">
              <h3 className="text-2xl font-bold text-accent-400">Search & Analyze News</h3>
              <ul className="space-y-3 text-slate-300">
                <li className="flex items-start gap-3">
                  <span className="text-accent-400 mt-1">✓</span>
                  <span>Search for news on any topic</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-accent-400 mt-1">✓</span>
                  <span>Analyze multiple articles at once</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-accent-400 mt-1">✓</span>
                  <span>Find dominant narratives</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-accent-400 mt-1">✓</span>
                  <span>Detect coordinated campaigns</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <div className="relative rounded-3xl overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-accent-500/20 to-blue-500/20"></div>
          <div className="absolute inset-0 bg-slate-800/50"></div>
          <div className="relative text-center space-y-8 py-20 px-8">
            <h2 className="text-5xl font-bold">Ready to analyze?</h2>
            <p className="text-xl text-slate-300 max-w-2xl mx-auto">
              Start detecting misinformation and bias in news articles. Powered by 11 specialized AI agents.
            </p>
            <Link to="/analyze" className="btn-primary inline-flex items-center gap-2 text-lg">
              Begin Analysis <ArrowRight size={24} />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-accent-500/10 py-12 mt-12">
        <div className="max-w-7xl mx-auto px-6 text-center text-slate-500 text-sm">
          <p>&copy; 2026 NarrativeWatch AI. Detecting misinformation with advanced AI.</p>
        </div>
      </footer>
    </main>
  )
}
