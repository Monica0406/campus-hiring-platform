import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import apiClient, { getErrorMessage } from '../../api/client';
import AlertMessage from '../../components/AlertMessage';

const CreateDrive = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    drive_date: '',
    min_cgpa: '0.00',
    allowed_departments: 'All',
    eligibility: '',
  });

  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    const parsedCgpa = parseFloat(formData.min_cgpa);
    if (isNaN(parsedCgpa) || parsedCgpa < 0 || parsedCgpa > 10) {
      setErrorMsg('Please enter a valid Minimum CGPA between 0.00 and 10.00.');
      return;
    }

    setSubmitting(true);
    try {
      const res = await apiClient.post('/drives/', {
        title: formData.title.trim(),
        description: formData.description.trim(),
        drive_date: formData.drive_date,
        min_cgpa: parsedCgpa.toFixed(2),
        allowed_departments: formData.allowed_departments.trim() || 'All',
        eligibility: formData.eligibility.trim(),
      });

      if (res.data?.success) {
        navigate('/company/drives');
      }
    } catch (err) {
      setErrorMsg(getErrorMessage(err, 'Failed to create placement drive.'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="container py-4">
      <nav aria-label="breadcrumb" className="mb-4">
        <ol className="breadcrumb">
          <li className="breadcrumb-item"><Link to="/company/drives">My Drives</Link></li>
          <li className="breadcrumb-item active" aria-current="page">Post New Drive</li>
        </ol>
      </nav>

      <div className="row justify-content-center">
        <div className="col-lg-8">
          <div className="card shadow-sm border-0 rounded-3">
            <div className="card-header bg-white py-3 border-bottom">
              <h4 className="fw-bold mb-0">
                <i className="bi bi-plus-circle me-2 text-primary"></i>
                Post a Placement Drive
              </h4>
            </div>

            <div className="card-body p-4 p-md-5">
              <AlertMessage type="danger" message={errorMsg} onClose={() => setErrorMsg('')} />

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label fw-semibold">Job / Role Title *</label>
                  <input
                    type="text"
                    name="title"
                    className="form-control"
                    placeholder="e.g. Software Engineer Intern, Data Analyst"
                    value={formData.title}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label fw-semibold">Role Description & Requirements *</label>
                  <textarea
                    name="description"
                    className="form-control"
                    rows={5}
                    placeholder="Describe role responsibilities, tech stack, key skills, and expectations..."
                    value={formData.description}
                    onChange={handleChange}
                    required
                  ></textarea>
                </div>

                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label className="form-label fw-semibold">Drive / Assessment Date *</label>
                    <input
                      type="date"
                      name="drive_date"
                      className="form-control"
                      value={formData.drive_date}
                      onChange={handleChange}
                      required
                    />
                  </div>

                  <div className="col-md-6 mb-3">
                    <label className="form-label fw-semibold">Minimum CGPA Requirement (0-10)</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="10"
                      name="min_cgpa"
                      className="form-control"
                      value={formData.min_cgpa}
                      onChange={handleChange}
                    />
                    <div className="form-text small">Set 0.00 for no CGPA restriction.</div>
                  </div>
                </div>

                <div className="mb-3">
                  <label className="form-label fw-semibold">Eligible Academic Departments</label>
                  <input
                    type="text"
                    name="allowed_departments"
                    className="form-control"
                    placeholder="e.g. CSE, IT, ECE or All"
                    value={formData.allowed_departments}
                    onChange={handleChange}
                  />
                  <div className="form-text small">Comma-separated departments or enter 'All' to allow any branch.</div>
                </div>

                <div className="mb-4">
                  <label className="form-label fw-semibold">Special Eligibility / Screening Notes (Optional)</label>
                  <input
                    type="text"
                    name="eligibility"
                    className="form-control"
                    placeholder="e.g. No active backlogs; minimum 75% in 12th standard"
                    value={formData.eligibility}
                    onChange={handleChange}
                  />
                </div>

                <div className="d-flex justify-content-end gap-2">
                  <Link to="/company/drives" className="btn btn-outline-secondary px-4">
                    Cancel
                  </Link>
                  <button
                    type="submit"
                    className="btn btn-primary px-4 fw-semibold"
                    disabled={submitting}
                  >
                    {submitting ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Publishing Drive...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-check-lg me-1"></i> Publish Drive
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateDrive;
