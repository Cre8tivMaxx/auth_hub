import { useEffect, useState } from "react";

export default function Home() {
  const [context, setContext] = useState({});
  const [selectedSite, setSelectedSite] = useState(null);

  useEffect(() => {
    fetch("/api/method/auth_hub.www.home.get_context")
      .then(res => res.json())
      .then(data => setContext(data.message || {}))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className=" bg-dark-500 flex mt-6 justify-center px-6">
      <div className="w-full max-w-5xl bg-[#34495e] shadow-2xl rounded-xl px-6 py-3 mt-8">

        {/* Title */}
        <h1 className="text-2xl font-bold text-center mb-8">Sites</h1>

        {/* Sites Grid */}
        {!selectedSite && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2">
            {context.sites?.map(site => (
              <div
                key={site}
                onClick={() => setSelectedSite(site)}
                className="cursor-pointer py-4 rounded-xl shadow-md border text-center
                           hover:bg-gray-400 hover:border-dark-600 transition"
              >
                <h2 className="font-semibold text-md">{site}</h2>
              </div>
            ))}
          </div>
        )}

        {/* Selected Site */}
        {selectedSite && (
          <div className="space-y-4">

            {/* Selected Site Box */}
            <div className="flex justify-center">
              <div className=" flex gap-2 px-4 rounded-xl shadow-lg text-center w-50">
                <h2 className="text-md font-semibold text-white mt-2">
                  {selectedSite}
                </h2>
                <button
                  onClick={() => setSelectedSite(null)}
                  className="text-sm text-gray-400 bg-dark-600 font-semibold"
                >
                  Change site
                </button>
              </div>
            </div>

            {/* Installed Apps */}
            <div>
              <h3 className="text-xl font-bold mb-6 text-center">
                Installed Apps
              </h3>

              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
                {context.installed_apps?.map(app => (
                  <a
                    key={app}
                    href={`http://localhost:8000/app/${app}`}
                    target="_blank"
                    className="p-4 rounded-xl shadow-md border text-center text-gray-400 font-semibold
                               hover:bg-gray-400 hover:border-white hover:text-white hover:font-semibold transition"
                  >
                    {app}
                  </a>
                ))}
              </div>
            </div>

          </div>
        )}

      </div>
    </div>
  );
}