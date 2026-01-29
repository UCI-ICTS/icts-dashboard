
```shell
Postgres
├── ictsdashboard_db   ← existing dashboard data
│   ├── metadata_*
│   ├── experiments_*
│   └── auth, users, etc
│
└── hpo_db             ← NEW
    ├── hpo_hpoterm
    ├── hpo_hpoedge
    └── hpo_hpoartifact
```