import React from 'react';
import { motion } from 'framer-motion';
import AnimatedCounter from './AnimatedCounter';

export default function MetricCard({
  label,
  value,
  color = 'blue',
  icon: Icon,
  suffix = '',
  decimals = 0,
  delay = 0
}) {
  const colorClasses = {
    blue: 'bg-blue-500/10 border-blue-500/30 text-blue-300',
    green: 'bg-green-500/10 border-green-500/30 text-green-300',
    yellow: 'bg-yellow-500/10 border-yellow-500/30 text-yellow-300',
    purple: 'bg-purple-500/10 border-purple-500/30 text-purple-300',
  };

  const bgColor = colorClasses[color] || colorClasses.blue;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.6,
        delay,
        ease: 'easeOut'
      }}
      whileHover={{ scale: 1.05, boxShadow: '0 20px 40px rgba(0,0,0,0.3)' }}
      className={`${bgColor} border rounded-lg p-6 cursor-pointer transition-all`}
    >
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm font-medium">{label}</p>
        {Icon && <Icon className="w-5 h-5 opacity-60" />}
      </div>
      <motion.p className="text-3xl font-bold text-white">
        <AnimatedCounter
          value={value}
          duration={2}
          suffix={suffix}
          decimals={decimals}
        />
      </motion.p>
    </motion.div>
  );
}
