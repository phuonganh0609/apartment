# Kiến trúc và dữ liệu

```mermaid
flowchart LR
    U[Quản lý / Nhân viên / Kế toán] --> F[Django Templates + Bootstrap]
    F --> B[Django Views + Forms + Phân quyền]
    B --> S[Services nghiệp vụ]
    S --> D[(SQLite / PostgreSQL)]
    B --> A[AI services]
    A --> R[Truy xuất quy định đang áp dụng]
    R --> D
    A --> P[Prompt + JSON validation]
    P --> M[Google Gemini API]
    M --> P
    P --> F
```

```mermaid
erDiagram
    Building ||--o{ Apartment : contains
    Apartment ||--o{ ApartmentAmenity : has
    Amenity ||--o{ ApartmentAmenity : linked
    Tenant ||--o{ Contact : contacts
    Tenant ||--o{ Contract : rents
    Apartment ||--o{ Contract : history
    Contract ||--o{ Payment : bills
    Apartment ||--o{ MaintenanceRequest : maintenance
    Regulation ||--o{ RegulationDocument : documents
    User {
        bigint id PK
        string username UK
        string role
        boolean can_edit_deposit
    }
    Contract {
        bigint id PK
        string code UK
        bigint apartment_id FK
        bigint tenant_id FK
        date start_date
        date end_date
        decimal deposit_amount
        text contract_content
    }
    Payment {
        bigint id PK
        bigint contract_id FK
        decimal amount
        date due_date
        date paid_date
        string status
    }
```

User không có quan hệ sở hữu bản ghi vì phạm vi đề tài là một đơn vị quản lý và phân quyền theo vai trò. Hệ thống này không phải nền tảng nhiều chủ nhà với dữ liệu cách ly theo tenant.
