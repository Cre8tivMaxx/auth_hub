// App.jsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./Components/Layout"
import Home from "./pages/Home.jsx";
import Profile from "./pages/Profile.jsx"


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout/>}>
          <Route path="/" element={<Home />} />
          <Route path="/profile" element={<Profile />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;