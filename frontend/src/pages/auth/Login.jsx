import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import AlertMessage from '../../components/AlertMessage';

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const from = location.state?.from?.pathname || null;

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');

    if (!formData.email.trim() || !formData.password) {
      setErrorMessage('Please enter both email and password.');
      return;
    }

    setSubmitting(true);
    const result = await login(formData.email.trim(), formData.password);
    setSubmitting(false);

    if (result.success) {
      if (from) {
        navigate(from, { replace: true });
      } else if (result.role === 'STUDENT') {
        navigate('/student/dashboard', { replace: true });
      } else if (result.role === 'COMPANY') {
        navigate('/company/dashboard', { replace: true });
      } else {
        navigate('/', { replace: true });
      }
    } else {
      setErrorMessage(result.error);
    }
  };

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-6 col-lg-5">
          <div className="card shadow-sm border-0 rounded-3">
            <div className="card-body p-4 p-md-5">
              <div className="text-center mb-4">
                <div className="p-3 bg-primary bg-opacity-10 text-primary rounded-circle d-inline-flex mb-3">
                  <i className="bi bi-box-arrow-in-right fs-1"></i>
                </div>
                <h3 className="fw-bold">Welcome Back</h3>
                <p className="text-muted">Sign in to your CampusHire account</p>
              </div>

              <AlertMessage type="danger" message={errorMessage} onClose={() => setErrorMessage('')} />

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label fw-semibold">Email address</label>
                  <div className="input-group">
                    <span className="input-group-text bg-light"><i className="bi bi-envelope"></i></span>
                    <input
                      type="email"
                      name="email"
                      className="form-control"
                      placeholder="name@college.edu or hr@company.com"
                      value={formData.email}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>

                <div className="mb-4">
                  <label className="form-label fw-semibold">Password</label>
                  <div className="input-group">
                    <span className="input-group-text bg-light"><i className="bi bi-lock"></i></span>
                    <input
                      type="password"
                      name="password"
                      className="form-control"
                      placeholder="Enter your password"
                      value={formData.password}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="btn btn-primary w-100 py-2 fw-semibold"
                  disabled={submitting}
                >
                  {submitting ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Signing in...
                    </>
                  ) : (
                    'Sign In'
                  )}
                </button>
              </form>

              <hr className="my-4" />

              <div className="text-center">
                <p className="text-muted mb-2 small">Don't have an account yet?</p>
                <div className="d-flex justify-content-center gap-2">
                  <Link to="/register/student" className="btn btn-outline-primary btn-sm">
                    <i className="bi bi-mortarboard me-1"></i> Register Student
                  </Link>
                  <Link to="/register/company" className="btn btn-outline-secondary btn-sm">
                    <i className="bi bi-building me-1"></i> Register Company
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
