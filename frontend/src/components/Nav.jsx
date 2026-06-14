import { Link } from 'react-router-dom'
import { Activity, Search, BarChart3 } from 'lucide-react'

export default function Nav() {
  return (
    <nav className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2">
            <Activity className="w-6 h-6 text-blue-500" />
            <span className="text-xl font-bold text-white">NarrativeWatch</span>
          </Link>

          <div className="flex items-center gap-8">
            <Link
              to="/"
              className="text-slate-300 hover:text-white flex items-center gap-2 transition"
            >
              <BarChart3 className="w-4 h-4" />
              Home
            </Link>
            <Link
              to="/analyze"
              className="text-slate-300 hover:text-white flex items-center gap-2 transition"
            >
              <Search className="w-4 h-4" />
              Analyze
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}
