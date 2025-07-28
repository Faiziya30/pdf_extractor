import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const Home = () => (
  <motion.div
    className="min-h-screen flex flex-col justify-center items-center bg-gradient-to-br from-red-100 via-white to-red-200 dark:from-gray-900 dark:via-gray-800 dark:to-black text-center px-4"
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
  >
    <div className="backdrop-blur-xl bg-white/60 dark:bg-white/10 shadow-xl rounded-3xl p-10 max-w-2xl">
      <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-red-600 to-pink-500 dark:from-red-400 dark:to-pink-300 mb-4">
        Smart PDF Insight
      </h1>
      <p className="text-lg text-gray-700 dark:text-gray-300 mb-6 leading-relaxed">
        Transform boring PDFs into an intelligent, interactive experience.
        Connect the dots, uncover insights, and impress like a pro.
      </p>
      <div className="flex justify-center gap-6">
        <Link
          to="/upload"
          className="px-6 py-3 bg-gradient-to-r from-pink-500 to-red-500 text-white font-semibold rounded-full shadow-lg hover:scale-105 transition-transform duration-300"
        >
          📤 Upload PDF
        </Link>
        <Link
          to="/results"
          className="px-6 py-3 bg-gradient-to-r from-gray-800 to-gray-900 text-white font-semibold rounded-full shadow-lg hover:scale-105 transition-transform duration-300"
        >
          📊 View Insights
        </Link>
      </div>
    </div>
  </motion.div>
);

export default Home;
