import React from "react";
import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="container py-5 text-center my-auto">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card shadow-sm border-0 p-5">
            <h1 className="display-1 fw-bold text-primary">404</h1>
            <h4 className="fw-semibold mb-3">Page Not Found</h4>
            <p className="text-muted mb-4">
              The page you are looking for might have been removed, had its name changed,
              or is temporarily unavailable.
            </p>
            <div>
              <Link to="/" className="btn btn-primary px-4">
                <i className="bi bi-house-door me-2"></i>Back to Home
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
