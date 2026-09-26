import React, { useEffect, useState } from 'react';
import apiClient, { getErrorMessage } from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import LoadingSpinner from '../../components/LoadingSpinner';
import AlertMessage from '../../components/AlertMessage';

const CompanyProfile = () => {
  const { updateUserProfile } = useAuth();

  const [formData, setFormData] = useState({
    company_name: '',
    email: '',
    location: '',
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const res = await apiClient.get('/companies/profile/');
      if (res.data?.success) {
        setFormData({
          company_name: res.data.data.company_name || '',
          email: res.data.data.email || '',
          location: res.data.data.location || '',
        });
      }
    } catch (err) {
      setErrorMsg(getErrorMessage(err, 'Failed to load company profile.'));
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSuccessMsg('');
    setErrorMsg('');

    setSaving(true);
    try {
      const res = await apiClient.patch('/companies/profile/', {
        company_name: formData.company_name.trim(),
        location: formData.location.trim(),
      });

      if (res.data?.success) {
        setSuccessMsg('Company profile updated successfully!');
        updateUserProfile(res.data.data);
      }
    } catch (err) {
      setErrorMsg(getErrorMessage(err, 'Failed to update company profile.'));
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="container py-5">
        <LoadingSpinner message="Loading company profile..." />
      </div>
    );
  }

  return (
    <div className="container py-4">
      <div className="row justify-content-center">
        <div className="col-lg-7">
          <div className="card shadow-sm border-0 rounded-3">
            <div className="card-header bg-white py-3 border-bottom">
              <h4 className="fw-bold mb-0">
                <i className="bi bi-building-gear me-2 text-primary"></i>
                Company Profile & Settings
              </h4>
            </div>

            <div className="card-body p-4 p-md-5">
              <AlertMessage type="success" message={successMsg} onClose={() => setSuccessMsg('')} />
              <AlertMessage type="danger" message={errorMsg} onClose={() => setErrorMsg('')} />

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label fw-semibold">Company / Organization Name *</label>
                  <input
                    type="text"
                    name="company_name"
                    className="form-control"
                    value={formData.company_name}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label fw-semibold">Official Email Address</label>
                  <input
                    type="email"
                    className="form-control bg-light"
                    value={formData.email}
                    disabled
                    readOnly
                  />
                  <div className="form-text small">Email cannot be modified after registration.</div>
                </div>

                <div className="mb-4">
                  <label className="form-label fw-semibold">Office / Headquarters Location *</label>
                  <input
                    type="text"
                    name="location"
                    className="form-control"
                    value={formData.location}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="d-flex justify-content-end">
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
                        <i className="bi bi-save me-2"></i> Update Profile
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

export default CompanyProfile;
