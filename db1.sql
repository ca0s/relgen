CREATE TABLE tabla1 (
	campo1 INT UNIQUE,
	campo2 TEXT,
	campo3 INT,

	PRIMARY KEY(campo1)
);

CREATE TABLE tabla2 (
	campo1 INT,
	campo2 TEXT,
	campo3 TEXT,

	PRIMARY KEY(campo1, campo2, campo3),
	FOREIGN KEY(campo1) REFERENCES tabla1(campo1)
		ON UPDATE CASCADE
		ON DELETE CASCADE
);

CREATE TABLE tabla3 (
	campo1 INT,
	campo2 TEXT,
	campo3 TEXT,

	FOREIGN KEY (campo1, campo2, campo3) REFERENCES tabla2(campo1, campo2, campo3)
		ON UPDATE CASCADE
		ON DELETE CASCADE
);
