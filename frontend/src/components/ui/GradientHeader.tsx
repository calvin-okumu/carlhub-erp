import React from 'react';

interface GradientHeaderProps {
  title: string;
  subtitle?: string;
  className?: string;
}

export default function GradientHeader({ title, subtitle, className = '' }: GradientHeaderProps) {
  return (
    <div className={`bg-gradient-to-r from-blue-600 to-purple-600 text-white p-8 rounded-lg ${className}`}>
      <h1 className="text-3xl font-bold mb-2">{title}</h1>
      {subtitle && <p className="text-blue-100">{subtitle}</p>}
    </div>
  );
}