import { Disclosure } from "@headlessui/react";
import { Link, useLocation } from "react-router-dom";
import { LogOut, Home, User } from "lucide-react";
import ThemeToggle from "./ThemeToggle";
import { useAuth } from "../Context/AuthContext";

export default function NavBar() {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navItems = [
    { name: "Home", path: "/", icon: Home },
    { name: "Profile", path: "/profile", icon: User },
  ];

  return (
    <Disclosure
      as="nav"
      className="sticky top-0 z-50 bg-subBackground backdrop-blur border-b border-[muted-foreground]"
    >
      <div className="mx-auto max-w-7xl px-4">
        <div className="flex h-16 items-center justify-between">

          {/* LEFT – Logo */}
          <Link to="/" className="flex items-center gap-1 mt-1">
            <div className="h-6 w-6 flex items-center justify-center rounded-lg bg-buttonBackground text-logoColor text-md font-semibold">
              L
            </div>
            <span className="text-xl font-bold text-foreground">
              LINK
            </span>
          </Link>

          {/* MIDDLE – Nav links */}
          <div className="flex gap-2">
            {navItems.map(({ name, path, icon: Icon }) => (
              <Link
                key={path}
                to={path}
                className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition
                  ${location.pathname === path
                    ? "bg-inputBckground text-foreground"
                    : "text-muted-foreground"
                  }`}
              >
                <Icon className="h-4 w-4" />
                {name}
              </Link>
            ))}
          </div>

          {/* RIGHT – Theme + Logout*/}
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <button
              onClick={logout}
              className="p-2 text-muted-foreground bg-transparent hover:bg-foreground"
              aria-label="Logout"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>

        </div>
      </div>
    </Disclosure>
  );
}