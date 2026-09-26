import React from 'react';

const statusConfig = {
  // Application Statuses
  APPLIED: { bg: 'secondary', label: 'Applied' },
  SHORTLISTED: { bg: 'info', text: 'dark', label: 'Shortlisted' },
  INTERVIEW_SCHEDULED: { bg: 'primary', label: 'Interview Scheduled' },
  SELECTED: { bg: 'success', label: 'Selected' },
  OFFERED: { bg: 'warning', text: 'dark', label: 'Offered' },
  REJECTED: { bg: 'danger', label: 'Rejected' },

  // Interview Statuses
  SCHEDULED: { bg: 'primary', label: 'Scheduled' },
  CLEARED: { bg: 'success', label: 'Cleared / Passed' },
  FAILED: { bg: 'danger', label: 'Failed' },
  CANCELLED: { bg: 'dark', label: 'Cancelled' },

  // Offer Statuses
  PENDING: { bg: 'warning', text: 'dark', label: 'Pending Response' },
  ACCEPTED: { bg: 'success', label: 'Accepted' },
};

const StatusBadge = ({ status }) => {
  const config = statusConfig[status] || { bg: 'secondary', label: status || 'Unknown' };
  const textClass = config.text ? `text-${config.text}` : '';

  return (
    <span className={`badge bg-${config.bg} ${textClass} px-2 py-1`}>
      {config.label}
    </span>
  );
};

export default StatusBadge;
