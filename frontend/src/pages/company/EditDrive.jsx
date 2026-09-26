import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import api, { getErrorMessage } from "../../api/client";
import LoadingSpinner from "../../components/LoadingSpinner";
import AlertMessage from "../../components/AlertMessage";

export default function EditDrive() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    min_cgpa: "7.00",
    allowed_departments: "All",
    eligibility: "",
    drive_date: "",
    is_active: true,
  });

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    fetchDrive();
  }, [id]);

  const fetchDrive = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get(`/drives/${id}/`);
      const drive = res.data?.data || res.data;

      // format date value (YYYY-MM-DD)
      let formattedDate = "";
      if (drive.drive_date) {
        formattedDate = drive.drive_date.split("T")[0];
      }

      setFormData({
        title: drive.title || "",
        description: drive.description || "",
        min_cgpa: drive.min_cgpa !== undefined ? String(drive.min_cgpa) : "7.00",
        allowed_departments: drive.allowed_departments || "All",
        eligibility: drive.eligibility || "",
        drive_date: formattedDate,
        is_active: drive.is_active !== undefined ? drive.is_active : true,
      });
    } catch (err) {
      setError(getErrorMessage(err, "Failed to load drive details."));
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    const parsedCgpa = parseFloat(formData.min_cgpa);
    if (isNaN(parsedCgpa) || parsedCgpa < 0 || parsedCgpa > 10) {
      setError("Please enter a valid Minimum CGPA between 0.00 and 10.00.");
      return;
    }

    setSubmitting(true);

    try {
      const payload = {
        title: formData.title.trim(),
        description: formData.description.trim(),
        min_cgpa: parsedCgpa.toFixed(2),
        allowed_departments: formData.allowed_departments.trim() || "All",
        eligibility: formData.eligibility.trim(),
        drive_date: formData.drive_date,
        is_active: formData.is_active,
      };

      await api.patch(`/drives/${id}/`, payload);
      setSuccess("Drive updated successfully!");
      setTimeout(() => {
        navigate("/company/drives");
      }, 1200);
    } catch (err) {
      setError(getErrorMessage(err, "Failed to update drive. Check all required fields."));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading drive data..." />;

  return (
    <div className="container py-4">
      <div className="row justify-content-center">
        <div className="col-lg-8">
          <nav aria-label="breadcrumb" className="mb-3">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/company/drives">My Drives</Link></li>
              <li className="breadcrumb-item active">Edit Drive #{id}</li>
            </ol>
          </nav>

          <div className="card shadow-sm border-0">
            <div className="card-header bg-white py-3 border-bottom d-flex justify-content-between align-items-center">
              <h4 className="card-title mb-0 fw-bold">Edit Placement Drive</h4>
              <Link to="/company/drives" className="btn btn-sm btn-outline-secondary">
                Back to Drives
              </Link>
            </div>
            <div className="card-body p-4">
              <AlertMessage type="danger" message={error} onClose={() => setError(null)} />
              <AlertMessage type="success" message={success} onClose={() => setSuccess(null)} />

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label fw-semibold">Drive Title / Role Name *</label>
                  <input
                    type="text"
                    name="title"
                    className="form-control"
                    placeholder="e.g. Software Engineer Graduate 2026"
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
                    rows="4"
                    placeholder="Describe role responsibilities, tech stack, hiring process..."
                    value={formData.description}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="row g-3 mb-3">
                  <div className="col-md-6">
                    <label className="form-label fw-semibold">Minimum CGPA (0-10) *</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="10"
                      name="min_cgpa"
                      className="form-control"
                      value={formData.min_cgpa}
                      onChange={handleChange}
                      required
                    />
                    <div className="form-text">e.g. 7.50</div>
                  </div>

                  <div className="col-md-6">
                    <label className="form-label fw-semibold">Allowed Departments *</label>
                    <input
                      type="text"
                      name="allowed_departments"
                      className="form-control"
                      placeholder="e.g. CSE, IT, ECE (or 'All')"
                      value={formData.allowed_departments}
                      onChange={handleChange}
                      required
                    />
                    <div className="form-text">Students must belong to an allowed branch to apply.</div>
                  </div>
                </div>

                <div className="mb-3">
                  <label className="form-label fw-semibold">Eligibility Notes</label>
                  <input
                    type="text"
                    name="eligibility"
                    className="form-control"
                    placeholder="e.g. No active backlogs; graduating 2026"
                    value={formData.eligibility}
                    onChange={handleChange}
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label fw-semibold">Drive Date / Deadline *</label>
                  <input
                    type="date"
                    name="drive_date"
                    className="form-control"
                    value={formData.drive_date}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="form-check mb-4">
                  <input
                    type="checkbox"
                    id="is_active"
                    name="is_active"
                    className="form-check-input"
                    checked={formData.is_active}
                    onChange={handleChange}
                  />
                  <label className="form-check-label fw-semibold" htmlFor="is_active">
                    Drive is Active (visible to students and accepting applications)
                  </label>
                </div>

                <div className="d-flex justify-content-end gap-2">
                  <Link to="/company/drives" className="btn btn-outline-secondary">
                    Cancel
                  </Link>
                  <button type="submit" className="btn btn-primary px-4" disabled={submitting}>
                    {submitting ? "Saving Changes..." : "Update Drive"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
