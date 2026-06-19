CREATE TABLE reviews(
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) on delete cascade,
  business_id UUID REFERENCES businesses(id) on delete cascade,
  description TEXT NOT NULL
)
