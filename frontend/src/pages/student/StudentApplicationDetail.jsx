import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient, { getErrorMessage } from '../../api/client';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';
import AlertMessage from '../../components/AlertMessage';

const StudentApplicationDetail = () => {
  const { id } = useParams();
  const [application, setApplication] = useState(null);
  const [interview, setInterview] = useState(null);
  const [offer, setOffer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionMsg, setActionMsg] = useState('');

  useEffect(() => {
    fetchApplicationDetails();
  }, [id]);

  const fetchApplicationDetails = async () => {
    setLoading(true);
    setError('');
    try {
      const [appRes, intRes, offRes] = await Promise.all([
        apiClient.get(`/applications/${id}/`),
        apiClient.get('/interviews/'),
        apiClient.get('/offers/'),
      ]);

      if (appRes.data?.success) {
        setApplication(appRes.data.data);
      }

      // Match interview belonging to this application
      if (intRes.data?.success) {
        const foundInt = intRes.data.data.find((i) => i.application === parseInt(id));
        if (foundInt) setInterview(foundInt);
      }

      // Match offer belonging to this application
      if (offRes.data?.success) {
        const foundOff = offRes.data.data.find((o) => o.application === parseInt(id));
        if (foundOff) setOffer(foundOff);
      }
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to load application details.'));
    } finally {
      setLoading(false);
    }
  };

  const handleOfferResponse = async (accept) => {
    if (!offer) return;
    setError('');
    setActionMsg('');

    try {
      const res = await apiClient.post(`/offers/${offer.id}/respond/`, { accept });
      if (res.data?.success) {
        setOffer(res.data.data);
        setActionMsg(`Offer has been ${accept ? 'accepted' : 'rejected'} successfully!`);
      }
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to update offer response.'));
    }
  };

  if (loading) {
    return (
      <div className="container py-5">
        <LoadingSpinner message="Fetching application progress..." />
      </div>
    );
  }

  if (!application) {
    return (
      <div className="container py-5 text-center">
        <AlertMessage type="danger" message="Application record not found." />
        <Link to="/student/applications" className="btn btn-primary mt-3">
          Back to Applications
        </Link>
      </div>
    );
  }

  const steps = [
    { key: 'APPLIED', label: '1. Applied' },
    { key: 'SHORTLISTED', label: '2. Shortlisted' },
    { key: 'INTERVIEW_SCHEDULED', label: '3. Interview' },
    { key: 'SELECTED', label: '4. Selected' },
    { key: 'OFFERED', label: '5. Offered' },
  ];

  const getStepStatusClass = (stepKey) => {
    if (application.status === 'REJECTED') {
      return 'bg-danger text-white';
    }

    const order = ['APPLIED', 'SHORTLISTED', 'INTERVIEW_SCHEDULED', 'SELECTED', 'OFFERED'];
    const currentIndex = order.indexOf(application.status);
    const stepIndex = order.indexOf(stepKey);

    if (stepIndex <= currentIndex) {
      return 'bg-success text-white';
    }
    return 'bg-light text-muted border';
  };

  return (
    <div className="container py-4">
      <nav aria-label="breadcrumb" className="mb-4">
        <ol className="breadcrumb">
          <li className="breadcrumb-item"><Link to="/student/applications">My Applications</Link></li>
          <li className="breadcrumb-item active" aria-current="page">Application #{application.id}</li>
        </ol>
      </nav>

      <AlertMessage type="danger" message={error} onClose={() => setError('')} />
      <AlertMessage type="success" message={actionMsg} onClose={() => setActionMsg('')} />

      <div className="card shadow-sm border-0 mb-4">
        <div className="card-body p-4">
          <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-start gap-3 mb-4">
            <div>
              <span className="badge bg-light text-primary border mb-2 fs-6">
                {application.company_name}
              </span>
              <h2 className="fw-bold text-dark mb-1">{application.drive_title}</h2>
              <p className="text-muted small mb-0">
                Applied on: <strong>{new Date(application.applied_date).toLocaleString()}</strong>
              </p>
            </div>
            <div className="text-md-end">
              <span className="d-block small text-muted mb-1">Status:</span>
              <StatusBadge status={application.status} />
            </div>
          </div>

          {/* Progress Timeline */}
          <div className="bg-light p-4 rounded-3 mb-4">
            <h6 className="fw-bold text-uppercase small text-muted mb-3">Recruitment Progression</h6>
            {application.status === 'REJECTED' ? (
              <div className="alert alert-danger mb-0">
                <i className="bi bi-x-circle-fill me-2"></i>
                This application was not selected to proceed further. Thank you for your interest and effort.
              </div>
            ) : (
              <div className="row text-center g-2">
                {steps.map((step) => (
                  <div key={step.key} className="col">
                    <div className={`p-2 rounded-2 small fw-semibold ${getStepStatusClass(step.key)}`}>
                      {step.label}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Associated Interview Card */}
          {interview && (
            <div className="card border-primary-subtle bg-primary bg-opacity-10 mb-4">
              <div className="card-body">
                <div className="d-flex justify-content-between align-items-center mb-2">
                  <h5 className="fw-bold text-primary mb-0">
                    <i className="bi bi-calendar-check me-2"></i> Scheduled Interview
                  </h5>
                  <StatusBadge status={interview.status} />
                </div>
                <div className="row mt-3 text-dark small">
                  <div className="col-md-6 mb-2">
                    <strong>Date & Time: </strong>
                    {new Date(interview.interview_date).toLocaleString()}
                  </div>
                  <div className="col-md-6 mb-2">
                    <strong>Meeting Mode: </strong>
                    {interview.mode}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Associated Job Offer Card */}
          {offer && (
            <div className="card border-success shadow-sm mb-4">
              <div className="card-header bg-success text-white py-3 d-flex justify-content-between align-items-center">
                <h5 className="fw-bold mb-0">
                  <i className="bi bi-award-fill me-2"></i> Official Job Offer
                </h5>
                <StatusBadge status={offer.status} />
              </div>
              <div className="card-body p-4">
                <div className="row g-3">
                  <div className="col-md-4">
                    <span className="text-muted small d-block">Position</span>
                    <strong className="fs-5 text-dark">{offer.position}</strong>
                  </div>
                  <div className="col-md-4">
                    <span className="text-muted small d-block">Annual CTC / Salary</span>
                    <strong className="fs-5 text-success">₹ {parseFloat(offer.salary).toLocaleString()}</strong>
                  </div>
                  <div className="col-md-4">
                    <span className="text-muted small d-block">Offer Date</span>
                    <strong className="fs-5 text-dark">{offer.offer_date}</strong>
                  </div>
                </div>

                {offer.status === 'PENDING' && (
                  <div className="mt-4 pt-3 border-top d-flex gap-3">
                    <button
                      className="btn btn-success fw-semibold px-4"
                      onClick={() => handleOfferResponse(true)}
                    >
                      <i className="bi bi-check-lg me-1"></i> Accept Job Offer
                    </button>
                    <button
                      className="btn btn-outline-danger fw-semibold px-4"
                      onClick={() => handleOfferResponse(false)}
                    >
                      <i className="bi bi-x-lg me-1"></i> Decline Offer
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="d-flex justify-content-between pt-3 border-top">
            <Link to="/student/applications" className="btn btn-outline-secondary">
              <i className="bi bi-arrow-left me-1"></i> Back to Applications
            </Link>
            <Link to={`/drives/${application.drive}`} className="btn btn-outline-primary">
              View Drive Details <i className="bi bi-arrow-right ms-1"></i>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentApplicationDetail;
