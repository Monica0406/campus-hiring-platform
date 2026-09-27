# Architectural Diagrams & Design Specifications

This directory contains the formal architectural, data model, and API contract specifications for the **Campus & Internship Hiring Platform**, matching the actual implementation.

---

## Diagram Index

| Document | Format | Description |
| :--- | :--- | :--- |
| **[System Architecture](system_architecture.md)** | Mermaid (Graph) | Four-tier architecture depicting React frontend, Django REST API, Python service layer, and MySQL database, with placeholders for external services and hosting. |
| **[ER Diagram](er_diagram.md)** | Mermaid (ERD) | Relational database schema covering the six core domain entities (`Student`, `Company`, `Drive`, `Application`, `Interview`, `Offer`) and Django authentication. |
| **[Class & Module Diagram](class_module_diagram.md)** | Mermaid (Class) | Object-oriented module structure, showing relationships between Django models, service layer functions, and REST API views. |
| **[API Contract Diagram](api_contract_diagram.md)** | Mermaid (Sequence) | Sequential REST interaction flow spanning student/company authentication, drive publication, application evaluation, interview scheduling, and offer acceptance. |

---

## Diagram Standards

All diagrams are authored in GitHub Flavored Markdown using native **Mermaid** syntax. They render directly in GitHub, IDE Markdown previewers, and documentation tools without requiring proprietary binary editors.
