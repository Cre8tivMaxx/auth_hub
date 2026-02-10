import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ExternalLink, ChevronDown, LogIn } from "lucide-react";

export default function AppCard({ site, isOpen, onToggle }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="group relative flex flex-col rounded-xl border border-[muted-foreground] bg-subBackground transition-all shadow-xl glow-sm hover:border-buttonBackground pb-4"
    >
      {/* Header: Logo + Arrow */}
      <div
        onClick={() => onToggle(site.name)}
        className="flex items-center justify-between p-4 cursor-pointer"
      >
        {/* Logo */}
        <div className="h-12 w-12 flex items-center justify-center rounded-lg bg-logoBackground text-buttonBackground text-xl font-bold">
          {site.name[0].toUpperCase()}
        </div>

        {/* Arrow */}
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        </motion.div>
      </div>

      {/* Content */}
      <div className="px-4 space-y-2">
        {/* Site name */}
        <h3 className="text-base font-semibold text-textColor">
          {site.name}
        </h3>

        {/* Description */}
        <p className="text-sm text-muted-foreground">
          {site.description}
        </p>

        {/* Login button */}
        <div className="flex justify-end pt-2">
          <a
            href={site.login}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 rounded-xl bg-buttonBackground px-3 py-2 text-sm font-semibold text-logoColor hover:opacity-90 transition"
          >
            <LogIn className="h-3 w-3 mt-1" />
            Login
          </a>
        </div>
      </div>

      {/* Installed apps */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="border-t border-[muted-foreground] p-4 mt-4"
          >
            <div className="grid gap-2 grid-cols-2 md:grid-cols-3">
              {site.installed_apps.map((app) => (
                <a
                  key={app}
                  href={site.login}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 rounded-lg bg-inputBckground px-3 py-2 text-sm font-medium text-foreground hover:bg-gray-500 hover:text-textColor transition"
                >
                  {app}
                  <ExternalLink className="h-3 w-3" />
                </a>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}