CREATE TABLE businesses(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID REFERENCES users(id) on delete cascade,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT
)