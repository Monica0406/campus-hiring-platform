import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import apiClient, { getErrorMessage } from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import LoadingSpinner from '../../components/LoadingSpinner';
import AlertMessage from '../../components/AlertMessage';

const DriveDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, role, user } = useAuth();

  const [drive, setDrive] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [hasApplied, setHasApplied] = useState(false);

  useEffect(() => {
    fetchDriveDetails();
    if (isAuthenticated && role === 'STUDENT') {
      checkApplicationStatus();
    }
  }, [id, isAuthenticated, role]);

  const fetchDriveDetails = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await apiClient.get(`/drives/${id}/`);
      if (res.data?.success) {
        setDrive(res.data.data);
      }
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to load drive details.'));
    } finally {
      setLoading(false);
    }
  };

  const checkApplicationStatus = async () => {
    try {
      const res = await apiClient.get('/applications/');
      if (res.data?.success) {
        const found = res.data.data.find((app) => app.drive === parseInt(id));
        if (found) {
          setHasApplied(true);
        }
      }
    } catch (err) {
      console.warn('Could not check application status', err);
    }
  };

  const handleApply = async () => {
    setError('');
    setSuccessMsg('');
    setSubmitting(true);

    try {
      const res = await apiClient.post('/applications/', {
        drive_id: parseInt(id),
      });

      if (res.data?.success) {
        setSuccessMsg('Your application has been submitted successfully!');
        setHasApplied(true);
      }
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to submit application.'));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="container py-5">
        <LoadingSpinner message="Fetching placement drive details..." />
      </div>
    );
  }

  if (!drive) {
    return (
      <div className="container py-5 text-center">
        <AlertMessage type="warning" message="Placement drive not found." />
        <Link to="/drives" className="btn btn-primary mt-3">
          <i className="bi bi-arrow-left me-2"></i> Back to Drives
        </Link>
      </div>
    );
  }

  // Calculate student eligibility previews
  const studentCgpa = parseFloat(user?.profile?.cgpa || 0);
  const minCgpa = parseFloat(drive.min_cgpa || 0);
  const cgpaEligible = !isNaN(studentCgpa) && studentCgpa >= minCgpa;

  const allowedList = (drive.allowed_departments || 'All')
    .split(',')
    .map((d) => d.trim().toUpperCase());
  const studentDept = (user?.profile?.department || '').trim().toUpperCase();
  const deptEligible = allowedList.includes('ALL') || (studentDept && allowedList.includes(studentDept));

  const isEligible = cgpaEligible && deptEligible;

  return (
    <div className="container py-4">
      {/* Breadcrumb */}
      <nav aria-label="breadcrumb" className="mb-4">
        <ol className="breadcrumb">
          <li className="breadcrumb-item"><Link to="/drives">Drives</Link></li>
          <li className="breadcrumb-item active" aria-current="page">{drive.title}</li>
        </ol>
      </nav>

      <AlertMessage type="danger" message={error} onClose={() => setError('')} />
      <AlertMessage type="success" message={successMsg} onClose={() => setSuccessMsg('')} />

      <div className="row g-4">
        {/* Left Column: Drive Info */}
        <div className="col-lg-8">
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-body p-4">
              <div className="d-flex justify-content-between align-items-start mb-3">
                <div>
                  <span className="badge bg-primary bg-opacity-10 text-primary border border-primary-subtle px-3 py-2 fs-6 mb-2">
                    <i className="bi bi-building me-1"></i> {drive.company_name}
                  </span>
                  <h2 className="fw-bold text-dark">{drive.title}</h2>
                </div>
                <span className={`badge ${drive.is_active ? 'bg-success' : 'bg-secondary'} px-3 py-2`}>
                  {drive.is_active ? 'Active Drive' : 'Closed'}
                </span>
              </div>

              <hr />

              <h5 className="fw-bold mt-4 mb-3">Role Overview & Responsibilities</h5>
              <div className="text-muted" style={{ whiteSpace: 'pre-line', lineHeight: '1.7' }}>
                {drive.description}
              </div>

              {drive.eligibility && (
                <>
                  <h5 className="fw-bold mt-4 mb-3">Special Eligibility Notes</h5>
                  <div className="alert alert-light border">
                    <i className="bi bi-info-circle me-2 text-primary"></i>
                    {drive.eligibility}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Key Details & Application Box */}
        <div className="col-lg-4">
          <div className="card shadow-sm border-0 mb-4 sticky-top" style={{ top: '80px' }}>
            <div className="card-body p-4">
              <h5 className="fw-bold mb-3 border-bottom pb-2">Placement Highlights</h5>

              <ul className="list-unstyled mb-4">
                <li className="d-flex justify-content-between py-2 border-bottom">
                  <span className="text-muted"><i className="bi bi-award me-2"></i> Min CGPA:</span>
                  <strong className="text-dark">{drive.min_cgpa}</strong>
                </li>
                <li className="d-flex justify-content-between py-2 border-bottom">
                  <span className="text-muted"><i className="bi bi-diagram-3 me-2"></i> Departments:</span>
                  <strong className="text-dark text-end">{drive.allowed_departments}</strong>
                </li>
                <li className="d-flex justify-content-between py-2 border-bottom">
                  <span className="text-muted"><i className="bi bi-calendar3 me-2"></i> Drive Date:</span>
                  <strong className="text-dark">{drive.drive_date}</strong>
                </li>
              </ul>

              {/* Interaction CTA depending on User state */}
              {isAuthenticated && role === 'STUDENT' ? (
                <div>
                  <div className="card bg-light border-0 p-3 mb-3">
                    <h6 className="fw-bold mb-2 small text-uppercase text-muted">Your Eligibility Preview</h6>
                    <div className="d-flex justify-content-between align-items-center mb-1 small">
                      <span>Your CGPA: <strong>{user?.profile?.cgpa || 'N/A'}</strong></span>
                      {cgpaEligible ? (
                        <span className="badge bg-success"><i className="bi bi-check me-1"></i> Meets Criteria</span>
                      ) : (
                        <span className="badge bg-danger"><i className="bi bi-x me-1"></i> Below {drive.min_cgpa}</span>
                      )}
                    </div>
                    <div className="d-flex justify-content-between align-items-center small">
                      <span>Department: <strong>{user?.profile?.department || 'N/A'}</strong></span>
                      {deptEligible ? (
                        <span className="badge bg-success"><i className="bi bi-check me-1"></i> Eligible Dept</span>
                      ) : (
                        <span className="badge bg-danger"><i className="bi bi-x me-1"></i> Not Eligible</span>
                      )}
                    </div>
                  </div>

                  {hasApplied ? (
                    <div className="alert alert-success text-center py-3 mb-0">
                      <i className="bi bi-check-circle-fill me-2 fs-5"></i>
                      <strong>Applied</strong>
                      <div className="small mt-1">You have already submitted an application for this drive.</div>
                      <Link to="/student/applications" className="btn btn-outline-success btn-sm mt-2">
                        View in My Applications
                      </Link>
                    </div>
                  ) : (
                    <button
                      className="btn btn-primary w-100 py-2 fw-semibold"
                      onClick={handleApply}
                      disabled={submitting || !drive.is_active}
                    >
                      {submitting ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2"></span>
                          Submitting...
                        </>
                      ) : !drive.is_active ? (
                        'Drive is Inactive'
                      ) : (
                        <>
                          <i className="bi bi-send-fill me-2"></i> Apply for this Drive
                        </>
                      )}
                    </button>
                  )}
                </div>
              ) : isAuthenticated && role === 'COMPANY' ? (
                <div className="text-center py-2">
                  <p className="text-muted small mb-3">You are viewing this drive in recruiter view.</p>
                  <Link to={`/company/drives/${drive.id}/applicants`} className="btn btn-outline-primary w-100 mb-2">
                    <i className="bi bi-people me-1"></i> View Applicants
                  </Link>
                  <Link to={`/company/drives/${drive.id}/edit`} className="btn btn-outline-secondary w-100">
                    <i className="bi bi-pencil me-1"></i> Edit Drive
                  </Link>
                </div>
              ) : (
                <div className="text-center py-2">
                  <p className="text-muted small mb-3">Sign in as an eligible student to apply for this placement drive.</p>
                  <Link to="/login" className="btn btn-primary w-100 fw-semibold">
                    <i className="bi bi-box-arrow-in-right me-1"></i> Sign In to Apply
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DriveDetail;
