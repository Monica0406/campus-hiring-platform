import React, { useEffect, useState } from 'react';
import apiClient, { getErrorMessage } from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import LoadingSpinner from '../../components/LoadingSpinner';
import AlertMessage from '../../components/AlertMessage';

const StudentProfile = () => {
  const { updateUserProfile } = useAuth();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    college: '',
    department: 'CSE',
    cgpa: '',
    resume: null,
  });

  const [currentResume, setCurrentResume] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const departments = ['CSE', 'IT', 'ECE', 'EEE', 'MECH', 'CIVIL', 'AI&DS', 'OTHER'];

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const res = await apiClient.get('/students/profile/');
      if (res.data?.success) {
        const data = res.data.data;
        setFormData({
          name: data.name || '',
          email: data.email || '',
          college: data.college || '',
          department: data.department || 'CSE',
          cgpa: data.cgpa || '',
          resume: null,
        });
        setCurrentResume(data.resume);
      }
    } catch (err) {
      setErrorMsg(getErrorMessage(err, 'Failed to load profile.'));
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFormData({ ...formData, resume: e.target.files[0] });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSuccessMsg('');
    setErrorMsg('');

    const parsedCgpa = parseFloat(formData.cgpa);
    if (isNaN(parsedCgpa) || parsedCgpa < 0 || parsedCgpa > 10) {
      setErrorMsg('Please enter a valid CGPA between 0.00 and 10.00.');
      return;
    }

    setSaving(true);
    try {
      // Build form data to support optional resume file upload
      const updatePayload = new FormData();
      updatePayload.append('name', formData.name.trim());
      updatePayload.append('college', formData.college.trim());
      updatePayload.append('department', formData.department);
      updatePayload.append('cgpa', parsedCgpa.toFixed(2));

      if (formData.resume) {
        updatePayload.append('resume', formData.resume);
      }

      const res = await apiClient.patch('/students/profile/', updatePayload, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (res.data?.success) {
        setSuccessMsg('Profile updated successfully!');
        updateUserProfile(res.data.data);
        if (res.data.data.resume) {
          setCurrentResume(res.data.data.resume);
        }
      }
    } catch (err) {
      setErrorMsg(getErrorMessage(err, 'Failed to update profile.'));
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="container py-5">
        <LoadingSpinner message="Loading your profile..." />
      </div>
    );
  }

  return (
    <div className="container py-4">
      <div className="row justify-content-center">
        <div className="col-lg-8">
          <div className="card shadow-sm border-0 rounded-3">
            <div className="card-header bg-white py-3 border-bottom">
              <h4 className="fw-bold mb-0">
                <i className="bi bi-person-circle me-2 text-primary"></i>
                Student Profile
              </h4>
            </div>

            <div className="card-body p-4 p-md-5">
              <AlertMessage type="success" message={successMsg} onClose={() => setSuccessMsg('')} />
              <AlertMessage type="danger" message={errorMsg} onClose={() => setErrorMsg('')} />

              <form onSubmit={handleSubmit}>
                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label className="form-label fw-semibold">Full Name *</label>
                    <input
                      type="text"
                      name="name"
                      className="form-control"
                      value={formData.name}
                      onChange={handleChange}
                      required
                    />
                  </div>

                  <div className="col-md-6 mb-3">
                    <label className="form-label fw-semibold">Email Address</label>
                    <input
                      type="email"
                      className="form-control bg-light"
                      value={formData.email}
                      disabled
                      readOnly
                    />
                    <div className="form-text small">Email cannot be changed after registration.</div>
                  </div>
                </div>

                <div className="mb-3">
                  <label className="form-label fw-semibold">College / University *</label>
                  <input
                    type="text"
                    name="college"
                    className="form-control"
                    value={formData.college}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label className="form-label fw-semibold">Academic Department *</label>
                    <select
                      name="department"
                      className="form-select"
                      value={formData.department}
                      onChange={handleChange}
                      required
                    >
                      {departments.map((d) => (
                        <option key={d} value={d}>
                          {d}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="col-md-6 mb-3">
                    <label className="form-label fw-semibold">Cumulative CGPA (0 - 10) *</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="10"
                      name="cgpa"
                      className="form-control"
                      value={formData.cgpa}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>

                {/* Resume Upload */}
                <div className="mb-4">
                  <label className="form-label fw-semibold">Resume / CV Document (PDF / Doc)</label>
                  <input
                    type="file"
                    className="form-control"
                    accept=".pdf,.doc,.docx"
                    onChange={handleFileChange}
                  />
                  {currentResume && (
                    <div className="mt-2 small text-muted d-flex align-items-center">
                      <i className="bi bi-file-earmark-check text-success me-2 fs-5"></i>
                      <span>Current uploaded resume: </span>
                      <a
                        href={currentResume}
                        target="_blank"
                        rel="noreferrer"
                        className="ms-1 fw-semibold text-primary"
                      >
                        View Resume <i className="bi bi-box-arrow-up-right"></i>
                      </a>
                    </div>
                  )}
                </div>

                <div className="d-flex justify-content-end gap-2">
                  <button
                    type="submit"
                    className="btn btn-primary px-4 fw-semibold"
                    disabled={saving}
                  >
                    {saving ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Saving Changes...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-save me-2"></i> Save Profile
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

export default StudentProfile;
