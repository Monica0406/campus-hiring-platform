import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import api, { getErrorMessage } from "../../api/client";
import StatusBadge from "../../components/StatusBadge";
import LoadingSpinner from "../../components/LoadingSpinner";
import AlertMessage from "../../components/AlertMessage";

export default function DriveApplicants() {
  const { id } = useParams();
  const [drive, setDrive] = useState(null);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Rejection modal state
  const [rejectAppId, setRejectAppId] = useState(null);
  const [rejectReason, setRejectReason] = useState("");

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [driveRes, appsRes] = await Promise.all([
        api.get(`/drives/${id}/`),
        api.get(`/applications/?drive=${id}`),
      ]);
      setDrive(driveRes.data?.data || driveRes.data);
      setApplications(appsRes.data?.data || appsRes.data || []);
    } catch (err) {
      setError(getErrorMessage(err, "Failed to load drive applicants."));
    } finally {
      setLoading(false);
    }
  };

  const handleShortlist = async (appId) => {
    if (!window.confirm("Shortlist this candidate for the next stage?")) return;
    setActionLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await api.post(`/api/applications/${appId}/shortlist/`);
      setSuccess(`Application #${appId} shortlisted successfully!`);
      fetchData();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to shortlist application."));
    } finally {
      setActionLoading(false);
    }
  };

  const handleOpenRejectModal = (appId) => {
    setRejectAppId(appId);
    setRejectReason("Profile did not match role requirements");
  };

  const handleConfirmReject = async () => {
    if (!rejectAppId) return;
    setActionLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await api.post(`/api/applications/${rejectAppId}/reject/`, {
        reason: rejectReason,
      });
      setSuccess(`Application #${rejectAppId} rejected.`);
      setRejectAppId(null);
      setRejectReason("");
      fetchData();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to reject application."));
    } finally {
      setActionLoading(false);
    }
  };

  const filteredApps = applications.filter((app) => {
    if (statusFilter === "ALL") return true;
    return app.status === statusFilter;
  });

  if (loading) return <LoadingSpinner message="Loading drive applicants..." />;

  return (
    <div className="container py-4">
      <nav aria-label="breadcrumb" className="mb-3">
        <ol className="breadcrumb">
          <li className="breadcrumb-item"><Link to="/company/drives">My Drives</Link></li>
          <li className="breadcrumb-item active">Drive #{id} Applicants</li>
        </ol>
      </nav>

      {drive && (
        <div className="card shadow-sm border-0 mb-4">
          <div className="card-body p-4">
            <div className="d-flex flex-wrap justify-content-between align-items-start gap-3">
              <div>
                <span className="badge bg-primary-subtle text-primary mb-2">Drive #{drive.id}</span>
                <h3 className="fw-bold mb-1">{drive.title}</h3>
                <p className="text-muted mb-0">
                  Eligibility: Min GPA {drive.min_gpa} | Max Backlogs {drive.max_backlogs} | Allowed Branches:{" "}
                  {Array.isArray(drive.allowed_branches) ? drive.allowed_branches.join(", ") : drive.allowed_branches}
                </p>
              </div>
              <div className="d-flex gap-2">
                <Link to={`/company/drives/${id}/edit`} className="btn btn-outline-secondary btn-sm">
                  Edit Drive
                </Link>
                <Link to="/company/interviews" className="btn btn-primary btn-sm">
                  View Interviews
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

      <AlertMessage type="danger" message={error} onClose={() => setError(null)} />
      <AlertMessage type="success" message={success} onClose={() => setSuccess(null)} />

      {/* Filter Bar */}
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-3 gap-2">
        <h5 className="fw-bold mb-0">
          Applicants ({filteredApps.length} of {applications.length})
        </h5>
        <div className="d-flex align-items-center gap-2">
          <label className="form-label mb-0 small text-muted">Status:</label>
          <select
            className="form-select form-select-sm"
            style={{ width: "auto" }}
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="ALL">All Statuses</option>
            <option value="APPLIED">Applied</option>
            <option value="SHORTLISTED">Shortlisted</option>
            <option value="INTERVIEW_SCHEDULED">Interview Scheduled</option>
            <option value="OFFERED">Offered</option>
            <option value="REJECTED">Rejected</option>
          </select>
        </div>
      </div>

      {applications.length === 0 ? (
        <div className="card shadow-sm border-0 text-center py-5">
          <div className="card-body">
            <i className="bi bi-people text-muted" style={{ fontSize: "3rem" }}></i>
            <h5 className="mt-3 text-muted">No Applications Received Yet</h5>
            <p className="text-muted small">Eligible students will appear here once they apply to this drive.</p>
          </div>
        </div>
      ) : filteredApps.length === 0 ? (
        <div className="card shadow-sm border-0 text-center py-4">
          <div className="card-body text-muted">
            No applicants match status filter "{statusFilter}".
          </div>
        </div>
      ) : (
        <div className="card shadow-sm border-0 overflow-hidden">
          <div className="table-responsive">
            <table className="table table-hover align-middle mb-0">
              <thead className="table-light">
                <tr>
                  <th>App #</th>
                  <th>Student Name</th>
                  <th>Email</th>
                  <th>GPA</th>
                  <th>Branch</th>
                  <th>Status</th>
                  <th>Applied On</th>
                  <th className="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredApps.map((app) => (
                  <tr key={app.id}>
                    <td>
                      <span className="fw-bold text-secondary">#{app.id}</span>
                    </td>
                    <td>
                      <div className="fw-semibold">{app.student_name || "N/A"}</div>
                    </td>
                    <td>
                      <span className="text-muted small">{app.student_email || "N/A"}</span>
                    </td>
                    <td>
                      <span className="badge bg-light text-dark border">
                        {app.student_gpa !== undefined ? app.student_gpa : "—"}
                      </span>
                    </td>
                    <td>
                      <span className="text-secondary small">{app.student_branch || "—"}</span>
                    </td>
                    <td>
                      <StatusBadge status={app.status} />
                    </td>
                    <td>
                      <small className="text-muted">
                        {app.applied_at ? new Date(app.applied_at).toLocaleDateString() : "—"}
                      </small>
                    </td>
                    <td className="text-end">
                      <div className="btn-group btn-group-sm">
                        <Link
                          to={`/company/applications/${app.id}`}
                          className="btn btn-outline-primary"
                          title="View Application Details"
                        >
                          Details
                        </Link>
                        {app.status === "APPLIED" && (
                          <button
                            className="btn btn-success"
                            onClick={() => handleShortlist(app.id)}
                            disabled={actionLoading}
                            title="Shortlist Candidate"
                          >
                            Shortlist
                          </button>
                        )}
                        {(app.status === "APPLIED" || app.status === "SHORTLISTED") && (
                          <button
                            className="btn btn-outline-danger"
                            onClick={() => handleOpenRejectModal(app.id)}
                            disabled={actionLoading}
                            title="Reject Candidate"
                          >
                            Reject
                          </button>
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

      {/* Reject Modal Backdrop & Modal */}
      {rejectAppId && (
        <div
          className="modal fade show d-block"
          tabIndex="-1"
          style={{ backgroundColor: "rgba(0,0,0,0.5)" }}
        >
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content border-0 shadow">
              <div className="modal-header bg-danger text-white">
                <h5 className="modal-title">Reject Application #{rejectAppId}</h5>
                <button
                  type="button"
                  className="btn-close btn-close-white"
                  onClick={() => setRejectAppId(null)}
                ></button>
              </div>
              <div className="modal-body p-4">
                <p className="text-muted mb-3">
                  Please provide an optional reason for rejecting this candidate.
                </p>
                <div className="mb-3">
                  <label className="form-label fw-semibold">Rejection Reason</label>
                  <textarea
                    className="form-control"
                    rows="3"
                    value={rejectReason}
                    onChange={(e) => setRejectReason(e.target.value)}
                    placeholder="e.g. Cutoff criteria not met or interview feedback..."
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setRejectAppId(null)}
                  disabled={actionLoading}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="btn btn-danger"
                  onClick={handleConfirmReject}
                  disabled={actionLoading}
                >
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
