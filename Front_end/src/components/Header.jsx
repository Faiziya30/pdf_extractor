// import React from 'react';
// import { Link, useLocation } from 'react-router-dom';
// import ToggleTheme from './ToggleTheme';

// const Header = () => {
//   const location = useLocation();

//   const navLinkStyle = (path) =>
//     `transition-all px-4 py-2 rounded-full text-sm font-semibold
//     ${location.pathname === path
//       ? 'bg-gradient-to-r from-red-500 to-pink-500 text-white shadow-lg scale-105'
//       : 'text-gray-700 dark:text-gray-200 hover:text-red-500 dark:hover:text-pink-400'}
//     `;

//   return (
//     <header className="sticky top-0 z-50 backdrop-blur-md bg-white/70 dark:bg-black/40 shadow-md border-b border-gray-200 dark:border-gray-800">
//       <div className="max-w-7xl mx-auto px-6 py-3 flex justify-between items-center">
//         <Link to="/" className="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-red-600 to-pink-500 dark:from-red-300 dark:to-pink-300">
//           SmartPDF
//         </Link>
//         <nav className="flex space-x-4 items-center">
//           <Link to="/" className={navLinkStyle('/')}>Home</Link>
//           <Link to="/upload" className={navLinkStyle('/upload')}>Upload</Link>
//           <Link to="/results" className={navLinkStyle('/results')}>Results</Link>
//           <ToggleTheme />
//         </nav>
//       </div>
//     </header>
//   );
// };

// export default Header;

import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import ToggleTheme from './ToggleTheme';
import { Menu, X } from 'lucide-react';

const Header = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const navLinkStyle = (path) =>
    `relative px-4 py-2 text-sm font-medium transition-all duration-300 ease-in-out
     ${location.pathname === path
       ? 'text-white bg-gradient-to-r from-red-500 to-pink-500 rounded-full shadow-md scale-105'
       : 'text-gray-800 dark:text-gray-200 hover:text-pink-500'}
     after:absolute after:-bottom-1 after:left-0 after:h-0.5 after:w-0 hover:after:w-full after:bg-pink-500 after:transition-all after:duration-300
    `;

  const navItems = (
    <>
      <Link to="/" className={navLinkStyle('/')}>Home</Link>
      <Link to="/upload" className={navLinkStyle('/upload')}>Upload</Link>
      <Link to="/results" className={navLinkStyle('/results')}>Results</Link>
    </>
  );

  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-white/70 dark:bg-black/40 shadow-md border-b border-gray-200 dark:border-gray-800">
      <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
        <Link
          to="/"
          className="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-red-600 to-pink-500 dark:from-red-300 dark:to-pink-300"
        >
          SmartPDF
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:flex space-x-4 items-center">
          {navItems}
          <ToggleTheme />
        </nav>

        {/* Mobile Hamburger */}
        <div className="md:hidden flex items-center space-x-2">
          <ToggleTheme />
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="text-gray-700 dark:text-white focus:outline-none"
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Nav Dropdown */}
      {isOpen && (
        <div className="md:hidden bg-white dark:bg-black shadow-lg py-4 px-6 flex flex-col space-y-3 text-center">
          {navItems}
        </div>
      )}
    </header>
  );
};

export default Header;

