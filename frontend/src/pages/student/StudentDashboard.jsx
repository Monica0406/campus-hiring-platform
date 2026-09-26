import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient, { getErrorMessage } from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import StatCard from '../../components/StatCard';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';
import AlertMessage from '../../components/AlertMessage';

const StudentDashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [stats, setStats] = useState({
    activeDrives: 0,
    applications: 0,
    interviews: 0,
    offers: 0,
  });

  const [recentApplications, setRecentApplications] = useState([]);
  const [upcomingInterviews, setUpcomingInterviews] = useState([]);
  const [pendingOffers, setPendingOffers] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError('');
    try {
      const [drivesRes, appsRes, interviewsRes, offersRes] = await Promise.all([
        apiClient.get('/drives/'),
        apiClient.get('/applications/'),
        apiClient.get('/interviews/'),
        apiClient.get('/offers/'),
      ]);

      const drivesData = drivesRes.data?.data || [];
      const appsData = appsRes.data?.data || [];
      const interviewsData = interviewsRes.data?.data || [];
      const offersData = offersRes.data?.data || [];

      setStats({
        activeDrives: drivesData.length,
        applications: appsData.length,
        interviews: interviewsData.length,
        offers: offersData.length,
      });

      setRecentApplications(appsData.slice(0, 5));
      setUpcomingInterviews(interviewsData.slice(0, 3));
      setPendingOffers(offersData.filter((o) => o.status === 'PENDING'));
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to load dashboard data.'));
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container py-5">
        <LoadingSpinner message="Loading your dashboard..." />
      </div>
    );
  }

  const studentName = user?.profile?.name || 'Student';

  return (
    <div className="container py-4">
      {/* Welcome Banner */}
      <div className="card shadow-sm border-0 bg-primary text-white mb-4">
        <div className="card-body p-4 p-md-5">
          <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
            <div>
              <h2 className="fw-bold mb-1">Welcome, {studentName}!</h2>
              <p className="mb-0 opacity-90">
                Department: <strong>{user?.profile?.department || 'N/A'}</strong> | CGPA: <strong>{user?.profile?.cgpa || 'N/A'}</strong> | College: <strong>{user?.profile?.college || 'N/A'}</strong>
              </p>
            </div>
            <div className="d-flex gap-2">
              <Link to="/drives" className="btn btn-warning fw-semibold">
                <i className="bi bi-search me-1"></i> Browse Drives
              </Link>
              <Link to="/student/profile" className="btn btn-outline-light">
                <i className="bi bi-person-gear me-1"></i> Edit Profile
              </Link>
            </div>
          </div>
        </div>
      </div>

      <AlertMessage type="danger" message={error} onClose={() => setError('')} />

      {/* Pending Offers Notification Banner */}
      {pendingOffers.length > 0 && (
        <div className="alert alert-warning shadow-sm border-warning d-flex align-items-center justify-content-between mb-4">
          <div className="d-flex align-items-center">
            <i className="bi bi-trophy-fill fs-3 me-3 text-warning"></i>
            <div>
              <strong className="fs-6">Action Required: You have {pendingOffers.length} pending job offer(s)!</strong>
              <div className="small text-muted">Review the compensation package and submit your acceptance or rejection.</div>
            </div>
          </div>
          <Link to="/student/offers" className="btn btn-warning fw-semibold btn-sm">
            View Offers
          </Link>
        </div>
      )}

      {/* Stat Cards */}
      <div className="row g-3 mb-4">
        <div className="col-sm-6 col-lg-3">
          <StatCard
            title="Active Drives"
            value={stats.activeDrives}
            icon="megaphone"
            color="primary"
            linkTo="/drives"
            linkText="Explore drives"
          />
        </div>
        <div className="col-sm-6 col-lg-3">
          <StatCard
            title="My Applications"
            value={stats.applications}
            icon="file-earmark-text"
            color="info"
            linkTo="/student/applications"
            linkText="Track status"
          />
        </div>
        <div className="col-sm-6 col-lg-3">
          <StatCard
            title="Scheduled Interviews"
            value={stats.interviews}
            icon="calendar-check"
            color="success"
            linkTo="/student/interviews"
            linkText="View schedule"
          />
        </div>
        <div className="col-sm-6 col-lg-3">
          <StatCard
            title="Job Offers"
            value={stats.offers}
            icon="award"
            color="warning"
            linkTo="/student/offers"
            linkText="Manage offers"
          />
        </div>
      </div>

      {/* Recent Applications & Upcoming Interviews */}
      <div className="row g-4">
        {/* Recent Applications */}
        <div className="col-lg-8">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
              <h5 className="fw-bold mb-0">Recent Applications</h5>
              <Link to="/student/applications" className="btn btn-sm btn-outline-primary">
                View All
              </Link>
            </div>
            <div className="card-body p-0">
              {recentApplications.length === 0 ? (
                <div className="p-4 text-center text-muted">
                  <i className="bi bi-inbox fs-2 mb-2 d-block"></i>
                  You haven't applied to any drives yet.
                  <div className="mt-2">
                    <Link to="/drives" className="btn btn-sm btn-primary">
                      Explore Open Drives
                    </Link>
                  </div>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover align-middle mb-0">
                    <thead className="table-light">
                      <tr>
                        <th>Company</th>
                        <th>Drive Title</th>
                        <th>Applied On</th>
                        <th>Current Status</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentApplications.map((app) => (
                        <tr key={app.id}>
                          <td className="fw-semibold">{app.company_name}</td>
                          <td>{app.drive_title}</td>
                          <td className="text-muted small">
                            {new Date(app.applied_date).toLocaleDateString()}
                          </td>
                          <td>
                            <StatusBadge status={app.status} />
                          </td>
                          <td>
                            <Link
                              to={`/student/applications/${app.id}`}
                              className="btn btn-sm btn-outline-secondary"
                            >
                              Details
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

        {/* Upcoming Interviews / Highlights */}
        <div className="col-lg-4">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
              <h5 className="fw-bold mb-0">Upcoming Interviews</h5>
              <Link to="/student/interviews" className="btn btn-sm btn-outline-primary">
                All
              </Link>
            </div>
            <div className="card-body p-3">
              {upcomingInterviews.length === 0 ? (
                <div className="p-4 text-center text-muted small">
                  <i className="bi bi-calendar-x fs-2 mb-2 d-block"></i>
                  No interviews scheduled at the moment.
                </div>
              ) : (
                <div className="d-flex flex-column gap-3">
                  {upcomingInterviews.map((item) => (
                    <div key={item.id} className="p-3 rounded-2 border bg-light">
                      <div className="d-flex justify-content-between align-items-start mb-1">
                        <strong className="text-dark">{item.company_name}</strong>
                        <StatusBadge status={item.status} />
                      </div>
                      <div className="small text-muted mb-2">{item.drive_title}</div>
                      <div className="d-flex justify-content-between small text-muted">
                        <span><i className="bi bi-camera-video me-1"></i> {item.mode}</span>
                        <span>
                          <i className="bi bi-clock me-1"></i>
                          {new Date(item.interview_date).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
