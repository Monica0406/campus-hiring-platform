import React from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { isAuthenticated, role, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getDisplayName = () => {
    if (!user) return '';
    if (role === 'STUDENT') {
      return user.profile?.name || user.email;
    }
    if (role === 'COMPANY') {
      return user.profile?.company_name || user.email;
    }
    return user.email;
  };

  const homeLink = !isAuthenticated
    ? '/'
    : role === 'STUDENT'
    ? '/student/dashboard'
    : '/company/dashboard';

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary sticky-top shadow-sm">
      <div className="container">
        <Link className="navbar-brand d-flex align-items-center fw-bold" to={homeLink}>
          <i className="bi bi-briefcase-fill me-2 fs-4"></i>
          <span>CampusHire</span>
        </Link>

        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarContent"
          aria-controls="navbarContent"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className="collapse navbar-collapse" id="navbarContent">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            {/* Common: Drives */}
            <li className="nav-item">
              <NavLink className="nav-link" to="/drives">
                <i className="bi bi-megaphone me-1"></i> Active Drives
              </NavLink>
            </li>

            {/* Student Navigation */}
            {isAuthenticated && role === 'STUDENT' && (
              <>
                <li className="nav-item">
                  <NavLink className="nav-link" to="/student/dashboard">
                    <i className="bi bi-speedometer2 me-1"></i> Dashboard
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link" to="/student/applications">
                    <i className="bi bi-file-earmark-text me-1"></i> My Applications
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link" to="/student/interviews">
                    <i className="bi bi-calendar-check me-1"></i> Interviews
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link" to="/student/offers">
                    <i className="bi bi-award me-1"></i> Offers
                  </NavLink>
                </li>
              </>
            )}

            {/* Company Navigation */}
            {isAuthenticated && role === 'COMPANY' && (
              <>
                <li className="nav-item">
                  <NavLink className="nav-link" to="/company/dashboard">
                    <i className="bi bi-speedometer2 me-1"></i> Dashboard
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link" to="/company/drives">
                    <i className="bi bi-building me-1"></i> My Drives
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link" to="/company/drives/create">
                    <i className="bi bi-plus-circle me-1"></i> Post Drive
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link" to="/company/interviews">
                    <i className="bi bi-calendar-event me-1"></i> Interviews
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link" to="/company/offers">
                    <i className="bi bi-envelope-paper me-1"></i> Offers
                  </NavLink>
                </li>
              </>
            )}
          </ul>

          <ul className="navbar-nav ms-auto mb-2 mb-lg-0 align-items-lg-center">
            {!isAuthenticated ? (
              <>
                <li className="nav-item">
                  <Link className="btn btn-outline-light btn-sm me-2 my-1" to="/login">
                    <i className="bi bi-box-arrow-in-right me-1"></i> Login
                  </Link>
                </li>
                <li className="nav-item dropdown">
                  <button
                    className="btn btn-warning btn-sm dropdown-toggle my-1"
                    type="button"
                    data-bs-toggle="dropdown"
                    aria-expanded="false"
                  >
                    <i className="bi bi-person-plus me-1"></i> Register
                  </button>
                  <ul className="dropdown-menu dropdown-menu-end shadow">
                    <li>
                      <Link className="dropdown-item" to="/register/student">
                        <i className="bi bi-mortarboard me-2"></i> As Student
                      </Link>
                    </li>
                    <li>
                      <Link className="dropdown-item" to="/register/company">
                        <i className="bi bi-building me-2"></i> As Company
                      </Link>
                    </li>
                  </ul>
                </li>
              </>
            ) : (
              <li className="nav-item dropdown">
                <button
                  className="btn btn-outline-light btn-sm dropdown-toggle d-flex align-items-center"
                  type="button"
                  data-bs-toggle="dropdown"
                  aria-expanded="false"
                >
                  <span className="badge bg-light text-primary me-2 text-uppercase">
                    {role}
                  </span>
                  <span className="text-truncate" style={{ maxWidth: '160px' }}>
                    {getDisplayName()}
                  </span>
                </button>
                <ul className="dropdown-menu dropdown-menu-end shadow">
                  <li>
                    <h6 className="dropdown-header">{user?.email}</h6>
                  </li>
                  <li>
                    <Link
                      className="dropdown-item"
                      to={role === 'STUDENT' ? '/student/profile' : '/company/profile'}
                    >
                      <i className="bi bi-person me-2"></i> Profile
                    </Link>
                  </li>
                  <li>
                    <hr className="dropdown-divider" />
                  </li>
                  <li>
                    <button className="dropdown-item text-danger" onClick={handleLogout}>
                      <i className="bi bi-box-arrow-right me-2"></i> Logout
                    </button>
                  </li>
                </ul>
              </li>
            )}
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
