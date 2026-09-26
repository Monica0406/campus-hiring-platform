import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient, { getErrorMessage } from '../../api/client';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';
import AlertMessage from '../../components/AlertMessage';

const StudentApplications = () => {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await apiClient.get('/applications/');
      if (res.data?.success) {
        setApplications(res.data.data);
      }
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to load applications.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold mb-1">My Applications</h2>
          <p className="text-muted mb-0">Track your recruitment progress across all applied drives</p>
        </div>
        <Link to="/drives" className="btn btn-outline-primary">
          <i className="bi bi-search me-1"></i> Browse More Drives
        </Link>
      </div>

      <AlertMessage type="danger" message={error} onClose={() => setError('')} />

      {loading ? (
        <LoadingSpinner message="Fetching your applications..." />
      ) : applications.length === 0 ? (
        <div className="card shadow-sm border-0 p-5 text-center">
          <div className="mb-3 text-muted">
            <i className="bi bi-file-earmark-x fs-1"></i>
          </div>
          <h4 className="fw-bold">No Applications Yet</h4>
          <p className="text-muted mb-4">
            You have not applied to any campus placement drives yet. Explore active drives and apply!
          </p>
          <div>
            <Link to="/drives" className="btn btn-primary px-4 fw-semibold">
              Browse Active Drives
            </Link>
          </div>
        </div>
      ) : (
        <div className="card shadow-sm border-0">
          <div className="card-body p-0">
            <div className="table-responsive">
              <table className="table table-hover align-middle mb-0">
                <thead className="table-light">
                  <tr>
                    <th>#</th>
                    <th>Company</th>
                    <th>Drive Title</th>
                    <th>Applied Date</th>
                    <th>Status</th>
                    <th className="text-end">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {applications.map((app, index) => (
                    <tr key={app.id}>
                      <td className="text-muted">{index + 1}</td>
                      <td>
                        <strong className="text-dark">{app.company_name}</strong>
                      </td>
                      <td>{app.drive_title}</td>
                      <td className="text-muted small">
                        {new Date(app.applied_date).toLocaleDateString()}
                      </td>
                      <td>
                        <StatusBadge status={app.status} />
                      </td>
                      <td className="text-end">
                        <Link
                          to={`/student/applications/${app.id}`}
                          className="btn btn-sm btn-outline-primary"
                        >
                          View Details <i className="bi bi-arrow-right ms-1"></i>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentApplications;
