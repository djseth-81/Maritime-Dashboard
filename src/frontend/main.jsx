import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider, Outlet } from "react-router-dom"

import App from "./App.jsx";
import ErrorPage from "./components/ErrorPage/ErrorPage.jsx";
import Auth from "./components/Auth/Auth.jsx"
import ProtectedRoute from "./components/Auth/ProtectedRoute/ProtectedRoute.jsx";

import "./index.css";

const Layout = () => {
  return (
    <>
      <Outlet />
    </>
  );
};

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    errorElement: <ErrorPage />,
  },
]);

createRoot(document.getElementById("root")).render(
    <RouterProvider router={router} />
);
