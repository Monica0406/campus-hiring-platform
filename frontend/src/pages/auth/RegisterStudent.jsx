import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import AlertMessage from '../../components/AlertMessage';

const RegisterStudent = () => {
  const { registerStudent } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    college: '',
    department: 'CSE',
    cgpa: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const departments = ['CSE', 'IT', 'ECE', 'EEE', 'MECH', 'CIVIL', 'AI&DS', 'OTHER'];

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');

    // Validations
    if (formData.password !== formData.confirmPassword) {
      setErrorMessage('Passwords do not match.');
      return;
    }

    if (formData.password.length < 6) {
      setErrorMessage('Password must be at least 6 characters.');
      return;
    }

    const parsedCgpa = parseFloat(formData.cgpa);
    if (isNaN(parsedCgpa) || parsedCgpa < 0 || parsedCgpa > 10) {
      setErrorMessage('Please enter a valid CGPA between 0.00 and 10.00.');
      return;
    }

    setSubmitting(true);
    const result = await registerStudent({
      name: formData.name.trim(),
      email: formData.email.trim(),
      password: formData.password,
      college: formData.college.trim(),
      department: formData.department.trim(),
      cgpa: parsedCgpa.toFixed(2),
    });
    setSubmitting(false);

    if (result.success) {
      navigate('/student/dashboard', { replace: true });
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
                  <i className="bi bi-mortarboard fs-1"></i>
                </div>
                <h3 className="fw-bold">Student Registration</h3>
                <p className="text-muted">Create your profile to apply for placement drives</p>
              </div>

              <AlertMessage type="danger" message={errorMessage} onClose={() => setErrorMessage('')} />

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label fw-semibold">Full Name *</label>
                  <input
                    type="text"
                    name="name"
                    className="form-control"
                    placeholder="e.g. Jane Doe"
                    value={formData.name}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label fw-semibold">College / University Email *</label>
                  <input
                    type="email"
                    name="email"
                    className="form-control"
                    placeholder="jane@university.edu"
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

                <div className="mb-3">
                  <label className="form-label fw-semibold">College / University Name *</label>
                  <input
                    type="text"
                    name="college"
                    className="form-control"
                    placeholder="e.g. National Institute of Technology"
                    value={formData.college}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="row">
                  <div className="col-md-6 mb-4">
                    <label className="form-label fw-semibold">Department *</label>
                    <select
                      name="department"
                      className="form-select"
                      value={formData.department}
                      onChange={handleChange}
                      required
                    >
                      {departments.map((dept) => (
                        <option key={dept} value={dept}>
                          {dept}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="col-md-6 mb-4">
                    <label className="form-label fw-semibold">Cumulative CGPA (0-10) *</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="10"
                      name="cgpa"
                      className="form-control"
                      placeholder="e.g. 8.50"
                      value={formData.cgpa}
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
                      Registering...
                    </>
                  ) : (
                    'Complete Student Registration'
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

export default RegisterStudent;
