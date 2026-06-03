import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Winner from './pages/Winner'
import Matches from './pages/Matches'
import GoldenBoot from './pages/GoldenBoot'

const navItems = [
  { to: '/', label: '🏠 דשבורד', end: true },
  { to: '/winner', label: '🏆 אלוף' },
  { to: '/matches', label: '⚽ משחקים' },
  { to: '/golden-boot', label: '👟 גביע הזהב' },
]

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col">
        <header className="bg-slate-900 border-b border-slate-700 sticky top-0 z-10">
          <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
            <h1 className="text-xl font-bold text-emerald-400">🎲 The Gambler</h1>
            <nav className="flex gap-2">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) =>
                    `px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-emerald-600 text-white'
                        : 'text-slate-300 hover:bg-slate-700'
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
        </header>

        <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/winner" element={<Winner />} />
            <Route path="/matches" element={<Matches />} />
            <Route path="/golden-boot" element={<GoldenBoot />} />
          </Routes>
        </main>

        <footer className="text-center text-slate-500 text-xs py-4 border-t border-slate-800">
          מבוסס על דירוגי FIFA, סטטיסטיקות היסטוריות ואודס בתי הימורים · מונדיאל 2026
        </footer>
      </div>
    </BrowserRouter>
  )
}
