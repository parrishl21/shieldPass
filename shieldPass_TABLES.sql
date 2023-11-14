CREATE TABLE users (
    UID SERIAL PRIMARY KEY,
	email varchar(256) NOT NULL,
	password varchar(256) NOT NULL,
    created_at TIMESTAMP DEFAULT current_timestamp
);

CREATE TABLE login (
	LID SERIAL PRIMARY KEY,
	UID SERIAL,
	CONSTRAINT fk_user_logins FOREIGN KEY (UID) REFERENCES users(UID) ON DELETE CASCADE,
	website varchar(256) NOT NULL,
	company varchar(256),
	email varchar(256) NOT NULL,
	username varchar(256) NOT NULL,
	password varchar(256) NOT NULL,
	num_of_uses integer DEFAULT 0 NOT NULL,
	strength integer,
	updated_at TIMESTAMP DEFAULT current_timestamp NOT NULL
);

CREATE TABLE notes (
	NID SERIAL PRIMARY KEY,
	UID SERIAL,
	CONSTRAINT fk_user_notes FOREIGN KEY (UID) REFERENCES users(UID) ON DELETE CASCADE,
	note_name varchar(32) NOT NULL,
	note TEXT NOT NULL,
	updated_at TIMESTAMP DEFAULT current_timestamp NOT NULL
);

CREATE OR REPLACE FUNCTION set_company() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.company IS NULL OR (TG_OP = 'UPDATE' AND NEW.website <> OLD.website) THEN
        NEW.company := regexp_replace(NEW.website, '^(https?://)?(www\.)?([^.]*)\.com.*$', '\3', 'g');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_company_trigger
BEFORE INSERT OR UPDATE ON login
FOR EACH ROW
EXECUTE FUNCTION set_company();

CREATE OR REPLACE FUNCTION check_login_password_strength()
RETURNS TRIGGER AS $$
DECLARE
    uppercase_count INT;
    digit_count INT;
    symbol_count INT;
	strength_score INT;
BEGIN
    NEW.strength := 0; -- Initialize strength score
    
    -- Calculate counts
    SELECT COUNT(*) INTO uppercase_count FROM regexp_matches(NEW.password, '[A-Z]', 'g');
    SELECT COUNT(*) INTO digit_count FROM regexp_matches(NEW.password, '[0-9]', 'g');
    SELECT COUNT(*) INTO symbol_count FROM regexp_matches(NEW.password, '[^\w\s]', 'g');

    -- Calculate strength score
    strength_score := (uppercase_count * 2) + (digit_count * 2) + (symbol_count * 3);
	
	IF strength_score < 5 THEN
        NEW.strength := 0;
    ELSIF strength_score < 10 THEN
        NEW.strength := 1;
    ELSIF strength_score < 15 THEN
        NEW.strength := 2;
    ELSE
        NEW.strength := 3;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_login_password_strength_trigger
BEFORE INSERT OR UPDATE ON login
FOR EACH ROW
EXECUTE FUNCTION check_login_password_strength();
