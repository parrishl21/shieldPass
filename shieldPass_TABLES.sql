CREATE TABLE users (
    UID SERIAL PRIMARY KEY,
	email varchar(256) NOT NULL,
	password varchar(256) NOT NULL,
    created_at TIMESTAMP DEFAULT current_timestamp
);

CREATE TABLE login (
	LID SERIAL PRIMARY KEY,
	UID SERIAL,
	CONSTRAINT fk_user_logins FOREIGN KEY (UID) REFERENCES users(UID),
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
	CONSTRAINT fk_user_notes FOREIGN KEY (UID) REFERENCES users(UID),
	note_name varchar(256) NOT NULL,
	note varchar(256) NOT NULL,
	updated_at TIMESTAMP DEFAULT current_timestamp NOT NULL
);

SELECT * FROM users;
SELECT * FROM login;
SELECT * FROM notes;

DROP TABLE users;
DROP TABLE login;
DROP TABLE notes;

CREATE OR REPLACE FUNCTION set_company() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.company IS NULL THEN
        NEW.company := regexp_replace(NEW.website, '^(https?://)?(www\.)?([^.]*)\.com.*$', '\3', 'g');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_company_trigger
BEFORE INSERT OR UPDATE ON login
FOR EACH ROW
EXECUTE FUNCTION set_company();