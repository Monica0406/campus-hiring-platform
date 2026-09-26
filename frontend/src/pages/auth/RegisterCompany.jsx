import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import AlertMessage from '../../components/AlertMessage';

const RegisterCompany = () => {
  const { registerCompany } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    company_name: '',
    email: '',
    password: '',
    confirmPassword: '',
    location: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');

    if (formData.password !== formData.confirmPassword) {
      setErrorMessage('Passwords do not match.');
      return;
    }

    if (formData.password.length < 6) {
      setErrorMessage('Password must be at least 6 characters.');
      return;
    }

    setSubmitting(true);
    const result = await registerCompany({
      company_name: formData.company_name.trim(),
      email: formData.email.trim(),
      password: formData.password,
      location: formData.location.trim(),
    });
    setSubmitting(false);

    if (result.success) {
      navigate('/company/dashboard', { replace: true });
    } else {
      setErrorMessage(result.error);
    }
  };

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-8 col-lg-6">
          <div className="card shadow-sm border-0 rounded-3">
            <div className="card-body p-4 p-md-5">
              <div className="text-center mb-4">
                <div className="p-3 bg-primary bg-opacity-10 text-primary rounded-circle d-inline-flex mb-3">
                  <i className="bi bi-building fs-1"></i>
                </div>
                <h3 className="fw-bold">Company Registration</h3>
                <p className="text-muted">Register your organization to post campus drives and hire talent</p>
              </div>

              <AlertMessage type="danger" message={errorMessage} onClose={() => setErrorMessage('')} />

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label fw-semibold">Company / Organization Name *</label>
                  <input
                    type="text"
                    name="company_name"
                    className="form-control"
                    placeholder="e.g. Acme Technologies Ltd"
                    value={formData.company_name}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label fw-semibold">Work / Official Email *</label>
                  <input
                    type="email"
                    name="email"
                    className="form-control"
                    placeholder="recruiter@company.com"
                    value={formData.email}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label className="form-label fw-semibold">Password *</label>
                    <input
                      type="password"
                      name="password"
                      className="form-control"
                      placeholder="At least 6 characters"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      minLength={6}
                    />
                  </div>
                  <div className="col-md-6 mb-3">
                    <label className="form-label fw-semibold">Confirm Password *</label>
                    <input
                      type="password"
                      name="confirmPassword"
                      className="form-control"
                      placeholder="Repeat password"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>

                <div className="mb-4">
                  <label className="form-label fw-semibold">Primary Office Location *</label>
                  <input
                    type="text"
                    name="location"
                    className="form-control"
                    placeholder="e.g. Bangalore, India or San Francisco, USA"
                    value={formData.location}
                    onChange={handleChange}
                    required
                  />
                </div>

                <button
                  type="submit"
                  className="btn btn-primary w-100 py-2 fw-semibold"
                  disabled={submitting}
                >
                  {submitting ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Registering...
                    </>
                  ) : (
                    'Complete Company Registration'
                  )}
                </button>
              </form>

              <div className="text-center mt-4">
                <span className="text-muted small">Already registered? </span>
                <Link to="/login" className="text-primary text-decoration-none fw-semibold small">
                  Sign in here
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterCompany;
