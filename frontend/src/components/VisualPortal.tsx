import React from 'react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell 
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface VisualData {
  type: 'line' | 'bar' | 'pie' | 'none';
  chart_data: Array<{ name: string; value: number }>;
  insight_cards: Array<{ title: string; content: string }>;
}

interface Sentiment {
  score: number;
  label: string;
  confidence: number;
}

interface AIResponse {
  summary: string;
  sentiment: Sentiment;
  visuals: VisualData;
  sources: string[];
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export const VisualPortal: React.FC<{ data: AIResponse | null }> = ({ data }) => {
  if (!data) return null;

  const renderChart = () => {
    const { type, chart_data } = data.visuals;

    if (type === 'none' || !chart_data || chart_data.length === 0) {
      return (
        <div className="h-full flex items-center justify-center text-slate-500 italic">
          No visual representation available for this analysis.
        </div>
      );
    }

    if (type === 'line' || type === 'bar') {
      const ChartComponent = type === 'line' ? AreaChart : BarChart;
      const DataComponent = type === 'line' ? Area : Bar;

      return (
        <ResponsiveContainer width="100%" height="100%">
          <ChartComponent data={chart_data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="name" stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
            <YAxis stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', color: '#f8fafc' }}
            />
            {type === 'line' ? (
              <Area type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorPortal)" />
            ) : (
              <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            )}
            <defs>
              <linearGradient id="colorPortal" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
            </defs>
          </ChartComponent>
        </ResponsiveContainer>
      );
    }

    if (type === 'pie') {
      return (
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chart_data}
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="value"
            >
              {chart_data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', color: '#f8fafc' }}
            />
          </PieChart>
        </ResponsiveContainer>
      );
    }

    if (type === 'heatmap') {
        return (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 h-full p-4 overflow-y-auto">
                {chart_data.map((item: any, i: number) => (
                    <motion.div 
                        key={i}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex flex-col items-center justify-center p-4 rounded-xl border border-slate-800"
                        style={{ 
                            backgroundColor: `rgba(${item.intensity > 50 ? '16, 185, 129' : '239, 68, 68'}, ${Math.abs(item.intensity - 50) / 50 * 0.4})` 
                        }}
                    >
                        <span className="text-white font-bold text-sm tracking-tighter">{item.name}</span>
                        <span className="text-xs text-slate-400 mt-1 uppercase font-bold">{item.label}</span>
                    </motion.div>
                ))}
            </div>
        )
    }

    if (type === 'candlestick') {
        return (
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chart_data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                    <XAxis dataKey="name" stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
                    <YAxis stroke="#475569" fontSize={10} tickLine={false} axisLine={false} domain={['auto', 'auto']} />
                    <Tooltip cursor={{fill: 'transparent'}} contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px' }} />
                    <Bar dataKey="close" fill="#3b82f6">
                        {chart_data.map((entry: any, index: number) => (
                            <Cell 
                                key={`cell-${index}`} 
                                fill={entry.close > entry.open ? '#10b981' : '#ef4444'} 
                            />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        )
    }

    return null;
  };

  const getSentimentIcon = () => {
    const label = data.sentiment.label.toLowerCase();
    if (label.includes('bull')) return <TrendingUp className="text-emerald-400" />;
    if (label.includes('bear')) return <TrendingDown className="text-red-400" />;
    return <Minus className="text-blue-400" />;
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-12"
    >
      {/* Narrative & Insight Cards */}
      <div className="lg:col-span-1 flex flex-col gap-6">
        <div className="glass-card rounded-2xl p-6 border-l-4 border-blue-500">
          <h4 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-2 flex items-center justify-between">
            Analysis Summary
            {getSentimentIcon()}
          </h4>
          <p className="text-slate-300 leading-relaxed text-sm">
            {data.summary}
          </p>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {data.visuals.insight_cards.map((card, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-slate-900/50 backdrop-blur-sm border border-slate-800 p-4 rounded-xl"
            >
              <h5 className="text-white font-semibold text-xs mb-1 flex items-center gap-2">
                <AlertCircle className="w-3 h-3 text-blue-400" />
                {card.title}
              </h5>
              <p className="text-slate-400 text-xs">{card.content}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Dynamic Visual Area */}
      <div className="lg:col-span-2 glass-card rounded-3xl p-8 min-h-[400px]">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h3 className="text-xl font-semibold text-white">Visual Intelligence</h3>
            <p className="text-slate-400 text-sm">Dynamic rendering of data points</p>
          </div>
          <div className="px-3 py-1 bg-slate-800 rounded-full text-[10px] font-bold text-slate-500 uppercase">
            {data.visuals.type} projection
          </div>
        </div>
        <div className="h-[300px] w-full">
          {renderChart()}
        </div>
      </div>
    </motion.div>
  );
};
