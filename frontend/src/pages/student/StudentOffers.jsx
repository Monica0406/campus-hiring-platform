import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient, { getErrorMessage } from '../../api/client';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';
import AlertMessage from '../../components/AlertMessage';

const StudentOffers = () => {
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [respondingId, setRespondingId] = useState(null);

  useEffect(() => {
    fetchOffers();
  }, []);

  const fetchOffers = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await apiClient.get('/offers/');
      if (res.data?.success) {
        setOffers(res.data.data);
      }
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to load offers.'));
    } finally {
      setLoading(false);
    }
  };

  const handleRespond = async (offerId, accept) => {
    setError('');
    setSuccessMsg('');
    setRespondingId(offerId);

    try {
      const res = await apiClient.post(`/offers/${offerId}/respond/`, { accept });
      if (res.data?.success) {
        setOffers((prev) =>
          prev.map((o) => (o.id === offerId ? res.data.data : o))
        );
        setSuccessMsg(`Offer ${accept ? 'accepted' : 'declined'} successfully!`);
      }
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to submit response to offer.'));
    } finally {
      setRespondingId(null);
    }
  };

  return (
    <div className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold mb-1">My Job Offers</h2>
          <p className="text-muted mb-0">Review offer packages and record your acceptance decisions</p>
        </div>
      </div>

      <AlertMessage type="success" message={successMsg} onClose={() => setSuccessMsg('')} />
      <AlertMessage type="danger" message={error} onClose={() => setError('')} />

      {loading ? (
        <LoadingSpinner message="Fetching job offers..." />
      ) : offers.length === 0 ? (
        <div className="card shadow-sm border-0 p-5 text-center">
          <div className="mb-3 text-muted">
            <i className="bi bi-award fs-1"></i>
          </div>
          <h4 className="fw-bold">No Job Offers Yet</h4>
          <p className="text-muted mb-3">
            You don't have any job offers at this time. Keep applying to placement drives and preparing for interviews!
          </p>
          <div>
            <Link to="/drives" className="btn btn-primary px-4 fw-semibold">
              Browse Active Drives
            </Link>
          </div>
        </div>
      ) : (
        <div className="row g-4">
          {offers.map((offer) => (
            <div key={offer.id} className="col-lg-6">
              <div
                className={`card shadow-sm border-0 h-100 ${
                  offer.status === 'PENDING' ? 'border-start border-warning border-4' : ''
                }`}
              >
                <div className="card-body p-4 d-flex flex-column">
                  <div className="d-flex justify-content-between align-items-start mb-2">
                    <span className="badge bg-light text-primary border">{offer.company_name}</span>
                    <StatusBadge status={offer.status} />
                  </div>

                  <h4 className="fw-bold text-dark mb-1">{offer.position}</h4>
                  <div className="text-muted small mb-3">{offer.drive_title}</div>

                  <div className="bg-light p-3 rounded-2 mb-4">
                    <div className="d-flex justify-content-between align-items-center mb-2">
                      <span className="text-muted"><i className="bi bi-cash-stack me-2"></i> Annual CTC / Salary:</span>
                      <span className="fs-5 fw-bold text-success">
                        ₹ {parseFloat(offer.salary).toLocaleString()}
                      </span>
                    </div>
                    <div className="d-flex justify-content-between align-items-center small text-muted">
                      <span><i className="bi bi-calendar3 me-2"></i> Extended on:</span>
                      <span>{offer.offer_date}</span>
                    </div>
                  </div>

                  <div className="mt-auto">
                    {offer.status === 'PENDING' ? (
                      <div className="d-flex gap-2">
                        <button
                          className="btn btn-success flex-grow-1 fw-semibold"
                          onClick={() => handleRespond(offer.id, true)}
                          disabled={respondingId === offer.id}
                        >
                          {respondingId === offer.id ? (
                            <span className="spinner-border spinner-border-sm"></span>
                          ) : (
                            <>
                              <i className="bi bi-check-lg me-1"></i> Accept Offer
                            </>
                          )}
                        </button>
                        <button
                          className="btn btn-outline-danger flex-grow-1 fw-semibold"
                          onClick={() => handleRespond(offer.id, false)}
                          disabled={respondingId === offer.id}
                        >
                          {respondingId === offer.id ? (
                            <span className="spinner-border spinner-border-sm"></span>
                          ) : (
                            <>
                              <i className="bi bi-x-lg me-1"></i> Decline
                            </>
                          )}
                        </button>
                      </div>
                    ) : (
                      <div className="text-end">
                        <Link
                          to={`/student/applications/${offer.application}`}
                          className="btn btn-sm btn-outline-secondary"
                        >
                          View Application Details <i className="bi bi-arrow-right ms-1"></i>
                        </Link>
                      </div>
                    )}
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

export default StudentOffers;
