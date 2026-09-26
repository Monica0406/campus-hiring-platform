import React, { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import api, { getErrorMessage } from "../../api/client";
import StatusBadge from "../../components/StatusBadge";
import LoadingSpinner from "../../components/LoadingSpinner";
import AlertMessage from "../../components/AlertMessage";

export default function CompanyApplicationDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [application, setApplication] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Schedule Interview modal
  const [showInterviewModal, setShowInterviewModal] = useState(false);
  const [interviewDate, setInterviewDate] = useState("");
  const [interviewMode, setInterviewMode] = useState("Online");

  // Extend Offer modal
  const [showOfferModal, setShowOfferModal] = useState(false);
  const [offerPosition, setOfferPosition] = useState("");
  const [offerSalary, setOfferSalary] = useState("");

  // Reject modal
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectReason, setRejectReason] = useState("");

  useEffect(() => {
    fetchApplication();
  }, [id]);

  const fetchApplication = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get(`/applications/${id}/`);
      const appData = res.data?.data || res.data;
      setApplication(appData);
      if (appData?.drive_title) {
        setOfferPosition(appData.drive_title);
      }
    } catch (err) {
      setError(getErrorMessage(err, "Failed to load application details."));
    } finally {
      setLoading(false);
    }
  };

  const handleShortlist = async () => {
    setActionLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await api.post(`/api/applications/${id}/shortlist/`);
      setSuccess("Application has been shortlisted!");
      fetchApplication();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to shortlist application."));
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    setActionLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await api.post(`/api/applications/${id}/reject/`, { reason: rejectReason });
      setSuccess("Application has been rejected.");
      setShowRejectModal(false);
      fetchApplication();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to reject application."));
    } finally {
      setActionLoading(false);
    }
  };

  const handleScheduleInterview = async (e) => {
    e.preventDefault();
    setActionLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await api.post("/api/interviews/", {
        application_id: parseInt(id, 10),
        interview_date: new Date(interviewDate).toISOString(),
        mode: interviewMode,
      });
      setSuccess("Interview scheduled successfully! Status updated to INTERVIEW_SCHEDULED.");
      setShowInterviewModal(false);
      fetchApplication();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to schedule interview. Check date and format."));
    } finally {
      setActionLoading(false);
    }
  };

  const handleExtendOffer = async (e) => {
    e.preventDefault();
    setActionLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await api.post("/api/offers/", {
        application_id: parseInt(id, 10),
        position: offerPosition,
        salary: parseFloat(offerSalary),
      });
      setSuccess("Formal job offer generated and sent to student! Status updated to OFFERED.");
      setShowOfferModal(false);
      fetchApplication();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to extend offer. Make sure candidate has passed the interview."));
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading candidate application..." />;
  if (!application) {
    return (
      <div className="container py-5 text-center">
        <h4>Application not found</h4>
        <Link to="/company/dashboard" className="btn btn-primary mt-3">Back to Dashboard</Link>
      </div>
    );
  }

  const { student_details, drive_details } = application;

  return (
    <div className="container py-4">
      <nav aria-label="breadcrumb" className="mb-3">
        <ol className="breadcrumb">
          <li className="breadcrumb-item"><Link to="/company/drives">Drives</Link></li>
          {application.drive && (
            <li className="breadcrumb-item">
              <Link to={`/company/drives/${application.drive}/applicants`}>
                Drive #{application.drive} Applicants
              </Link>
            </li>
          )}
          <li className="breadcrumb-item active">Application #{application.id}</li>
        </ol>
      </nav>

      <AlertMessage type="danger" message={error} onClose={() => setError(null)} />
      <AlertMessage type="success" message={success} onClose={() => setSuccess(null)} />

      {/* Header Card */}
      <div className="card shadow-sm border-0 mb-4">
        <div className="card-body p-4">
          <div className="d-flex flex-wrap justify-content-between align-items-center gap-3">
            <div>
              <div className="d-flex align-items-center gap-3 mb-2">
                <h3 className="fw-bold mb-0">Application #{application.id}</h3>
                <StatusBadge status={application.status} />
              </div>
              <p className="text-muted mb-0">
                Applied on {application.applied_at ? new Date(application.applied_at).toLocaleString() : "N/A"}
              </p>
            </div>

            {/* Workflow Action Buttons */}
            <div className="d-flex flex-wrap gap-2">
              {application.status === "APPLIED" && (
                <>
                  <button
                    className="btn btn-success"
                    onClick={handleShortlist}
                    disabled={actionLoading}
                  >
                    Shortlist Candidate
                  </button>
                  <button
                    className="btn btn-outline-danger"
                    onClick={() => {
                      setRejectReason("Profile did not match criteria");
                      setShowRejectModal(true);
                    }}
                    disabled={actionLoading}
                  >
                    Reject
                  </button>
                </>
              )}

              {application.status === "SHORTLISTED" && (
                <>
                  <button
                    className="btn btn-primary"
                    onClick={() => setShowInterviewModal(true)}
                    disabled={actionLoading}
                  >
                    Schedule Interview
                  </button>
                  <button
                    className="btn btn-outline-danger"
                    onClick={() => {
                      setRejectReason("Candidate did not proceed");
                      setShowRejectModal(true);
                    }}
                    disabled={actionLoading}
                  >
                    Reject
                  </button>
                </>
              )}

              {(application.status === "SHORTLISTED" || application.status === "INTERVIEW_SCHEDULED") && (
                <button
                  className="btn btn-warning fw-semibold"
                  onClick={() => setShowOfferModal(true)}
                  disabled={actionLoading}
                >
                  Generate Job Offer
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="row g-4">
        {/* Candidate Profile Details */}
        <div className="col-lg-6">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-header bg-white py-3 border-bottom">
              <h5 className="card-title fw-bold mb-0">
                <i className="bi bi-person-circle me-2 text-primary"></i>Candidate Profile
              </h5>
            </div>
            <div className="card-body p-4">
              <div className="row g-3">
                <div className="col-sm-6">
                  <span className="text-muted small d-block">Full Name</span>
                  <span className="fw-semibold">{application.student_name || student_details?.name || "N/A"}</span>
                </div>
                <div className="col-sm-6">
                  <span className="text-muted small d-block">Email Address</span>
                  <span className="fw-semibold">{application.student_email || student_details?.email || "N/A"}</span>
                </div>
                <div className="col-sm-6">
                  <span className="text-muted small d-block">Roll / Student ID</span>
                  <span className="fw-semibold">{student_details?.roll_number || "N/A"}</span>
                </div>
                <div className="col-sm-6">
                  <span className="text-muted small d-block">Branch / Department</span>
                  <span className="fw-semibold">{application.student_branch || student_details?.branch || "N/A"}</span>
                </div>
                <div className="col-sm-6">
                  <span className="text-muted small d-block">Cumulative GPA</span>
                  <span className="badge bg-primary fs-6">
                    {application.student_gpa !== undefined ? application.student_gpa : student_details?.gpa || "N/A"}
                  </span>
                </div>
                <div className="col-sm-6">
                  <span className="text-muted small d-block">Active Backlogs</span>
                  <span className={`badge fs-6 ${student_details?.backlogs > 0 ? "bg-warning text-dark" : "bg-success"}`}>
                    {student_details?.backlogs !== undefined ? student_details.backlogs : 0}
                  </span>
                </div>
                <div className="col-12">
                  <span className="text-muted small d-block">Key Skills</span>
                  <div className="mt-1 d-flex flex-wrap gap-1">
                    {student_details?.skills ? (
                      student_details.skills.split(",").map((s, idx) => (
                        <span key={idx} className="badge bg-light text-dark border">
                          {s.trim()}
                        </span>
                      ))
                    ) : (
                      <span className="text-muted small">None listed</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Drive Info */}
        <div className="col-lg-6">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-header bg-white py-3 border-bottom">
              <h5 className="card-title fw-bold mb-0">
                <i className="bi bi-briefcase me-2 text-primary"></i>Placement Drive
              </h5>
            </div>
            <div className="card-body p-4">
              <div className="row g-3">
                <div className="col-12">
                  <span className="text-muted small d-block">Position / Title</span>
                  <h6 className="fw-bold mb-1">{application.drive_title || drive_details?.title || "N/A"}</h6>
                </div>
                <div className="col-sm-6">
                  <span className="text-muted small d-block">Min GPA Requirement</span>
                  <span className="fw-semibold">{drive_details?.min_gpa || "—"}</span>
                </div>
                <div className="col-sm-6">
                  <span className="text-muted small d-block">Max Backlogs Allowed</span>
                  <span className="fw-semibold">{drive_details?.max_backlogs !== undefined ? drive_details.max_backlogs : "—"}</span>
                </div>
                <div className="col-12">
                  <span className="text-muted small d-block">Description</span>
                  <p className="text-muted small mb-0">
                    {drive_details?.description || "No drive description available."}
                  </p>
                </div>
                {application.rejection_reason && (
                  <div className="col-12">
                    <div className="alert alert-danger mb-0">
                      <strong>Rejection Reason:</strong> {application.rejection_reason}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Schedule Interview Modal */}
      {showInterviewModal && (
        <div className="modal fade show d-block" tabIndex="-1" style={{ backgroundColor: "rgba(0,0,0,0.5)" }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content border-0 shadow">
              <div className="modal-header bg-primary text-white">
                <h5 className="modal-title">Schedule Interview</h5>
                <button type="button" className="btn-close btn-close-white" onClick={() => setShowInterviewModal(false)}></button>
              </div>
              <form onSubmit={handleScheduleInterview}>
                <div className="modal-body p-4">
                  <div className="mb-3">
                    <label className="form-label fw-semibold">Interview Date & Time *</label>
                    <input
                      type="datetime-local"
                      className="form-control"
                      value={interviewDate}
                      onChange={(e) => setInterviewDate(e.target.value)}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label fw-semibold">Mode *</label>
                    <select
                      className="form-select"
                      value={interviewMode}
                      onChange={(e) => setInterviewMode(e.target.value)}
                      required
                    >
                      <option value="Online">Online (Google Meet / Zoom)</option>
                      <option value="In-Person">In-Person (Campus Placement Cell)</option>
                    </select>
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowInterviewModal(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={actionLoading}>
                    {actionLoading ? "Scheduling..." : "Schedule Interview"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Extend Offer Modal */}
      {showOfferModal && (
        <div className="modal fade show d-block" tabIndex="-1" style={{ backgroundColor: "rgba(0,0,0,0.5)" }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content border-0 shadow">
              <div className="modal-header bg-warning text-dark">
                <h5 className="modal-title fw-bold">Extend Job Offer</h5>
                <button type="button" className="btn-close" onClick={() => setShowOfferModal(false)}></button>
              </div>
              <form onSubmit={handleExtendOffer}>
                <div className="modal-body p-4">
                  <div className="mb-3">
                    <label className="form-label fw-semibold">Designation / Position *</label>
                    <input
                      type="text"
                      className="form-control"
                      value={offerPosition}
                      onChange={(e) => setOfferPosition(e.target.value)}
                      placeholder="e.g. Graduate Software Engineer"
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label fw-semibold">Annual CTC / Salary (INR) *</label>
                    <input
                      type="number"
                      step="1000"
                      min="10000"
                      className="form-control"
                      value={offerSalary}
                      onChange={(e) => setOfferSalary(e.target.value)}
                      placeholder="e.g. 850000"
                      required
                    />
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowOfferModal(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-warning fw-bold" disabled={actionLoading}>
                    {actionLoading ? "Issuing..." : "Extend Offer"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="modal fade show d-block" tabIndex="-1" style={{ backgroundColor: "rgba(0,0,0,0.5)" }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content border-0 shadow">
              <div className="modal-header bg-danger text-white">
                <h5 className="modal-title">Reject Application</h5>
                <button type="button" className="btn-close btn-close-white" onClick={() => setShowRejectModal(false)}></button>
              </div>
              <div className="modal-body p-4">
                <label className="form-label fw-semibold">Rejection Reason</label>
                <textarea
                  className="form-control"
                  rows="3"
                  value={rejectReason}
                  onChange={(e) => setRejectReason(e.target.value)}
                  placeholder="Provide reason for candidate..."
                />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowRejectModal(false)}>
                  Cancel
                </button>
                <button type="button" className="btn btn-danger" onClick={handleReject} disabled={actionLoading}>
                  {actionLoading ? "Rejecting..." : "Confirm Rejection"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
