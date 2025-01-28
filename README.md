# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/gueriboutmathieu/python_utils/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                     |    Stmts |     Miss |   Cover |   Missing |
|--------------------------------------------------------- | -------: | -------: | ------: | --------: |
| python\_utils/\_\_init\_\_.py                            |        0 |        0 |    100% |           |
| python\_utils/auth.py                                    |       67 |        0 |    100% |           |
| python\_utils/domain.py                                  |       52 |        4 |     92% |   101-114 |
| python\_utils/entity.py                                  |        3 |        0 |    100% |           |
| python\_utils/env\_vars.py                               |       23 |        0 |    100% |           |
| python\_utils/fastapi\_generic\_routes.py                |       15 |        0 |    100% |           |
| python\_utils/fastapi\_middleware.py                     |       52 |        4 |     92% |34, 92, 97-98 |
| python\_utils/json.py                                    |        3 |        3 |      0% |      1-13 |
| python\_utils/loggers.py                                 |       39 |        0 |    100% |           |
| python\_utils/paths.py                                   |       13 |        1 |     92% |        16 |
| python\_utils/sqlalchemy\_crud\_repository.py            |       62 |       12 |     81% |48-59, 104-115, 121-132 |
| python\_utils/sqlalchemy\_postgresql\_engine\_wrapper.py |        9 |        0 |    100% |           |
| python\_utils/testing/\_\_init\_\_.py                    |        0 |        0 |    100% |           |
| python\_utils/testing/database.py                        |       37 |        3 |     92% |     40-42 |
| python\_utils/testing/directory.py                       |       11 |        0 |    100% |           |
| python\_utils/testing/docker.py                          |       27 |        6 |     78% |18-20, 32-34 |
| python\_utils/testing/server.py                          |       41 |        4 |     90% | 52-54, 65 |
|                                                **TOTAL** |  **454** |   **37** | **92%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/gueriboutmathieu/python_utils/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/gueriboutmathieu/python_utils/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/gueriboutmathieu/python_utils/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/gueriboutmathieu/python_utils/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fgueriboutmathieu%2Fpython_utils%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/gueriboutmathieu/python_utils/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.