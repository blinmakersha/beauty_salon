CREATE EXTENSION "uuid-ossp";

CREATE TABLE IF NOT EXISTS client (id uuid primary key default uuid_generate_v4(), name TEXT NOT NULL, surname TEXT NOT NULL, sex TEXT NOT NULL, date_of_birth	date not null, email TEXT, phone TEXT NOT NULL, user TEXT, money INT, created timestamp with time zone default CURRENT_TIMESTAMP, modified timestamp with time zone default CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS doctor (id uuid primary key default uuid_generate_v4(), name TEXT NOT NULL, surname TEXT NOT NULL, speciality TEXT NOT NULL, description TEXT, sex TEXT NOT NULL, date_of_birth	date, email text, phone TEXT NOT NULL, office TEXT NOT NULL, created timestamp with time zone default CURRENT_TIMESTAMP, modified timestamp with time zone default CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS service (id uuid primary key default uuid_generate_v4(), title TEXT NOT NULL, description TEXT, price decimal(10) not null, created timestamp with time zone default CURRENT_TIMESTAMP, modified timestamp with time zone default CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS personal_data (id uuid primary key default uuid_generate_v4(), client_id uuid references client, allergies text, medications_taken text, notes text, created timestamp with time zone default CURRENT_TIMESTAMP, modified timestamp with time zone default CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS appointment (id uuid primary key default uuid_generate_v4(), client_id uuid references client, doctor_id uuid references doctor, time_of_beginning timestamptz not null, time_of_ending timestamptz not null, status_payment text not null, date_of_payment timestamptz, created timestamp with time zone default CURRENT_TIMESTAMP, modified timestamp with time zone default CURRENT_TIMESTAMP)

CREATE TABLE IF NOT EXISTS service_to_appointment (id uuid primary key default uuid_generate_v4(), service_id uuid not null references service, appointment_id uuid not null references appointment, created timestamp with time zone default CURRENT_TIMESTAMP);
