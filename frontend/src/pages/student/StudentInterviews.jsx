import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient, { getErrorMessage } from '../../api/client';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';
import AlertMessage from '../../components/AlertMessage';

const StudentInterviews = () => {
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchInterviews();
  }, []);

  const fetchInterviews = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await apiClient.get('/interviews/');
      if (res.data?.success) {
        setInterviews(res.data.data);
      }
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to load interviews.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold mb-1">My Interviews</h2>
          <p className="text-muted mb-0">Scheduled interview rounds and meeting details</p>
        </div>
      </div>

      <AlertMessage type="danger" message={error} onClose={() => setError('')} />

      {loading ? (
        <LoadingSpinner message="Fetching your scheduled interviews..." />
      ) : interviews.length === 0 ? (
        <div className="card shadow-sm border-0 p-5 text-center">
          <div className="mb-3 text-muted">
            <i className="bi bi-calendar2-x fs-1"></i>
          </div>
          <h4 className="fw-bold">No Scheduled Interviews</h4>
          <p className="text-muted mb-3">
            You currently have no interviews scheduled. Once a company shortlists your application, your interview round will appear here.
          </p>
          <div>
            <Link to="/student/applications" className="btn btn-primary px-4 fw-semibold">
              View My Applications
            </Link>
          </div>
        </div>
      ) : (
        <div className="row g-4">
          {interviews.map((item) => (
            <div key={item.id} className="col-md-6">
              <div className="card shadow-sm border-0 h-100">
                <div className="card-body p-4">
                  <div className="d-flex justify-content-between align-items-start mb-3">
                    <div>
                      <span className="badge bg-light text-primary border mb-1">
                        {item.company_name}
                      </span>
                      <h5 className="fw-bold text-dark mb-0">{item.drive_title}</h5>
                    </div>
                    <StatusBadge status={item.status} />
                  </div>

                  <div className="bg-light p-3 rounded-2 my-3 small">
                    <div className="d-flex justify-content-between mb-2">
                      <span className="text-muted">
                        <i className="bi bi-calendar-event me-2"></i> Date & Time:
                      </span>
                      <strong className="text-dark">
                        {new Date(item.interview_date).toLocaleString()}
                      </strong>
                    </div>
                    <div className="d-flex justify-content-between">
                      <span className="text-muted">
                        <i className="bi bi-camera-video me-2"></i> Meeting Mode:
                      </span>
                      <strong className="text-dark">{item.mode}</strong>
                    </div>
                  </div>

                  <div className="d-flex justify-content-end">
                    <Link
                      to={`/student/applications/${item.application}`}
                      className="btn btn-sm btn-outline-primary"
                    >
                      View Application Details <i className="bi bi-arrow-right ms-1"></i>
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default StudentInterviews;
