# DFD, SecDev Groups Activities

##  L0

```mermaid
flowchart LR
    %% Участники
    User[Пользователь в браузере]

    subgraph Internet [Trust Boundary: Untrusted Internet]
        User -- F1: Login Request --> GW
        GW -- F6: Set-Cookie Response --> User
        User -- F7: Authed Request to Protected API --> GW
    end

    subgraph Edge [Trust Boundary: Edge]
        GW[API Gateway]
    end

    subgraph Core [Trust Boundary: Core Backend]
        GASvc[Groups Activities Service]
    end

    subgraph Data [Trust Boundary: Data Store]
        DB[(Groups & Users, Auth DB <br/>PostgreSQL)]
    end

    %% Потоки данных
    GW -- F2: Forward Login --> GASvc
    GASvc -- F3: Verify Credentials --> DB
    GASvc -- F4: Create Session Record --> DB
    GASvc -- F5: Return SessionID --> GW
    GW -- F8: Forward Authed Request --> GASvc
    GASvc -- F9: Validate Session from DB --> DB
    GASvc -- F10: Data Response --> GW
    GW -- F11: Protected Data --> User

    %% Основная логика
    GASvc -- F12: Gore logic --> DB
```

## Легенда к потокам данных

| ID | Источник | Назначение | Ключевые атрибуты | Протокол |
| :--- | :--- | :--- | :--- | :--- |
| **F1** | Пользователь | API Gateway | `(email, password)` | HTTPS/JSON |
| **F2** | API Gateway | Groups Activities Service | `(email, password)` | HTTP |
| **F3** | Groups Activities Service | PostgreSQL DB | `(email, password)` | TCP/SQL |
| **F4** | Groups Activities Service | PostgreSQL DB | `session_id, user_id, expiration_date` | TCP/SQL |
| **F5** | Groups Activities Service | API Gateway | `session_id` | HTTP |
| **F6** | API Gateway | Пользователь | `session_id` | HTTPS |
| **F7** | Пользователь | API Gateway | `Cookie: (session_id)` | HTTPS |
| **F8** | API Gateway | Groups Activities Service | `Cookie: (session_id), request body` | HTTP |
| **F9** | Groups Activities Service | PostgreSQL DB | `session_id, ` | TCP/SQL |
| **F10**| Groups Activities Service | API Gateway | `user_data (email e.t.c )` | HTTP |
| **F11**| API Gateway | Пользователь | `user_data (email e.t.c)` | HTTPS |
| **F12**| Groups Activities Service | PostgreSQL DB | `user_id, group_id` | TCP/SQL |
