import React, { useEffect, useState } from 'react';
import riskAPI from './api';
import { Line, Bar } from 'react-chartjs-2';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement,
  Title, 
  Tooltip, 
  Legend 
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement,
  Title, 
  Tooltip, 
  Legend
);

const ModelPerformanceLog = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMetric, setSelectedMetric] = useState('accuracy');
  const [selectedModels, setSelectedModels] = useState([]);
  const [viewMode, setViewMode] = useState('table'); // 'table', 'line', 'bar'
  const [sortConfig, setSortConfig] = useState({ key: 'timestamp', direction: 'desc' });

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await riskAPI.get('/api/risk/models/');
        setLogs(response.data);

        // Initialize selectedModels with all unique model versions
        const uniqueModels = [...new Set(response.data.map(log => log.model_version))];
        setSelectedModels(uniqueModels);
      } catch (err) {
        console.error('Error fetching model performance logs:', err);
        setError('Failed to load model performance logs. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchLogs();
  }, []);

  // Sort logs based on current sort configuration
  const sortedLogs = React.useMemo(() => {
    let sortableLogs = [...logs];
    if (sortConfig.key) {
      sortableLogs.sort((a, b) => {
        if (a[sortConfig.key] < b[sortConfig.key]) {
          return sortConfig.direction === 'asc' ? -1 : 1;
        }
        if (a[sortConfig.key] > b[sortConfig.key]) {
          return sortConfig.direction === 'asc' ? 1 : -1;
        }
        return 0;
      });
    }
    return sortableLogs;
  }, [logs, sortConfig]);

  // Filter logs based on selected models
  const filteredLogs = React.useMemo(() => {
    return sortedLogs.filter(log => selectedModels.includes(log.model_version));
  }, [sortedLogs, selectedModels]);

  // Request a sort
  const requestSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  // Toggle model selection
  const toggleModelSelection = (modelVersion) => {
    if (selectedModels.includes(modelVersion)) {
      setSelectedModels(selectedModels.filter(m => m !== modelVersion));
    } else {
      setSelectedModels([...selectedModels, modelVersion]);
    }
  };

  // Prepare chart data
  const prepareChartData = () => {
    // Group logs by model version
    const modelGroups = {};
    filteredLogs.forEach(log => {
      if (!modelGroups[log.model_version]) {
        modelGroups[log.model_version] = [];
      }
      modelGroups[log.model_version].push(log);
    });

    // Sort each group by timestamp
    Object.keys(modelGroups).forEach(model => {
      modelGroups[model].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    });

    // Create datasets for the chart
    const datasets = Object.keys(modelGroups).map((model, index) => {
      const colors = ['blue', 'green', 'red', 'purple', 'orange', 'cyan', 'magenta'];
      return {
        label: model,
        data: modelGroups[model].map(log => log[selectedMetric]),
        borderColor: colors[index % colors.length],
        backgroundColor: colors[index % colors.length] + '33', // Add transparency
        fill: false,
      };
    });

    // Get all unique timestamps across all models
    const allTimestamps = [...new Set(filteredLogs.map(log => 
      new Date(log.timestamp).toLocaleDateString()
    ))];
    allTimestamps.sort((a, b) => new Date(a) - new Date(b));

    return {
      labels: allTimestamps,
      datasets,
    };
  };

  const chartData = React.useMemo(() => prepareChartData(), [filteredLogs, selectedMetric]);

  if (loading) {
    return <p className="p-4 text-center">Loading...</p>;
  }

  if (error) {
    return <p className="p-4 text-red-500 text-center">{error}</p>;
  }

  // Get unique model versions for filter
  const uniqueModels = [...new Set(logs.map(log => log.model_version))];

  return (
    <div className="p-4 max-w-5xl mx-auto">
      <h2 className="text-xl font-bold mb-4">Model Performance Dashboard</h2>

      {/* Controls */}
      <div className="mb-6 flex flex-wrap gap-4 items-center">
        <div>
          <label className="mr-2 font-medium">View Mode:</label>
          <select 
            className="p-2 border rounded"
            value={viewMode} 
            onChange={(e) => setViewMode(e.target.value)}
          >
            <option value="table">Table</option>
            <option value="line">Line Chart</option>
            <option value="bar">Bar Chart</option>
          </select>
        </div>

        {viewMode !== 'table' && (
          <div>
            <label className="mr-2 font-medium">Metric:</label>
            <select 
              className="p-2 border rounded"
              value={selectedMetric} 
              onChange={(e) => setSelectedMetric(e.target.value)}
            >
              <option value="accuracy">Accuracy</option>
              <option value="precision">Precision</option>
              <option value="recall">Recall</option>
              <option value="auc_score">AUC Score</option>
              <option value="f1_score">F1 Score</option>
            </select>
          </div>
        )}

        <div>
          <label className="mr-2 font-medium">Filter Models:</label>
          <div className="flex flex-wrap gap-2">
            {uniqueModels.map(model => (
              <label key={model} className="inline-flex items-center">
                <input 
                  type="checkbox" 
                  checked={selectedModels.includes(model)} 
                  onChange={() => toggleModelSelection(model)}
                  className="mr-1"
                />
                {model}
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* Table View */}
      {viewMode === 'table' && (
        <div className="overflow-x-auto">
          <table className="w-full table-auto text-sm border">
            <thead className="bg-gray-100">
              <tr>
                <th 
                  className="cursor-pointer hover:bg-gray-200 p-2"
                  onClick={() => requestSort('model_version')}
                >
                  Model {sortConfig.key === 'model_version' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                </th>
                <th 
                  className="cursor-pointer hover:bg-gray-200 p-2"
                  onClick={() => requestSort('accuracy')}
                >
                  Accuracy {sortConfig.key === 'accuracy' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                </th>
                <th 
                  className="cursor-pointer hover:bg-gray-200 p-2"
                  onClick={() => requestSort('precision')}
                >
                  Precision {sortConfig.key === 'precision' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                </th>
                <th 
                  className="cursor-pointer hover:bg-gray-200 p-2"
                  onClick={() => requestSort('recall')}
                >
                  Recall {sortConfig.key === 'recall' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                </th>
                <th 
                  className="cursor-pointer hover:bg-gray-200 p-2"
                  onClick={() => requestSort('auc_score')}
                >
                  AUC {sortConfig.key === 'auc_score' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                </th>
                <th 
                  className="cursor-pointer hover:bg-gray-200 p-2"
                  onClick={() => requestSort('f1_score')}
                >
                  F1 {sortConfig.key === 'f1_score' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                </th>
                <th 
                  className="cursor-pointer hover:bg-gray-200 p-2"
                  onClick={() => requestSort('timestamp')}
                >
                  Date {sortConfig.key === 'timestamp' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.map((log) => (
                <tr key={log.id} className="text-center border-t hover:bg-gray-50">
                  <td className="p-2">{log.model_version}</td>
                  <td className="p-2">{log.accuracy.toFixed(4)}</td>
                  <td className="p-2">{log.precision.toFixed(4)}</td>
                  <td className="p-2">{log.recall.toFixed(4)}</td>
                  <td className="p-2">{log.auc_score.toFixed(4)}</td>
                  <td className="p-2">{log.f1_score.toFixed(4)}</td>
                  <td className="p-2">{new Date(log.timestamp).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Line Chart View */}
      {viewMode === 'line' && (
        <div>
          <h3 className="text-lg font-semibold mb-2">
            {selectedMetric.charAt(0).toUpperCase() + selectedMetric.slice(1).replace('_', ' ')} Over Time
          </h3>
          <Line data={chartData} options={{
            responsive: true,
            plugins: {
              legend: {
                position: 'top',
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    return `${context.dataset.label}: ${context.parsed.y.toFixed(4)}`;
                  }
                }
              }
            },
            scales: {
              y: {
                min: 0,
                max: 1,
                title: {
                  display: true,
                  text: selectedMetric.charAt(0).toUpperCase() + selectedMetric.slice(1).replace('_', ' ')
                }
              }
            }
          }} />
        </div>
      )}

      {/* Bar Chart View */}
      {viewMode === 'bar' && (
        <div>
          <h3 className="text-lg font-semibold mb-2">
            {selectedMetric.charAt(0).toUpperCase() + selectedMetric.slice(1).replace('_', ' ')} Comparison
          </h3>
          <Bar data={chartData} options={{
            responsive: true,
            plugins: {
              legend: {
                position: 'top',
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    return `${context.dataset.label}: ${context.parsed.y.toFixed(4)}`;
                  }
                }
              }
            },
            scales: {
              y: {
                min: 0,
                max: 1,
                title: {
                  display: true,
                  text: selectedMetric.charAt(0).toUpperCase() + selectedMetric.slice(1).replace('_', ' ')
                }
              }
            }
          }} />
        </div>
      )}
    </div>
  );
};

export default ModelPerformanceLog;
