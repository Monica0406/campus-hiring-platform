import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient, { getErrorMessage } from '../../api/client';
import LoadingSpinner from '../../components/LoadingSpinner';
import AlertMessage from '../../components/AlertMessage';

const DriveList = () => {
  const [drives, setDrives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDept, setSelectedDept] = useState('ALL');

  useEffect(() => {
    fetchDrives();
  }, []);

  const fetchDrives = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await apiClient.get('/drives/');
      if (res.data?.success) {
        setDrives(res.data.data);
      }
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to load active drives.'));
    } finally {
      setLoading(false);
    }
  };

  const filteredDrives = drives.filter((drive) => {
    const matchesSearch =
      drive.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      drive.company_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      drive.description.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesDept =
      selectedDept === 'ALL' ||
      drive.allowed_departments.toUpperCase().includes('ALL') ||
      drive.allowed_departments.toUpperCase().includes(selectedDept);

    return matchesSearch && matchesDept;
  });

  return (
    <div className="container py-4">
      <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4 gap-3">
        <div>
          <h2 className="fw-bold mb-1">Active Placement Drives</h2>
          <p className="text-muted mb-0">Browse current opportunities and check your eligibility</p>
        </div>
      </div>

      <AlertMessage type="danger" message={error} onClose={() => setError('')} />

      {/* Filter and Search Bar */}
      <div className="card shadow-sm border-0 mb-4">
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-8">
              <div className="input-group">
                <span className="input-group-text bg-light"><i className="bi bi-search"></i></span>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Search by job title, company, or keywords..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>
            <div className="col-md-4">
              <select
                className="form-select"
                value={selectedDept}
                onChange={(e) => setSelectedDept(e.target.value)}
              >
                <option value="ALL">All Departments</option>
                <option value="CSE">CSE</option>
                <option value="IT">IT</option>
                <option value="ECE">ECE</option>
                <option value="EEE">EEE</option>
                <option value="MECH">MECH</option>
                <option value="CIVIL">CIVIL</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {loading ? (
        <LoadingSpinner message="Loading placement drives..." />
      ) : filteredDrives.length === 0 ? (
        <div className="card border-0 shadow-sm p-5 text-center">
          <div className="mb-3 text-muted">
            <i className="bi bi-inbox fs-1"></i>
          </div>
          <h5 className="fw-semibold">No Drives Found</h5>
          <p className="text-muted mb-0">
            {searchQuery || selectedDept !== 'ALL'
              ? 'No placement drives match your filter criteria. Try clearing your search.'
              : 'There are currently no active placement drives.'}
          </p>
        </div>
      ) : (
        <div className="row g-4">
          {filteredDrives.map((drive) => (
            <div key={drive.id} className="col-md-6 col-lg-4">
              <div className="card h-100 shadow-sm border-0 transition-all">
                <div className="card-body d-flex flex-column">
                  <div className="d-flex justify-content-between align-items-start mb-2">
                    <span className="badge bg-primary bg-opacity-10 text-primary border border-primary-subtle">
                      {drive.company_name}
                    </span>
                    <span className="badge bg-success">Active</span>
                  </div>

                  <h5 className="card-title fw-bold text-dark mt-1 mb-2">{drive.title}</h5>

                  <p className="card-text text-muted small flex-grow-1">
                    {drive.description?.length > 120
                      ? `${drive.description.substring(0, 120)}...`
                      : drive.description}
                  </p>

                  <div className="bg-light p-3 rounded-2 mb-3 small">
                    <div className="d-flex justify-content-between mb-1">
                      <span className="text-muted"><i className="bi bi-mortarboard me-1"></i> Min CGPA:</span>
                      <span className="fw-bold text-dark">{drive.min_cgpa}</span>
                    </div>
                    <div className="d-flex justify-content-between mb-1">
                      <span className="text-muted"><i className="bi bi-diagram-3 me-1"></i> Eligible Depts:</span>
                      <span className="fw-bold text-dark text-truncate ms-2" style={{ maxWidth: '140px' }}>
                        {drive.allowed_departments}
                      </span>
                    </div>
                    <div className="d-flex justify-content-between">
                      <span className="text-muted"><i className="bi bi-calendar-event me-1"></i> Drive Date:</span>
                      <span className="fw-bold text-dark">{drive.drive_date}</span>
                    </div>
                  </div>

                  <Link to={`/drives/${drive.id}`} className="btn btn-primary w-100 fw-semibold">
                    View Details & Apply
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DriveList;
