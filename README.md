Работает под unix подобными OS (macos, linux)

Чтобы запустить в первый раз:
``` bash
./compile.sh && ./run.sh
```

Последующие запуски:

``` bash
./run.sh
```

Схемы таблиц:
``` sql
CREATE TABLE departments (
	id INTEGER NOT NULL, 
	name VARCHAR(100), 
	description VARCHAR, 
	budget NUMERIC, 
	PRIMARY KEY (id)
);

CREATE TABLE professors (
	id INTEGER NOT NULL, 
	fio VARCHAR(60), 
	birth_date DATE, 
	social_rating INTEGER, 
	department_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(department_id) REFERENCES departments (id)
);
```