-- Drop tables if they exist (to allow re-creation)
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS motorcycles;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS market_data;

-- Table: users
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL
);

CREATE INDEX ix_users_id ON users(id);
CREATE UNIQUE INDEX ix_users_username ON users(username);

-- Table: motorcycles
CREATE TABLE motorcycles (
    id INTEGER PRIMARY KEY,
    brand VARCHAR(255),
    model_type VARCHAR(255),
    year INTEGER,
    price FLOAT,
    stock INTEGER,
    specifications JSON,
    market_position TEXT,
    competitor_prices JSON
);

CREATE INDEX ix_motorcycles_id ON motorcycles(id);

-- Table: customers
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(255),
    lifetime_value FLOAT,
    purchases INTEGER,
    satisfaction_score FLOAT
);




-- Removed incomplete INSERT statement


        id,
        first_name,
        last_name
        email,
        phone,
        lifetime_value,
        purchases,
        satisfaction_score
      )


CREATE INDEX ix_customers_id ON customers(id);


-- Table: sales
CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    date DATE,
    motorcycle_id INTEGER,
    customer_id INTEGER,
    sales_amount FLOAT,
    units_sold INTEGER,
    sales_channel VARCHAR(255),
    promotion_applied VARCHAR(255),
    sales_region VARCHAR(255),
    FOREIGN KEY (motorcycle_id) REFERENCES motorcycles(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE INDEX ix_sales_id ON sales(id);

-- Table: market_data
CREATE TABLE market_data (
    id INTEGER PRIMARY KEY,
    date DATE,
    market_share FLOAT,
    market_size FLOAT,
    economic_indicator1 FLOAT,
    economic_indicator2 FLOAT,
    seasonal_factors JSON,
    trend_indicators JSON
);

CREATE INDEX ix_market_data_id ON market_data(id);
