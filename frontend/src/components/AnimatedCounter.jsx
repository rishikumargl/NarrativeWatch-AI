import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export default function AnimatedCounter({
  value = 0,
  duration = 2,
  prefix = '',
  suffix = '',
  decimals = 0
}) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    const startValue = 0;
    const endValue = parseFloat(value) || 0;
    const startTime = Date.now();
    const durationMs = duration * 1000;

    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / durationMs, 1);

      const currentValue = startValue + (endValue - startValue) * progress;
      setDisplayValue(currentValue);

      if (progress === 1) {
        clearInterval(interval);
      }
    }, 16); // ~60fps

    return () => clearInterval(interval);
  }, [value, duration]);

  const formatted = displayValue.toFixed(decimals);

  return (
    <span>
      {prefix}
      {formatted}
      {suffix}
    </span>
  );
}
