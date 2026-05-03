import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { useThemeStore } from '../store/useThemeStore';
import { Menu, Moon, Sun, Radar, Network, MapPin } from 'lucide-react';
import RSSPanel from './RSSPanel';
import ChatWidget from './ChatWidget';
import AnomalyPanel from './AnomalyPanel';
import { Toaster } from 'sonner';

export default function Layout() {
  const { sidebarOpen, toggleSidebar } = useAppStore();
  const { theme, toggleTheme } = useThemeStore();
  const location = useLocation();

  const navLink = (to, icon, label) => {
    const active = location.pathname === to;
    return (
      <Link
        to={to}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
          active
            ? 'text-primary bg-primary/10'
            : 'text-muted-foreground hover:text-foreground hover:bg-accent'
        }`}
      >
        {icon}
        <span className="hidden sm:block">{label}</span>
      </Link>
    );
  };

  return (
    <div className="min-h-screen flex flex-col bg-background overflow-x-hidden">
      <Toaster richColors position="top-right" />
      {/* Topbar */}
      <header className="h-16 border-b border-border bg-card flex items-center justify-between px-4 sticky top-0 z-30">
        <div className="flex items-center space-x-4 min-w-0">
          <button onClick={toggleSidebar} className="p-2 hover:bg-accent rounded-md text-foreground transition-colors flex-shrink-0">
            <Menu className="w-5 h-5" />
          </button>
          <Link to="/" className="flex items-center space-x-2.5 min-w-0">
            <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-1.5 rounded-lg shadow-sm flex-shrink-0">
              <Radar className="w-5 h-5 text-white" />
            </div>
            <div className="flex items-center gap-2 min-w-0">
              <span className="font-extrabold text-xl tracking-tight hidden sm:block bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent truncate">
                Synapse
              </span>
            </div>
          </Link>
        </div>

        <div className="flex items-center space-x-1 sm:space-x-2 flex-shrink-0">
          {navLink('/graph', <Network className="w-4 h-4" />, 'Sinyal Graf')}
          {navLink('/timeline', <MapPin className="w-4 h-4" />, 'Harita & Zaman')}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-full hover:bg-accent text-foreground"
          >
            {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Mobile backdrop */}
        {sidebarOpen && (
          <button
            aria-label="Kapat"
            onClick={toggleSidebar}
            className="md:hidden fixed inset-0 z-10 bg-black/30"
          />
        )}

        <aside
          className={`
            ${sidebarOpen ? 'w-72 translate-x-0' : 'w-0 -translate-x-full'}
            md:translate-x-0 md:w-72
            transition-all duration-300 ease-in-out border-r border-border bg-card
            overflow-y-auto flex-shrink-0 z-20
            fixed md:static top-16 bottom-0 left-0
          `}
        >
          <div className="p-4 flex flex-col space-y-6 w-72">
            <RSSPanel />
            <AnomalyPanel />
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto overflow-x-hidden bg-background p-4 md:p-8 min-w-0">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>

      <ChatWidget />
    </div>
  );
}
