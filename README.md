# Budget

Application for easily entering expenses in categories, purely intended for the
personal use of my wife and myself.

## Installation & Running Locally

Install project dependencies for the API:

- `pipenv sync --dev`

Use the built-in task runner to excute commands:

- `./x.py lint` (lints project with pycodestyle)
- `./x.py format` (formats project with autopep8)
- `./x.py test` (tests project with pytest)

## Design

Mocks for the application can be found on my personal Figma,
[here](https://www.figma.com/file/pWr2duGU1xBJDSKWY4jRFp/Feature-Mocks?node-id=5%3A19)

## TODO - API

- /accounts/login
- /accounts/me

- POST /transactions/

```
{
    category: "grocery",
    amount: 1000000,
    title: "some title",
    notes: "some notes"
}
```

- GET /months/current

```
{
    totals: {
        income: 1000000,
        remaining: 10000,
    },
    transactions: {
        grocery: [
            {
                /* transaction data */
            }
        ],
        giving: [
            {
                /* transaction data */
            }
        ]

    }
}
```

On start up - check date, and roll over month if required. Should probably
check/track how much is left over at the end of the month before rolling over.

## License

MIT

## Authors

- Michael Helvey <michael.helvey1@gmail.com>
