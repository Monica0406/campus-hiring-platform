import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient, { getErrorMessage } from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import StatCard from '../../components/StatCard';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';
import AlertMessage from '../../components/AlertMessage';

const CompanyDashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [stats, setStats] = useState({
    drives: 0,
    applicants: 0,
    interviews: 0,
    offers: 0,
  });

  const [drives, setDrives] = useState([]);
  const [recentApplications, setRecentApplications] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError('');
    try {
      const [drivesRes, appsRes, interviewsRes, offersRes] = await Promise.all([
        apiClient.get('/drives/?mine=true'),
        apiClient.get('/applications/'),
        apiClient.get('/interviews/'),
        apiClient.get('/offers/'),
      ]);

      const drivesData = drivesRes.data?.data || [];
      const appsData = appsRes.data?.data || [];
      const interviewsData = interviewsRes.data?.data || [];
      const offersData = offersRes.data?.data || [];

      setStats({
        drives: drivesData.length,
        applicants: appsData.length,
        interviews: interviewsData.length,
        offers: offersData.length,
      });

      setDrives(drivesData.slice(0, 5));
      setRecentApplications(appsData.slice(0, 5));
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to load company dashboard.'));
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container py-5">
        <LoadingSpinner message="Loading recruiter dashboard..." />
      </div>
    );
  }

  const companyName = user?.profile?.company_name || 'Recruiter';

  return (
    <div className="container py-4">
      {/* Banner */}
      <div className="card shadow-sm border-0 bg-primary text-white mb-4">
        <div className="card-body p-4 p-md-5">
          <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
            <div>
              <span className="badge bg-light text-primary mb-2 text-uppercase fw-semibold">
                Company Portal
              </span>
              <h2 className="fw-bold mb-1">{companyName}</h2>
              <p className="mb-0 opacity-90">
                Location: <strong>{user?.profile?.location || 'N/A'}</strong> | Email: <strong>{user?.email}</strong>
              </p>
            </div>
            <div className="d-flex gap-2">
              <Link to="/company/drives/create" className="btn btn-warning fw-semibold">
                <i className="bi bi-plus-circle me-1"></i> Post New Drive
              </Link>
              <Link to="/company/profile" className="btn btn-outline-light">
                <i className="bi bi-gear me-1"></i> Settings
              </Link>
            </div>
          </div>
        </div>
      </div>

      <AlertMessage type="danger" message={error} onClose={() => setError('')} />

      {/* KPI Cards */}
      <div className="row g-3 mb-4">
        <div className="col-sm-6 col-lg-3">
          <StatCard
            title="My Drives"
            value={stats.drives}
            icon="building"
            color="primary"
            linkTo="/company/drives"
            linkText="Manage drives"
          />
        </div>
        <div className="col-sm-6 col-lg-3">
          <StatCard
            title="Total Applicants"
            value={stats.applicants}
            icon="people"
            color="info"
            linkTo="/company/drives"
            linkText="Review candidates"
          />
        </div>
        <div className="col-sm-6 col-lg-3">
          <StatCard
            title="Scheduled Interviews"
            value={stats.interviews}
            icon="calendar-check"
            color="success"
            linkTo="/company/interviews"
            linkText="Interview list"
          />
        </div>
        <div className="col-sm-6 col-lg-3">
          <StatCard
            title="Extended Offers"
            value={stats.offers}
            icon="envelope-paper"
            color="warning"
            linkTo="/company/offers"
            linkText="Track offers"
          />
        </div>
      </div>

      {/* Tables: Active Drives & Recent Applicants */}
      <div className="row g-4">
        {/* Drives Overview */}
        <div className="col-lg-6">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
              <h5 className="fw-bold mb-0">Placement Drives</h5>
              <Link to="/company/drives" className="btn btn-sm btn-outline-primary">
                View All
              </Link>
            </div>
            <div className="card-body p-0">
              {drives.length === 0 ? (
                <div className="p-4 text-center text-muted">
                  <i className="bi bi-briefcase fs-2 mb-2 d-block"></i>
                  No placement drives created yet.
                  <div className="mt-2">
                    <Link to="/company/drives/create" className="btn btn-sm btn-primary">
                      Create Your First Drive
                    </Link>
                  </div>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover align-middle mb-0">
                    <thead className="table-light">
                      <tr>
                        <th>Title</th>
                        <th>Drive Date</th>
                        <th>Status</th>
                        <th className="text-end">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {drives.map((drive) => (
                        <tr key={drive.id}>
                          <td className="fw-semibold text-dark">{drive.title}</td>
                          <td className="text-muted small">{drive.drive_date}</td>
                          <td>
                            <span className={`badge ${drive.is_active ? 'bg-success' : 'bg-secondary'}`}>
                              {drive.is_active ? 'Active' : 'Closed'}
                            </span>
                          </td>
                          <td className="text-end">
                            <Link
                              to={`/company/drives/${drive.id}/applicants`}
                              className="btn btn-sm btn-outline-primary me-1"
                            >
                              Applicants
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Recent Applicants */}
        <div className="col-lg-6">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
              <h5 className="fw-bold mb-0">Recent Candidate Applications</h5>
            </div>
            <div className="card-body p-0">
              {recentApplications.length === 0 ? (
                <div className="p-4 text-center text-muted">
                  <i className="bi bi-person-x fs-2 mb-2 d-block"></i>
                  No applicants received yet.
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover align-middle mb-0">
                    <thead className="table-light">
                      <tr>
                        <th>Candidate</th>
                        <th>Dept / CGPA</th>
                        <th>Status</th>
                        <th className="text-end">Manage</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentApplications.map((app) => (
                        <tr key={app.id}>
                          <td>
                            <div className="fw-semibold text-dark">{app.student_name}</div>
                            <div className="small text-muted">{app.drive_title}</div>
                          </td>
                          <td className="small">
                            {app.student_department} ({app.student_cgpa})
                          </td>
                          <td>
                            <StatusBadge status={app.status} />
                          </td>
                          <td className="text-end">
                            <Link
                              to={`/company/applications/${app.id}`}
                              className="btn btn-sm btn-outline-secondary"
                            >
                              Review
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompanyDashboard;
