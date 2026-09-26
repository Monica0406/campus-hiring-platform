import React from "react";
import { BrowserRouter, Link } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import AppRoutes from "./routes/AppRoutes";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="d-flex flex-column min-vh-100 bg-light">
          <Navbar />
          <main className="flex-grow-1">
            <AppRoutes />
          </main>
          <footer className="bg-white border-top py-4 mt-auto">
            <div className="container text-center text-muted small">
              <div className="d-flex flex-wrap justify-content-center gap-3 mb-2">
                <Link to="/" className="text-decoration-none text-muted">Home</Link>
                <span>&bull;</span>
                <Link to="/drives" className="text-decoration-none text-muted">Placement Drives</Link>
                <span>&bull;</span>
                <Link to="/login" className="text-decoration-none text-muted">Portal Login</Link>
                <span>&bull;</span>
                <span className="text-muted">Campus Hiring Platform &copy; 2026</span>
              </div>
              <p className="mb-0 text-secondary">
                Designed & Developed for College Placement & Training Cell. Medium Complexity Capstone Project.
              </p>
            </div>
          </footer>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}
