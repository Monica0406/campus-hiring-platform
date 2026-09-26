import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api, { getErrorMessage } from "../../api/client";
import StatusBadge from "../../components/StatusBadge";
import LoadingSpinner from "../../components/LoadingSpinner";
import AlertMessage from "../../components/AlertMessage";

export default function CompanyInterviews() {
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Result modal state
  const [selectedInterview, setSelectedInterview] = useState(null);
  const [passedChoice, setPassedChoice] = useState(true);

  useEffect(() => {
    fetchInterviews();
  }, []);

  const fetchInterviews = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get("/interviews/");
      setInterviews(res.data?.data || res.data || []);
    } catch (err) {
      setError(getErrorMessage(err, "Failed to load scheduled interviews."));
    } finally {
      setLoading(false);
    }
  };

  const handleOpenResultModal = (interview) => {
    setSelectedInterview(interview);
    setPassedChoice(true);
  };

  const handleRecordResult = async () => {
    if (!selectedInterview) return;
    setActionLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await api.patch(`/api/interviews/${selectedInterview.id}/`, {
        passed: passedChoice,
      });
      setSuccess(
        `Interview #${selectedInterview.id} result recorded as: ${
          passedChoice ? "PASSED (Candidate eligible for Offer)" : "FAILED"
        }`
      );
      setSelectedInterview(null);
      fetchInterviews();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to record interview result."));
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading interviews..." />;

  return (
    <div className="container py-4">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-2">
        <div>
          <h2 className="fw-bold mb-1">Company Interviews</h2>
          <p className="text-muted mb-0">Track and record evaluation results for candidate interviews.</p>
        </div>
        <Link to="/company/drives" className="btn btn-outline-primary">
          <i className="bi bi-briefcase me-2"></i>My Drives
        </Link>
      </div>

      <AlertMessage type="danger" message={error} onClose={() => setError(null)} />
      <AlertMessage type="success" message={success} onClose={() => setSuccess(null)} />

      {interviews.length === 0 ? (
        <div className="card shadow-sm border-0 text-center py-5">
          <div className="card-body">
            <i className="bi bi-camera-video text-muted" style={{ fontSize: "3rem" }}></i>
            <h5 className="mt-3 text-muted">No Interviews Scheduled</h5>
            <p className="text-muted small">
              To schedule an interview, open a drive's applicants list, shortlist a candidate, and click "Schedule Interview".
            </p>
            <Link to="/company/drives" className="btn btn-primary btn-sm">
              Go to Drives
            </Link>
          </div>
        </div>
      ) : (
        <div className="card shadow-sm border-0 overflow-hidden">
          <div className="table-responsive">
            <table className="table table-hover align-middle mb-0">
              <thead className="table-light">
                <tr>
                  <th>ID</th>
                  <th>Candidate</th>
                  <th>Drive / Role</th>
                  <th>Scheduled For</th>
                  <th>Mode</th>
                  <th>Status</th>
                  <th className="text-end">Action</th>
                </tr>
              </thead>
              <tbody>
                {interviews.map((iv) => (
                  <tr key={iv.id}>
                    <td className="fw-bold text-secondary">#{iv.id}</td>
                    <td>
                      <div className="fw-semibold">{iv.student_name || "N/A"}</div>
                      <small className="text-muted">{iv.student_email || "N/A"}</small>
                    </td>
                    <td>{iv.drive_title || "N/A"}</td>
                    <td>
                      <div>{new Date(iv.interview_date).toLocaleDateString()}</div>
                      <small className="text-muted">{new Date(iv.interview_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</small>
                    </td>
                    <td>
                      <span className="badge bg-light text-dark border">{iv.mode}</span>
                    </td>
                    <td>
                      <StatusBadge status={iv.status} />
                    </td>
                    <td className="text-end">
                      <div className="btn-group btn-group-sm">
                        {iv.application && (
                          <Link
                            to={`/company/applications/${iv.application}`}
                            className="btn btn-outline-secondary"
                            title="View Application Details"
                          >
                            View App
                          </Link>
                        )}
                        {iv.status === "SCHEDULED" && (
                          <button
                            className="btn btn-primary"
                            onClick={() => handleOpenResultModal(iv)}
                            disabled={actionLoading}
                          >
                            Record Result
                          </button>
                        )}
                        {iv.status === "PASSED" && iv.application && (
                          <Link
                            to={`/company/applications/${iv.application}`}
                            className="btn btn-warning"
                          >
                            Extend Offer
                          </Link>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Record Result Modal */}
      {selectedInterview && (
        <div className="modal fade show d-block" tabIndex="-1" style={{ backgroundColor: "rgba(0,0,0,0.5)" }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content border-0 shadow">
              <div className="modal-header bg-primary text-white">
                <h5 className="modal-title">Record Interview Result #{selectedInterview.id}</h5>
                <button type="button" className="btn-close btn-close-white" onClick={() => setSelectedInterview(null)}></button>
              </div>
              <div className="modal-body p-4">
                <p className="mb-2">
                  <strong>Candidate:</strong> {selectedInterview.student_name}
                </p>
                <p className="mb-4">
                  <strong>Drive:</strong> {selectedInterview.drive_title}
                </p>

                <label className="form-label fw-semibold">Interview Evaluation Outcome</label>
                <div className="d-flex flex-column gap-2">
                  <div className="form-check p-3 border rounded">
                    <input
                      className="form-check-input"
                      type="radio"
                      name="evalResult"
                      id="resPass"
                      checked={passedChoice === true}
                      onChange={() => setPassedChoice(true)}
                    />
                    <label className="form-check-label fw-bold text-success" htmlFor="resPass">
                      PASSED (Recommend candidate for Job Offer)
                    </label>
                    <small className="d-block text-muted">
                      Marks candidate as PASSED, unlocking the ability to generate a formal offer.
                    </small>
                  </div>

                  <div className="form-check p-3 border rounded">
                    <input
                      className="form-check-input"
                      type="radio"
                      name="evalResult"
                      id="resFail"
                      checked={passedChoice === false}
                      onChange={() => setPassedChoice(false)}
                    />
                    <label className="form-check-label fw-bold text-danger" htmlFor="resFail">
                      FAILED (Did not meet expectations)
                    </label>
                    <small className="d-block text-muted">
                      Marks interview as FAILED and rejects the application.
                    </small>
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setSelectedInterview(null)}>
                  Cancel
                </button>
                <button
                  type="button"
                  className={`btn ${passedChoice ? "btn-success" : "btn-danger"}`}
                  onClick={handleRecordResult}
                  disabled={actionLoading}
                >
                  {actionLoading ? "Submitting..." : "Save Evaluation"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
