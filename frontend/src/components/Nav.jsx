import { Link } from 'react-router-dom'
import { Zap } from 'lucide-react'

export default function Nav() {
  return (
    <nav className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur border-b border-accent-500/10">
      <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 bg-gradient-to-br from-accent-500 to-accent-400 rounded-lg flex items-center justify-center group-hover:shadow-lg group-hover:shadow-accent-500/50 transition-all">
            <Zap size={24} className="text-slate-950" strokeWidth={3} />
          </div>
          <span className="text-xl font-bold bg-gradient-to-r from-accent-500 to-accent-400 bg-clip-text text-transparent">
            NarrativeWatch
          </span>
        </Link>

        <Link to="/analyze" className="btn-primary">
          Analyze Now
        </Link>
      </div>
    </nav>
  )
}
