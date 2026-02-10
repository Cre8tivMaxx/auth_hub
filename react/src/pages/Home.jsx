import { useEffect, useState } from "react";
import AppCard from "../Components/AppCard";

export default function Home() {
  const [context, setContext] = useState({});
  const [openSite, setOpenSite] = useState(null);

  useEffect(() => {
    fetch("/api/method/auth_hub.www.home.get_context")
      .then((res) => res.json())
      .then((data) => setContext(data.message || {}))
      .catch((err) => console.error(err));
  }, []);

  const sitesData = context.sites?.map((site) => ({
    name: site,
    description: context.Description,
    installed_apps: context.installed_apps || [],
    login: context.login,
  }));

  const handleToggle = (name) => {
    setOpenSite((prev) => (prev === name ? null : name));
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center py-8">

      <h1 className="text-2xl font-bold text-center text-foreground mb-6">
        Access all your connected apps from one place
      </h1>


      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 w-full max-w-6xl px-4">
        {sitesData?.map((site) => (
          <AppCard
            key={site.name}
            site={site}
            isOpen={openSite === site.name}
            onToggle={handleToggle}
          />
        ))}
      </div>
    </div>
  );
}