import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { computeScores } from '../lib/scoring'
import { TEAMS } from '../data/teams'

const scores = computeScores(TEAMS)

const COLORS = ['#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#d1fae5']

function getColor(index: number): string {
  return COLORS[Math.min(index, COLORS.length - 1)]
}

export default function Winner() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">🏆 מי יזכה במונדיאל?</h2>
        <p className="text-slate-400 mt-1">
          ציון כולל = אודס 40% + דירוג FIFA 35% + היסטוריה 25%
        </p>
      </div>

      {/* Chart */}
      <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <h3 className="text-sm font-medium text-slate-400 mb-4">ציון כולל לפי קבוצה (Top 10)</h3>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={scores.slice(0, 10)} layout="vertical" margin={{ left: 20, right: 20 }}>
            <XAxis type="number" domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <YAxis
              type="category"
              dataKey="team.name"
              width={80}
              tick={{ fill: '#e2e8f0', fontSize: 13 }}
            />
            <Tooltip
              contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
              labelStyle={{ color: '#f1f5f9' }}
              formatter={(value: number) => [`${value} נקודות`, 'ציון']}
            />
            <Bar dataKey="total" radius={[0, 4, 4, 0]}>
              {scores.slice(0, 10).map((_, i) => (
                <Cell key={i} fill={getColor(i)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Table */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700 text-slate-400 text-right">
              <th className="py-3 px-4">#</th>
              <th className="py-3 px-4">קבוצה</th>
              <th className="py-3 px-4">דירוג FIFA</th>
              <th className="py-3 px-4">אודס → %</th>
              <th className="py-3 px-4">היסטוריה</th>
              <th className="py-3 px-4">ציון כולל</th>
              <th className="py-3 px-4">אליפויות</th>
            </tr>
          </thead>
          <tbody>
            {scores.map((s, i) => (
              <tr
                key={s.team.name}
                className={`border-b border-slate-700/50 transition-colors hover:bg-slate-700/30 ${
                  i < 3 ? 'bg-emerald-900/10' : ''
                }`}
              >
                <td className="py-3 px-4 text-slate-400 font-mono">
                  {i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : i + 1}
                </td>
                <td className="py-3 px-4 font-medium">
                  <span className="ml-2">{s.team.flag}</span>
                  {s.team.name}
                </td>
                <td className="py-3 px-4 text-slate-300">#{s.team.fifaRank}</td>
                <td className="py-3 px-4">
                  <span className="text-emerald-400 font-semibold">
                    {Math.round(s.team.oddsProb * 100)}%
                  </span>
                </td>
                <td className="py-3 px-4 text-slate-300">{s.historyScore}</td>
                <td className="py-3 px-4">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-slate-700 rounded-full h-2 max-w-24">
                      <div
                        className="bg-emerald-500 h-2 rounded-full"
                        style={{ width: `${s.total}%` }}
                      />
                    </div>
                    <span className="font-bold text-white">{s.total}</span>
                  </div>
                </td>
                <td className="py-3 px-4 text-yellow-400">
                  {'🏆'.repeat(s.team.titles)}
                  {s.team.titles === 0 && <span className="text-slate-500">—</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700 text-sm text-slate-400">
        <strong className="text-slate-200">⚠️ שים לב:</strong> האודס מעודכן לתאריך הכנת הכלי. לעדכון,
        ערוך את <code className="bg-slate-700 px-1 rounded">src/data/teams.ts</code> ושנה את{' '}
        <code className="bg-slate-700 px-1 rounded">oddsProb</code> לפי ה-implied probability מה-bookmaker שלך.
      </div>
    </div>
  )
}
