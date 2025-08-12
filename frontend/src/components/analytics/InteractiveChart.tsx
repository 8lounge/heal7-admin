'use client'

import React from 'react'
import { motion } from 'framer-motion'

interface ChartDataPoint {
  label: string
  value: number
  date?: string
}

interface InteractiveChartProps {
  data: ChartDataPoint[]
  type: 'line' | 'bar' | 'area'
  height?: number
  color?: string
  title?: string
}

export default function InteractiveChart({ 
  data, 
  type = 'line', 
  height = 200, 
  color = '#3B82F6',
  title 
}: InteractiveChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-gray-400">
        <p>데이터를 불러오는 중...</p>
      </div>
    )
  }

  const maxValue = Math.max(...data.map(d => d.value))
  const minValue = Math.min(...data.map(d => d.value))
  const range = maxValue - minValue || 1
  const padding = 40
  const chartWidth = 400
  const chartHeight = height - padding * 2

  const getY = (value: number) => {
    return chartHeight - ((value - minValue) / range) * chartHeight + padding
  }

  const getX = (index: number) => {
    return (index / (data.length - 1)) * chartWidth + padding
  }

  const renderLineChart = () => {
    const pathD = data
      .map((point, index) => {
        const x = getX(index)
        const y = getY(point.value)
        return `${index === 0 ? 'M' : 'L'} ${x} ${y}`
      })
      .join(' ')

    return (
      <g>
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio, i) => (
          <line
            key={i}
            x1={padding}
            y1={padding + chartHeight * ratio}
            x2={chartWidth + padding}
            y2={padding + chartHeight * ratio}
            stroke="#f3f4f6"
            strokeWidth={1}
          />
        ))}

        {/* Area fill */}
        {type === 'area' && (
          <motion.path
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.2 }}
            transition={{ duration: 1 }}
            d={`${pathD} L ${getX(data.length - 1)} ${getY(minValue)} L ${getX(0)} ${getY(minValue)} Z`}
            fill={color}
          />
        )}

        {/* Main line */}
        <motion.path
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1.5, ease: "easeInOut" }}
          d={pathD}
          stroke={color}
          strokeWidth={3}
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Data points */}
        {data.map((point, index) => (
          <motion.circle
            key={index}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            whileHover={{ scale: 1.5 }}
            cx={getX(index)}
            cy={getY(point.value)}
            r={4}
            fill={color}
            stroke="white"
            strokeWidth={2}
            className="cursor-pointer"
          >
            <title>{`${point.label}: ${point.value}`}</title>
          </motion.circle>
        ))}
      </g>
    )
  }

  const renderBarChart = () => {
    const barWidth = chartWidth / data.length * 0.6
    const barSpacing = chartWidth / data.length * 0.4

    return (
      <g>
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio, i) => (
          <line
            key={i}
            x1={padding}
            y1={padding + chartHeight * ratio}
            x2={chartWidth + padding}
            y2={padding + chartHeight * ratio}
            stroke="#f3f4f6"
            strokeWidth={1}
          />
        ))}

        {/* Bars */}
        {data.map((point, index) => {
          const x = padding + (index * (chartWidth / data.length)) + barSpacing / 2
          const y = getY(point.value)
          const barHeight = getY(minValue) - y

          return (
            <motion.rect
              key={index}
              initial={{ height: 0, y: getY(minValue) }}
              animate={{ height: barHeight, y }}
              transition={{ duration: 0.8, delay: index * 0.1 }}
              whileHover={{ opacity: 0.8 }}
              x={x}
              y={y}
              width={barWidth}
              height={barHeight}
              fill={color}
              rx={3}
              className="cursor-pointer"
            >
              <title>{`${point.label}: ${point.value}`}</title>
            </motion.rect>
          )
        })}
      </g>
    )
  }

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-lg font-semibold mb-4 text-gray-800">{title}</h3>
      )}
      
      <svg
        width={chartWidth + padding * 2}
        height={height}
        className="w-full h-auto"
        viewBox={`0 0 ${chartWidth + padding * 2} ${height}`}
      >
        {/* Y-axis labels */}
        {[maxValue, maxValue * 0.75, maxValue * 0.5, maxValue * 0.25, minValue].map((value, i) => (
          <text
            key={i}
            x={padding - 10}
            y={padding + (chartHeight * i / 4) + 5}
            textAnchor="end"
            className="text-xs fill-gray-500"
          >
            {Math.round(value).toLocaleString()}
          </text>
        ))}

        {/* X-axis labels */}
        {data.map((point, index) => (
          <text
            key={index}
            x={getX(index)}
            y={height - padding + 20}
            textAnchor="middle"
            className="text-xs fill-gray-500"
          >
            {point.label.length > 8 ? point.label.substring(0, 8) + '...' : point.label}
          </text>
        ))}

        {/* Chart content */}
        {type === 'bar' ? renderBarChart() : renderLineChart()}
      </svg>

      {/* Legend */}
      <div className="flex justify-between items-center mt-4 text-sm text-gray-600">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div 
              className="w-3 h-3 rounded" 
              style={{ backgroundColor: color }}
            ></div>
            <span>총 {data.length}개 데이터 포인트</span>
          </div>
          <span>최대값: {maxValue.toLocaleString()}</span>
        </div>
      </div>
    </div>
  )
}