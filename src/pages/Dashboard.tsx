import { Link } from 'react-router-dom'
import { computeScores } from '../lib/scoring'
import { TEAMS } from '../data/teams'
import candidates from '../data/golden-boot-candidates.json'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip } from 'recharts'

const scores = computeScores(TEAMS)
const top3 = scores.slice(0, 3)
const goldenBootFav = [...candidates].sort((a, b) => a.decimalOdds - b.decimalOdds)[0]

const medals = ['🥇', '🥈', '🥉']

export default function Dashboard() {
  const topTeam = top3[0]
  const radarData = [
    { subject: 'אודס', value: topTeam.oddsScore },
    { subject: 'FIFA', value: topTeam.fifaScore },
    { subject: 'היסטוריה', value: topTeam.historyScore },
    { subject: 'אליפויות', value: Math.min(topTeam.team.titles * 20, 100) },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">🏠 דשבורד — מונדיאל 2026</h2>
        <p className="text-slate-400 mt-1">סיכום המלצות לפי כל הפרמטרים</p>
      </div>

      {/* Top picks */}
      <div className="grid gap-4 md:grid-cols-3">
        {top3.map((s, i) => (
          <div
            key={s.team.name}
            className={`bg-slate-800 rounded-xl p-4 border ${
              i === 0 ? 'border-emerald-500' : 'border-slate-700'
            }`}
          >
            <div className="text-3xl mb-2">{medals[i]}</div>
            <div className="flex items-center gap-2 text-xl font-bold text-white">
              <span>{s.team.flag}</span>
              <span>{s.team.name}</span>
            </div>
            <div className="mt-2 text-sm text-slate-400">
              ציון כולל:{' '}
              <span className="text-emerald-400 font-bold text-lg">{s.total}</span>
            </div>
            <div className="mt-1 flex gap-3 text-xs text-slate-500">
              <span>FIFA #{s.team.fifaRank}</span>
              <span>{Math.round(s.team.oddsProb * 100)}% סיכוי</span>
            </div>
          </div>
        ))}
      </div>

      {/* Radar + Golden boot fav */}
      <div className="grid gap-4 md:grid-cols-2">
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <h3 className="text-sm font-medium text-slate-400 mb-2">
            פרופיל מועמד #1: {topTeam.team.flag} {topTeam.team.name}
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#334155" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <Radar
                dataKey="value"
                stroke="#10b981"
                fill="#10b981"
                fillOpacity={0.3}
              />
              <Tooltip
                contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <h3 className="text-sm font-medium text-slate-400 mb-3">👟 פייבוריט גביע הזהב</h3>
          <div className="flex items-center gap-3 mb-3">
            <span className="text-4xl">{goldenBootFav.flag}</span>
            <div>
              <div className="font-bold text-white text-lg">{goldenBootFav.name}</div>
              <div className="text-slate-400 text-sm">{goldenBootFav.country} · {goldenBootFav.club}</div>
            </div>
          </div>
          <div className="flex gap-4 text-sm">
            <div className="bg-slate-700 rounded-lg p-3 flex-1 text-center">
              <div className="text-emerald-400 font-bold text-xl">x{goldenBootFav.decimalOdds}</div>
              <div className="text-slate-400 text-xs">אודס</div>
            </div>
            <div className="bg-slate-700 rounded-lg p-3 flex-1 text-center">
              <div className="text-white font-bold text-xl">{goldenBootFav.avgGoalsPerWC}</div>
              <div className="text-slate-400 text-xs">גולים ממוצע</div>
            </div>
          </div>
          <p className="mt-3 text-xs text-slate-400">{goldenBootFav.note}</p>
        </div>
      </div>

      {/* Quick links */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { to: '/winner', icon: '🏆', label: 'מי יזכה?' },
          { to: '/matches', icon: '⚽', label: 'ניתוח משחקים' },
          { to: '/golden-boot', icon: '👟', label: 'גביע הזהב' },
        ].map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className="bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl p-4 text-center transition-colors"
          >
            <div className="text-2xl mb-1">{link.icon}</div>
            <div className="text-sm font-medium text-slate-300">{link.label}</div>
          </Link>
        ))}
      </div>
    </div>
  )
}
