import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

// Public pages
import Home from "../pages/Home";
import Login from "../pages/auth/Login";
import RegisterStudent from "../pages/auth/RegisterStudent";
import RegisterCompany from "../pages/auth/RegisterCompany";
import DriveList from "../pages/drives/DriveList";
import DriveDetail from "../pages/drives/DriveDetail";
import NotFound from "../pages/NotFound";

// Student pages
import StudentDashboard from "../pages/student/StudentDashboard";
import StudentProfile from "../pages/student/StudentProfile";
import StudentApplications from "../pages/student/StudentApplications";
import StudentApplicationDetail from "../pages/student/StudentApplicationDetail";
import StudentInterviews from "../pages/student/StudentInterviews";
import StudentOffers from "../pages/student/StudentOffers";

// Company pages
import CompanyDashboard from "../pages/company/CompanyDashboard";
import CompanyProfile from "../pages/company/CompanyProfile";
import CompanyDrives from "../pages/company/CompanyDrives";
import CreateDrive from "../pages/company/CreateDrive";
import EditDrive from "../pages/company/EditDrive";
import DriveApplicants from "../pages/company/DriveApplicants";
import CompanyApplicationDetail from "../pages/company/CompanyApplicationDetail";
import CompanyInterviews from "../pages/company/CompanyInterviews";
import CompanyOffers from "../pages/company/CompanyOffers";

// Route protection
import ProtectedRoute from "../components/ProtectedRoute";

export default function AppRoutes() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register/student" element={<RegisterStudent />} />
      <Route path="/register/company" element={<RegisterCompany />} />
      <Route path="/drives" element={<DriveList />} />
      <Route path="/drives/:id" element={<DriveDetail />} />

      {/* Student Protected Routes */}
      <Route
        path="/student/dashboard"
        element={
          <ProtectedRoute allowedRoles={["student"]}>
            <StudentDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/profile"
        element={
          <ProtectedRoute allowedRoles={["student"]}>
            <StudentProfile />
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/applications"
        element={
          <ProtectedRoute allowedRoles={["student"]}>
            <StudentApplications />
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/applications/:id"
        element={
          <ProtectedRoute allowedRoles={["student"]}>
            <StudentApplicationDetail />
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/interviews"
        element={
          <ProtectedRoute allowedRoles={["student"]}>
            <StudentInterviews />
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/offers"
        element={
          <ProtectedRoute allowedRoles={["student"]}>
            <StudentOffers />
          </ProtectedRoute>
        }
      />

      {/* Company Protected Routes */}
      <Route
        path="/company/dashboard"
        element={
          <ProtectedRoute allowedRoles={["company"]}>
            <CompanyDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/company/profile"
        element={
          <ProtectedRoute allowedRoles={["company"]}>
            <CompanyProfile />
          </ProtectedRoute>
        }
      />
      <Route
        path="/company/drives"
        element={
          <ProtectedRoute allowedRoles={["company"]}>
            <CompanyDrives />
          </ProtectedRoute>
        }
      />
      <Route
        path="/company/drives/create"
        element={
          <ProtectedRoute allowedRoles={["company"]}>
            <CreateDrive />
          </ProtectedRoute>
        }
      />
      <Route
        path="/company/drives/:id/edit"
        element={
          <ProtectedRoute allowedRoles={["company"]}>
            <EditDrive />
          </ProtectedRoute>
        }
      />
      <Route
        path="/company/drives/:id/applicants"
        element={
          <ProtectedRoute allowedRoles={["company"]}>
            <DriveApplicants />
          </ProtectedRoute>
        }
      />
      <Route
        path="/company/applications/:id"
        element={
          <ProtectedRoute allowedRoles={["company"]}>
            <CompanyApplicationDetail />
          </ProtectedRoute>
        }
      />
      <Route
        path="/company/interviews"
        element={
          <ProtectedRoute allowedRoles={["company"]}>
            <CompanyInterviews />
          </ProtectedRoute>
        }
      />
      <Route
        path="/company/offers"
        element={
          <ProtectedRoute allowedRoles={["company"]}>
            <CompanyOffers />
          </ProtectedRoute>
        }
      />

      {/* 404 Catch-All */}
      <Route path="/404" element={<NotFound />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
}
