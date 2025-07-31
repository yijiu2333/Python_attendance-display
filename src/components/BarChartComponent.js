import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { animated } from '@react-spring/web';
import { useSpring } from '@react-spring/core';

const AnimatedBar = animated(Bar);

export default function BarChartComponent({ data, width = '100%', height = 400 }) {
  const springProps = useSpring({
    from: { opacity: 0, transform: 'scaleY(0)' },
    to: { opacity: 1, transform: 'scaleY(1)' },
    config: { tension: 210, friction: 20 }
  });

  return (
    <div style={{ overflowX: 'auto', whiteSpace: 'nowrap', padding: '1rem', margin: 'auto' }}>
      <ResponsiveContainer width={width} height={height}>
        <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis 
            dataKey="name" 
            angle={-45} 
            textAnchor="end" 
            height={60} 
            tick={{ fontSize: 12 }} 
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #ddd',
              borderRadius: '4px'
            }}
            formatter={(value) => [`${value}人`, '人数']}
          />
          <AnimatedBar
            dataKey="value"
            fill="#8884d8"
            radius={[4, 4, 0, 0]}
            style={springProps}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}