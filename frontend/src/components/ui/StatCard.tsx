import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  color?: string;
  className?: string;
  onClick?: () => void;
  trend?: {
    value: number;
    period: string;
  };
  subtitle?: string;
  loading?: boolean;
}

export default function StatCard({ 
  title, 
  value, 
  icon: Icon, 
  color = 'blue', 
  className = '', 
  onClick, 
  trend,
  subtitle,
  loading = false
}: StatCardProps) {
  const colorClasses = {
    blue: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      icon: 'text-blue-600',
      gradient: 'from-blue-500 to-blue-600'
    },
    green: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      icon: 'text-green-600',
      gradient: 'from-green-500 to-green-600'
    },
    red: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      icon: 'text-red-600',
      gradient: 'from-red-500 to-red-600'
    },
    yellow: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      icon: 'text-yellow-600',
      gradient: 'from-yellow-500 to-yellow-600'
    },
    purple: {
      bg: 'bg-purple-50',
      border: 'border-purple-200',
      icon: 'text-purple-600',
      gradient: 'from-purple-500 to-purple-600'
    },
    gray: {
      bg: 'bg-gray-50',
      border: 'border-gray-200',
      icon: 'text-gray-600',
      gradient: 'from-gray-500 to-gray-600'
    }
  };

  const colors = colorClasses[color as keyof typeof colorClasses] || colorClasses.blue;

  const getTrendIcon = (trendValue: number) => {
    if (trendValue > 0) return TrendingUp;
    if (trendValue < 0) return TrendingDown;
    return Minus;
  };

  const getTrendColor = (trendValue: number) => {
    if (trendValue > 0) return 'text-green-600 bg-green-50';
    if (trendValue < 0) return 'text-red-600 bg-red-50';
    return 'text-gray-600 bg-gray-50';
  };

  return (
    <div
      className={`relative bg-white border ${colors.border} rounded-xl p-6 shadow-sm hover:shadow-md transition-all duration-300 ${
        onClick ? 'cursor-pointer hover:scale-[1.02] hover:-translate-y-1' : ''
      } ${className}`}
      onClick={onClick}
    >
      {/* Background gradient decoration */}
      <div className={`absolute top-0 right-0 w-20 h-20 bg-gradient-to-br ${colors.gradient} opacity-5 rounded-bl-xl`}></div>
      
      <div className="relative">
        {/* Header with icon */}
        <div className="flex items-start justify-between mb-4">
          <div className={`p-3 ${colors.bg} rounded-lg`}>
            <Icon className={`h-6 w-6 ${colors.icon}`} />
          </div>
          {trend && (
            <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getTrendColor(trend.value)}`}>
              {React.createElement(getTrendIcon(trend.value), { className: 'w-3 h-3' })}
              {Math.abs(trend.value)}%
            </div>
          )}
        </div>

        {/* Main content */}
        <div className="space-y-1">
          {loading ? (
            <div className="space-y-2">
              <div className="h-8 bg-gray-200 rounded animate-pulse"></div>
              <div className="h-4 bg-gray-100 rounded w-3/4 animate-pulse"></div>
            </div>
          ) : (
            <>
              <div className="text-3xl font-bold text-gray-900 leading-tight">
                {value}
              </div>
              <div className="text-sm font-medium text-gray-600">
                {title}
              </div>
              {subtitle && (
                <div className="text-xs text-gray-500 mt-1">
                  {subtitle}
                </div>
              )}
              {trend && (
                <div className="text-xs text-gray-500 mt-2">
                  vs {trend.period}
                </div>
              )}
            </>
          )}
        </div>

        {/* Hover effect overlay */}
        {onClick && (
          <div className="absolute inset-0 bg-blue-600 opacity-0 hover:opacity-5 rounded-xl transition-opacity duration-300 pointer-events-none"></div>
        )}
      </div>
    </div>
  );
}