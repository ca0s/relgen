# relgen
Relational data generator

This tool was written to test database performance.

It parses a data schema containing table structure, relations and constraints and generates random data which satisfies those given conditions.

## Usage:
```
$ python2 reldata.py [-h] -f data_definition.rel [-sgbd {mysql|postgresql} -sdb sql_database [-shost sql_host [-sport sql_port]] [-suser sql_user [-spass sql_pass]] [-sdel]]
  -h      Show this help
  -f      File to load data definition from
  -sgbd   Insert data in a database of given type. MySQL and PostgreSQL are supported (optional)
  -sdb    Database to use
  -shost  Host of the SQL server (optional)
  -sport  Port of the SQL server (optional)
  -suser  SQL user to use (optional)
  -spass  SQL password to use (optional)
  -sdel   Delete all rows from table before insertion (optional)
  -snri   Disable referetial integrity before insertion (optional)
  -sni    Do not execute any INSERT query (optional)
```

## Configuration format
Config files have .rel extension. Some examples are provided in this repository.

Config's format is a JSON list of objects, where each object represents a table. For example:
```
[
  {
    "name": "table_a",
    "fields": [],
    "n": 100
  },
  {
    "name": "table_b",
    "fields": [],
    "n": 200
  }
]
```
Where "name" is the table's name in the DBMS, n is the number of rows the tool will generate and fields is a list of objects.

A field is defined like this:
```
{
  "name": "field_1",    # field's name in the table
  "gentype": GEN_TYPE,  # see below
  "references": [       # foreign references (the value inserted in this table's field must exist in all the
    "table_x.field_1",  # referenced table's fields) (optional, defaults to [])
    "table_y.field_3"
  ],
  "unique": True/False  # if true, this field cannot have repeated values in the whole table (optional, defaults to False)
  "filter": "filt_name",# pass generated values through named boolean filter until it returns true (optional, defaults to none)
  "prefix": "p-",       # string to prefix random data with (optional, defaults to "")
  "suffix": "-s",       # string to suffix random data with (optional, defaults to "")
  "charset": "abcd",    # charset to use with random string generator (optional, defaults to lowercase alphanumeric)
  "genlen": 8,          # length of the generated data (optional, applies to string, defaults to 10)
  "genbegin": "",       # start value for the random generator (optional, applies to int and date)
  "genend": "",         # end value for the random generator (optional, applies to int and date)
  "values": [1, 2, 3],  # list of values to choose from if using the choose generator (mandatory if using said generator)
}
```

Generators:
- **inc_int**         incrementally generates integers starting from 0 or genbegin
- **rand_int**        generates random integets ranging from genbegin (defaults to 0) to genend (defaults to 9001)
- **randstr**         generates random strings
- **randdate**        generates random dates
- **inc_date**        incrementally generates dates from genbegin
- **randtime**        generates random timestamps
- **inc_time**        incrementally generates timestamps from genbegin
- **randchoose**      returns a random value from those given in the "values" parameter

## Bugs
- The tool will not detect the case when the configured restrictions will make the generator generate fewer results than those needed. This will make the tool hang.
- Documentation was written some years after the tool was written, and thus is incomplete and maybe wrong.
- More, probably.
