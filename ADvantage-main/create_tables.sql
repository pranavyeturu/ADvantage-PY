-- Create custom user table
CREATE TABLE user_auth_customuser (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    email VARCHAR(255) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ad generation history
CREATE TABLE ad_generation_history (
    ad_id SERIAL PRIMARY KEY,
    user_id INT,
    product_name TEXT,
    product_description TEXT,
    trend TEXT,
    ad_content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Google Trends data
CREATE TABLE google_trends_now (
    id SERIAL PRIMARY KEY,
    topic VARCHAR(255) NOT NULL,
    summary TEXT,
    scraped_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subscription plans or payments
CREATE TABLE subscriptions (
    subscription_id SERIAL PRIMARY KEY,
    user_id INT,
    plan_name VARCHAR(100),
    start_date DATE,
    end_date DATE,
    status VARCHAR(50)
);

-- Transaction history
CREATE TABLE transaction_history (
    transaction_id SERIAL PRIMARY KEY,
    user_id INT,
    amount DECIMAL(10, 2),
    transaction_type VARCHAR(50),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
