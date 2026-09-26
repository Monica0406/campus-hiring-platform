import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient, { getErrorMessage } from '../api/client';
import { useAuth } from '../context/AuthContext';

const Home = () => {
  const { isAuthenticated, role } = useAuth();
  const [drives, setDrives] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDrives = async () => {
      try {
        const response = await apiClient.get('/drives/');
        if (response.data?.success) {
          setDrives(response.data.data.slice(0, 3));
        }
      } catch (err) {
        console.warn('Could not fetch preview drives', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDrives();
  }, []);

  return (
    <div>
      {/* Hero Section */}
      <section className="bg-primary text-white py-5 text-center">
        <div className="container py-4">
          <div className="row justify-content-center">
            <div className="col-lg-8">
              <span className="badge bg-warning text-dark px-3 py-2 text-uppercase mb-3 fw-semibold">
                Campus Recruitment 2026
              </span>
              <h1 className="display-4 fw-bold mb-3">
                Connecting Ambitious Students with Top Companies
              </h1>
              <p className="lead mb-4 opacity-90">
                A unified platform for placement drives, automated eligibility screening, interview coordination, and seamless job offer management.
              </p>
              <div className="d-flex justify-content-center gap-3 flex-wrap">
                <Link to="/drives" className="btn btn-warning btn-lg px-4 fw-semibold">
                  <i className="bi bi-briefcase me-2"></i> Browse Drives
                </Link>
                {!isAuthenticated ? (
                  <>
                    <Link to="/register/student" className="btn btn-outline-light btn-lg px-4 fw-semibold">
                      <i className="bi bi-mortarboard me-2"></i> Join as Student
                    </Link>
                    <Link to="/register/company" className="btn btn-light btn-lg px-4 text-primary fw-semibold">
                      <i className="bi bi-building me-2"></i> Hire as Company
                    </Link>
                  </>
                ) : (
                  <Link
                    to={role === 'STUDENT' ? '/student/dashboard' : '/company/dashboard'}
                    className="btn btn-light btn-lg px-4 text-primary fw-semibold"
                  >
                    <i className="bi bi-speedometer2 me-2"></i> Go to Dashboard
                  </Link>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Pillars */}
      <section className="py-5 bg-light">
        <div className="container py-3">
          <div className="text-center mb-5">
            <h2 className="fw-bold">Designed for High-Impact Campus Placements</h2>
            <p className="text-muted">End-to-end recruitment process managed with complete transparency</p>
          </div>

          <div className="row g-4">
            <div className="col-md-4">
              <div className="card h-100 border-0 shadow-sm p-3">
                <div className="card-body">
                  <div className="p-3 bg-primary bg-opacity-10 text-primary rounded-3 d-inline-block mb-3">
                    <i className="bi bi-funnel fs-2"></i>
                  </div>
                  <h5 className="card-title fw-bold">Automated Eligibility</h5>
                  <p className="card-text text-muted">
                    Smart validation checks CGPA criteria and eligible academic branches instantly before applications are accepted.
                  </p>
                </div>
              </div>
            </div>

            <div className="col-md-4">
              <div className="card h-100 border-0 shadow-sm p-3">
                <div className="card-body">
                  <div className="p-3 bg-success bg-opacity-10 text-success rounded-3 d-inline-block mb-3">
                    <i className="bi bi-calendar-event fs-2"></i>
                  </div>
                  <h5 className="card-title fw-bold">Recruitment Pipeline</h5>
                  <p className="card-text text-muted">
                    Clear stage-by-stage progression: from Shortlisted to Interview Scheduled, Selected, and Extended Offer.
                  </p>
                </div>
              </div>
            </div>

            <div className="col-md-4">
              <div className="card h-100 border-0 shadow-sm p-3">
                <div className="card-body">
                  <div className="p-3 bg-warning bg-opacity-10 text-warning rounded-3 d-inline-block mb-3">
                    <i className="bi bi-patch-check fs-2"></i>
                  </div>
                  <h5 className="card-title fw-bold">Instant Offer Responses</h5>
                  <p className="card-text text-muted">
                    Students can review offer packages and respond with one-click acceptance or rejection, keeping companies informed.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Latest Drives Preview */}
      <section className="py-5">
        <div className="container py-3">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h2 className="fw-bold mb-1">Featured Active Drives</h2>
              <p className="text-muted mb-0">Upcoming placement opportunities open for applications</p>
            </div>
            <Link to="/drives" className="btn btn-outline-primary fw-semibold">
              View All Drives <i className="bi bi-arrow-right"></i>
            </Link>
          </div>

          {loading ? (
            <div className="text-center py-4">
              <div className="spinner-border text-primary" role="status"></div>
            </div>
          ) : drives.length === 0 ? (
            <div className="alert alert-info text-center py-4">
              <i className="bi bi-info-circle me-2"></i> No active drives right now. Check back soon!
            </div>
          ) : (
            <div className="row g-4">
              {drives.map((drive) => (
                <div key={drive.id} className="col-md-4">
                  <div className="card h-100 shadow-sm border-0">
                    <div className="card-body d-flex flex-column">
                      <div className="d-flex justify-content-between align-items-start mb-2">
                        <span className="badge bg-light text-primary border">{drive.company_name}</span>
                        <span className="badge bg-success bg-opacity-10 text-success">Active</span>
                      </div>
                      <h5 className="card-title fw-bold mb-2">{drive.title}</h5>
                      <p className="card-text text-muted small flex-grow-1">
                        {drive.description?.length > 110
                          ? `${drive.description.substring(0, 110)}...`
                          : drive.description}
                      </p>
                      <div className="border-top pt-3 mt-2 text-muted small">
                        <div className="d-flex justify-content-between mb-1">
                          <span><i className="bi bi-award me-1"></i> Min CGPA:</span>
                          <strong className="text-dark">{drive.min_cgpa}</strong>
                        </div>
                        <div className="d-flex justify-content-between mb-2">
                          <span><i className="bi bi-calendar3 me-1"></i> Drive Date:</span>
                          <strong className="text-dark">{drive.drive_date}</strong>
                        </div>
                        <Link to={`/drives/${drive.id}`} className="btn btn-primary w-100 btn-sm mt-2">
                          View Details & Apply
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default Home;
