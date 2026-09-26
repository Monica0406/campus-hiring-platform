import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient, { getErrorMessage } from '../../api/client';
import LoadingSpinner from '../../components/LoadingSpinner';
import AlertMessage from '../../components/AlertMessage';

const CompanyDrives = () => {
  const [drives, setDrives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    fetchMyDrives();
  }, []);

  const fetchMyDrives = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await apiClient.get('/drives/?mine=true');
      if (res.data?.success) {
        setDrives(res.data.data);
      }
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to load your drives.'));
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (driveId, title) => {
    if (!window.confirm(`Are you sure you want to delete the drive "${title}"? This cannot be undone.`)) {
      return;
    }

    setDeletingId(driveId);
    setError('');
    setSuccessMsg('');

    try {
      const res = await apiClient.delete(`/drives/${driveId}/`);
      if (res.data?.success) {
        setDrives((prev) => prev.filter((d) => d.id !== driveId));
        setSuccessMsg(`Drive "${title}" was successfully deleted.`);
      }
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to delete drive.'));
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="container py-4">
      <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4 gap-3">
        <div>
          <h2 className="fw-bold mb-1">Manage Placement Drives</h2>
          <p className="text-muted mb-0">Create, edit, and review applicants across your placement drives</p>
        </div>
        <Link to="/company/drives/create" className="btn btn-primary fw-semibold">
          <i className="bi bi-plus-circle me-1"></i> Post New Drive
        </Link>
      </div>

      <AlertMessage type="success" message={successMsg} onClose={() => setSuccessMsg('')} />
      <AlertMessage type="danger" message={error} onClose={() => setError('')} />

      {loading ? (
        <LoadingSpinner message="Fetching your placement drives..." />
      ) : drives.length === 0 ? (
        <div className="card shadow-sm border-0 p-5 text-center">
          <div className="mb-3 text-muted">
            <i className="bi bi-building fs-1"></i>
          </div>
          <h4 className="fw-bold">No Drives Posted Yet</h4>
          <p className="text-muted mb-4">
            You have not posted any placement drives yet. Create a drive to start receiving applications from qualified candidates.
          </p>
          <div>
            <Link to="/company/drives/create" className="btn btn-primary px-4 fw-semibold">
              <i className="bi bi-plus-lg me-1"></i> Create Your First Drive
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
                    <th>Drive Title</th>
                    <th>Drive Date</th>
                    <th>Min CGPA</th>
                    <th>Allowed Branches</th>
                    <th>Status</th>
                    <th className="text-end">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {drives.map((drive) => (
                    <tr key={drive.id}>
                      <td>
                        <div className="fw-bold text-dark">{drive.title}</div>
                        <div className="small text-muted text-truncate" style={{ maxWidth: '280px' }}>
                          {drive.description}
                        </div>
                      </td>
                      <td className="text-muted small">{drive.drive_date}</td>
                      <td>
                        <span className="badge bg-light text-dark border">{drive.min_cgpa}</span>
                      </td>
                      <td className="small text-muted text-truncate" style={{ maxWidth: '160px' }}>
                        {drive.allowed_departments}
                      </td>
                      <td>
                        <span className={`badge ${drive.is_active ? 'bg-success' : 'bg-secondary'}`}>
                          {drive.is_active ? 'Active' : 'Closed'}
                        </span>
                      </td>
                      <td className="text-end">
                        <div className="btn-group btn-group-sm">
                          <Link
                            to={`/company/drives/${drive.id}/applicants`}
                            className="btn btn-outline-primary"
                            title="View Applicants"
                          >
                            <i className="bi bi-people me-1"></i> Applicants
                          </Link>
                          <Link
                            to={`/company/drives/${drive.id}/edit`}
                            className="btn btn-outline-secondary"
                            title="Edit Drive"
                          >
                            <i className="bi bi-pencil"></i>
                          </Link>
                          <button
                            className="btn btn-outline-danger"
                            title="Delete Drive"
                            onClick={() => handleDelete(drive.id, drive.title)}
                            disabled={deletingId === drive.id}
                          >
                            {deletingId === drive.id ? (
                              <span className="spinner-border spinner-border-sm"></span>
                            ) : (
                              <i className="bi bi-trash"></i>
                            )}
                          </button>
                        </div>
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

export default CompanyDrives;
