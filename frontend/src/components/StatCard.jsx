import React from 'react';
import { Link } from 'react-router-dom';

const StatCard = ({ title, value, icon, color = 'primary', linkTo, linkText = 'View all' }) => {
  return (
    <div className="card shadow-sm border-0 h-100">
      <div className="card-body">
        <div className="d-flex align-items-center justify-content-between mb-3">
          <span className="text-muted fw-semibold text-uppercase small">{title}</span>
          <div className={`p-2 rounded bg-${color} bg-opacity-10 text-${color}`}>
            <i className={`bi bi-${icon} fs-4`}></i>
          </div>
        </div>
        <div className="display-6 fw-bold text-dark mb-2">{value}</div>
        {linkTo && (
          <Link to={linkTo} className={`text-${color} text-decoration-none small fw-semibold`}>
            {linkText} <i className="bi bi-arrow-right"></i>
          </Link>
        )}
      </div>
    </div>
  );
};

export default StatCard;
