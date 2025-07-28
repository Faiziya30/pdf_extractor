import { useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { Sparkles, Brain, FileText } from 'lucide-react';

const Results = () => {
  const [persona, setPersona] = useState('');
  const [job, setJob] = useState('');
  const [insights, setInsights] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchInsights = async () => {
    if (!persona || !job) return toast.error('Please fill out both fields!');
    setIsLoading(true);
    try {
      const res = await axios.post('http://localhost:5000/insights', { persona, job });
      setInsights(res.data);
      toast.success('Insights loaded!');
    } catch (err) {
      console.error(err);
      toast.error('Error fetching insights');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Input Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <input
          type="text"
          placeholder="Persona (e.g. Chemistry Student)"
          value={persona}
          onChange={(e) => setPersona(e.target.value)}
          className="p-3 rounded-lg border border-pink-400 dark:border-pink-500 focus:outline-none focus:ring-2 focus:ring-pink-400 bg-white dark:bg-gray-900 dark:text-white shadow-sm"
        />
        <input
          type="text"
          placeholder="Job to be done (e.g. Summarize Key Reactions)"
          value={job}
          onChange={(e) => setJob(e.target.value)}
          className="p-3 rounded-lg border border-pink-400 dark:border-pink-500 focus:outline-none focus:ring-2 focus:ring-pink-400 bg-white dark:bg-gray-900 dark:text-white shadow-sm"
        />
      </div>

      <div className="text-center mb-10">
        <button
          onClick={fetchInsights}
          disabled={isLoading}
          className={`px-8 py-3 rounded-full font-semibold transition-all duration-300
            ${persona && job
              ? 'bg-gradient-to-r from-pink-500 to-red-500 text-white hover:scale-105 shadow-lg'
              : 'bg-gray-300 dark:bg-gray-700 text-gray-500 cursor-not-allowed'}`}
        >
          {isLoading ? 'Processing...' : '💡 Get Insights'}
        </button>
      </div>

      {/* Insight Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {insights.map((item, idx) => (
          <div
            key={idx}
            className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md hover:shadow-pink-400 transition-all duration-300 border-l-4 border-pink-400 dark:border-pink-500"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2 text-pink-500 dark:text-pink-300 font-semibold text-lg">
                <Sparkles size={20} />
                {item.title}
              </div>
              <span className="text-sm bg-gradient-to-r from-red-400 to-pink-500 text-white px-3 py-1 rounded-full shadow">
                Score: {(item.score * 100).toFixed(0)}%
              </span>
            </div>
            <p className="text-gray-700 dark:text-gray-300 mb-2">
              <Brain className="inline-block mr-2 text-pink-400" size={16} />
              {item.section}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 flex items-center">
              <FileText className="mr-1" size={14} />
              Page {item.page}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Results;
