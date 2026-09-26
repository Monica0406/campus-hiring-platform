import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api, { getErrorMessage } from "../../api/client";
import StatusBadge from "../../components/StatusBadge";
import StatCard from "../../components/StatCard";
import LoadingSpinner from "../../components/LoadingSpinner";
import AlertMessage from "../../components/AlertMessage";

export default function CompanyOffers() {
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchOffers();
  }, []);

  const fetchOffers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get("/offers/");
      setOffers(res.data?.data || res.data || []);
    } catch (err) {
      setError(getErrorMessage(err, "Failed to load company offers."));
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading extended offers..." />;

  const totalOffers = offers.length;
  const acceptedOffers = offers.filter((o) => o.status === "ACCEPTED").length;
  const pendingOffers = offers.filter((o) => o.status === "PENDING").length;
  const rejectedOffers = offers.filter((o) => o.status === "REJECTED").length;

  return (
    <div className="container py-4">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-2">
        <div>
          <h2 className="fw-bold mb-1">Company Job Offers</h2>
          <p className="text-muted mb-0">Track formal employment offers extended to candidates and student acceptance.</p>
        </div>
        <Link to="/company/drives" className="btn btn-outline-primary">
          <i className="bi bi-briefcase me-2"></i>My Drives
        </Link>
      </div>

      <AlertMessage type="danger" message={error} onClose={() => setError(null)} />

      {/* Summary KPI Cards */}
      <div className="row g-3 mb-4">
        <div className="col-sm-6 col-lg-3">
          <StatCard title="Total Offers" value={totalOffers} icon="bi-award" colorClass="bg-primary" />
        </div>
        <div className="col-sm-6 col-lg-3">
          <StatCard title="Accepted" value={acceptedOffers} icon="bi-check-circle" colorClass="bg-success" />
        </div>
        <div className="col-sm-6 col-lg-3">
          <StatCard title="Pending Decision" value={pendingOffers} icon="bi-hourglass-split" colorClass="bg-warning text-dark" />
        </div>
        <div className="col-sm-6 col-lg-3">
          <StatCard title="Declined" value={rejectedOffers} icon="bi-x-circle" colorClass="bg-secondary" />
        </div>
      </div>

      {offers.length === 0 ? (
        <div className="card shadow-sm border-0 text-center py-5">
          <div className="card-body">
            <i className="bi bi-envelope-paper text-muted" style={{ fontSize: "3rem" }}></i>
            <h5 className="mt-3 text-muted">No Job Offers Extended Yet</h5>
            <p className="text-muted small">
              Once candidates pass their interview stage, you can generate and extend an offer directly from their application page.
            </p>
            <Link to="/company/interviews" className="btn btn-primary btn-sm">
              Review Interviews
            </Link>
          </div>
        </div>
      ) : (
        <div className="card shadow-sm border-0 overflow-hidden">
          <div className="table-responsive">
            <table className="table table-hover align-middle mb-0">
              <thead className="table-light">
                <tr>
                  <th>Offer #</th>
                  <th>Candidate</th>
                  <th>Position</th>
                  <th>Drive</th>
                  <th>Salary / CTC</th>
                  <th>Offer Date</th>
                  <th>Decision Status</th>
                  <th className="text-end">Details</th>
                </tr>
              </thead>
              <tbody>
                {offers.map((offer) => (
                  <tr key={offer.id}>
                    <td className="fw-bold text-secondary">#{offer.id}</td>
                    <td>
                      <div className="fw-semibold">{offer.student_name || "N/A"}</div>
                      <small className="text-muted">{offer.student_email || "N/A"}</small>
                    </td>
                    <td>
                      <span className="fw-semibold">{offer.position}</span>
                    </td>
                    <td>{offer.drive_title || "N/A"}</td>
                    <td>
                      <span className="fw-bold text-success">
                        ₹{Number(offer.salary).toLocaleString()}
                      </span>
                    </td>
                    <td>
                      <small className="text-muted">
                        {offer.offer_date ? new Date(offer.offer_date).toLocaleDateString() : "—"}
                      </small>
                    </td>
                    <td>
                      <StatusBadge status={offer.status} />
                    </td>
                    <td className="text-end">
                      {offer.application ? (
                        <Link
                          to={`/company/applications/${offer.application}`}
                          className="btn btn-sm btn-outline-primary"
                        >
                          View App
                        </Link>
                      ) : (
                        "—"
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
